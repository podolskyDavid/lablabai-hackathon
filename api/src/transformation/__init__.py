import re
from types import FunctionType
from typing import Dict

import openai
from pandas import DataFrame

from src.database import Task
from src.transformation import transformations, toolmaker
from src.transformation.prompts import *
import inspect


def get_signatures_and_full_docstrings(module) -> str:
    """Around 11k characters in total for the transformations module"""
    s = ""

    for name, func in inspect.getmembers(module):
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
            sig = inspect.signature(func)
            doc = inspect.getdoc(func)
            doc = re.sub('\n+', '\n', doc)  # Remove multiple newlines
            s += f'Function: {name}{sig}\nDocstring: {doc}\n\n'

    return s


def get_signatures_and_short_descriptions(module) -> str:
    s = ""

    for name, func in inspect.getmembers(module):
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
            sig = inspect.signature(func)
            doc = inspect.getdoc(func)
            doc = doc.split('\n')[0]  # Only the first line of the docstring
            s += f'Function: {name}{sig}\nDocstring: {doc}\n\n'

    return s


def get_signatures(module) -> str:
    s = ""

    for name, func in inspect.getmembers(module):
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
            sig = inspect.signature(func)
            s += f'{name}\n\n'

    return s


def get_import_statements(module) -> str:
    source_lines = inspect.getsourcelines(module)[0]
    import_statements = []

    for line in source_lines:
        if re.match(r'^\s*import|from', line):
            import_statements.append(line.rstrip())

        if re.search(r'\b(def|class)\b', line):
            break

    return '\n'.join(import_statements)


def get_function_code_and_docstring(function_name) -> str:
    try:
        function = getattr(transformations, function_name)
        if not isinstance(function, FunctionType):
            raise AttributeError
        function_src = inspect.getsource(function)
        return function_src
    except AttributeError:
        raise AttributeError(f"'{function_name}' is not a function in the 'transformations' module")




class TransformationOrchestrator:
    def __init__(self, task: Task):
        self.task = task
        """Use this to access the state, i.e. the previous steps and their results."""

    def _select_transformation(self, step: str, summary: str, columns: list) -> str:
        """
        Decides whether to use one of the predefined functions in transformations.py
        or to use toolmaker.make_tool to create a new function
        :return: the name of the function to use or "None" to create a new function with toolmaker
        """

        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system",
                 "content": SELECT_TRANSFORMATION_PROMPT +
                            get_signatures_and_short_descriptions(transformations)[:60] +
                            # get_signatures(transformations) +
                            "\n\nAVAILABLE COLUMNS:" + "\n".join(columns)
                 },
                {"role": "user",
                 "content": f"Select exactly one function to apply to the dataframe to achieve the following preprocessing step:"
                            f"\n\n{step}\n\n"
                            f"Info about the dataframe:"
                            f"\n\n{summary}\n"
                 },
            ]
        )
        return chat_completion.choices[0].message.content.split('(')[0]

    def _generate_transformation(self, step: str, summary: str) -> str:
        """
        Generates a transformation function from scratch using toolmaker.make_tool
        """
        tool, success = toolmaker.make_tool(step, summary)
        if success:
            return tool
        else:
            return "# Your function definition goes here"

    def generate_code(self, step: str, summary: str, columns) -> str:
        """
        Generate a code snippet that's ready to be executed.
        It should contain a function definition and a call to that function.
        """
        transformation = self._select_transformation(step, summary, columns)
        transformation_comment = "# Using the following transformation predefined in transformations.py: "
        if transformation == "None":
            function_definition = self._generate_transformation(step, summary)
            transformation_comment = "# Using the following function generated with toolmaker.py: "
        else:
            try:
                function_definition: str = get_function_code_and_docstring(transformation)
            except AttributeError:
                print(f'... Creating a function from scratch with toolmaker '
                      f'because the function {transformation} was selected '
                      f'but it does not exist in transformations.py (likely hallucinated) ...')
                function_definition = self._generate_transformation(step, summary)
                transformation_comment = "# Using the following function generated with toolmaker.py: "


        prompt: str = GENERATE_FUNCTION_CALL_PROMPT \
            .replace('{function_definition}', function_definition) \
            .replace('{step}', step) \
            .replace('{summary_string}', summary)

        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user",
                 "content": prompt
                 },
            ]
        )
        function_call = chat_completion.choices[0].message.content
        if '```python' in function_call:
            function_call = function_call.split('```python')[1].split('```')[0]
        else:
            print('!!! No function call was generated !!!')
            print('Generated:')
            print(function_call)
            print('!!! Consider changing the GENERATE_FUNCTION_CALL_PROMPT !!!')
            function_call = '# No function call code was generated'

        prompt: str = GENERATE_IMPORTS_PROMPT \
            .replace('{snippet}', function_definition + '\n' + function_call) \
            .replace('{imports}', get_import_statements(transformations))
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": prompt
                 },
            ]
        )
        imports = chat_completion.choices[0].message.content
        if '```python' in imports:
            imports = imports.split('```python')[1].split('```')[0]
        else:
            print('!!! No import statements were generated !!!')
            print('Generated:')
            print(imports)
            print('!!! Consider changing the GENERATE_FUNCTION_CALL_PROMPT !!!')
            imports = '# No code was generated to import the necessary libraries'

        return imports + \
            '\n' + transformation_comment + '\n' + \
            function_definition + \
            '\n# Call the function above\n' + \
            function_call


if __name__ == '__main__':
    print(get_signatures(transformations)[:500])

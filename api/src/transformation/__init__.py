import re
from types import FunctionType
from typing import Dict

import openai
from pandas import DataFrame

from api.src.database import Task
from api.src.transformation import transformations, toolmaker
from api.src.transformation.prompts import *
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


def summary_to_str(summary: Dict[str, str]) -> str:
    s = ""
    for key, value in summary.items():
        s += f"{key}:\n {value}\n\n"
    return s


class TransformationOrchestrator:
    def __init__(self, task: Task):
        self.task = task
        """Use this to access the state, i.e. the previous steps and their results."""

    def _select_transformation(self, step: str, summary: Dict[str, str]) -> str:
        """
        Decides whether to use one of the predefined functions in transformations.py
        or to use toolmaker.make_tool to create a new function
        :return: the name of the function to use or "None" to create a new function with toolmaker
        """

        # TODO: Experiment with prompts; consider calling get_signatures_and_short_descriptions() instead of get_signatures()
        # TODO: Check if the function exists in the transformations module and try to regenerate if it doesn't. See toolmaker for an example
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system",
                 "content": SELECT_TRANSFORMATION_PROMPT +
                            # get_signatures_and_short_descriptions(transformations)
                            get_signatures(transformations)
                 },
                {"role": "user",
                 "content": f"Select exactly one function to apply to the dataframe to achieve the following preprocessing step:"
                            f"\n\n{step}\n\n"
                            f"Info about the dataframe:"
                            f"\n\n{summary_to_str(summary)}\n"
                 },
            ]
        )
        # only return the function name, not the signature
        return chat_completion.choices[0].message.content.split('(')[0]

    def _generate_transformation(self, step: str, summary: Dict[str, str]) -> str:
        """
        Generates a transformation function from scratch using toolmaker.make_tool
        """
        tool, success = toolmaker.make_tool(step, summary_to_str(summary))
        if success:
            return tool
        else:
            # last resort: nudge the model to write a function
            return "# Your function definition goes here"

    def generate_code(self, step: str, summary: Dict[str, str]) -> str:
        """
        Generate a code snippet that's ready to be executed.
        It should contain a function definition and a call to that function.
        """
        transformation = self._select_transformation(step, summary)
        if transformation == "None":
            print('... Creating a function with toolmaker because no function was selected ...')
            function_definition = self._generate_transformation(step, summary)
        else:
            try:
                # Get full function code including docstring from transformations.py
                # The model will then generate import statements and a call to this function
                function_definition: str = get_function_code_and_docstring(transformation)
            except AttributeError:
                # TODO create a function from scratch with toolmaker
                print(f'... Creating a function from scratch with toolmaker '
                      f'because the function {transformation} was selected '
                      f'but it does not exist in transformations.py (likely hallucinated) ...')
                print('!!! Consider changing the SELECT_TRANSFORMATION_PROMPT !!!')
                function_definition = self._generate_transformation(step, summary)

        # Generate a function call and append it to the function definition
        prompt: str = GENERATE_FUNCTION_CALL_PROMPT \
            .replace('{function_definition}', function_definition) \
            .replace('{step}', step) \
            .replace('{summary_string}', summary_to_str(summary))

        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user",
                 "content": prompt
                 },
            ]
        )
        function_call = chat_completion.choices[0].message.content
        # TODO add some code correctness check like in toolmaker - maybe use some kind of linter?
        if '```python' in function_call:
            function_call = function_call.split('```python')[1].split('```')[0]
        else:
            print('!!! No function call was generated !!!')
            print('Generated:')
            print(function_call)
            print('!!! Consider changing the GENERATE_FUNCTION_CALL_PROMPT !!!')
            function_call = '# No function call code was generated'

        # Generate import statements and prepend them to the function definition
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
        # TODO add some code correctness check like in toolmaker - maybe use some kind of linter?
        if '```python' in imports:
            imports = imports.split('```python')[1].split('```')[0]
        else:
            print('!!! No import statements were generated !!!')
            print('Generated:')
            print(imports)
            print('!!! Consider changing the GENERATE_FUNCTION_CALL_PROMPT !!!')
            imports = '# No imports code was generated'

        return imports + \
            '\n# Transformation to be applied:\n' + \
            function_definition + \
            '\n# Call the function above\n' + \
            function_call


if __name__ == '__main__':
    print(get_signatures(transformations)[:500])

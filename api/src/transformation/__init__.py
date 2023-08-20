import re
from types import FunctionType
from typing import Dict

import openai
from pandas import DataFrame

from api.src.database import Task
from api.src.transformation import transformations
from api.src.transformation.prompts import *
import inspect


def get_signatures_and_full_docstrings(module):
    """Around 11k characters in total for the transformations module"""
    s = ""

    for name, func in inspect.getmembers(module):
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
            sig = inspect.signature(func)
            doc = inspect.getdoc(func)
            doc = re.sub('\n+', '\n', doc)  # Remove multiple newlines
            s += f'Function: {name}{sig}\nDocstring: {doc}\n\n'

    return s

def get_signatures_and_short_descriptions(module):
    """Around 11k characters in total for the transformations module"""
    s = ""

    for name, func in inspect.getmembers(module):
        if inspect.isfunction(func) and inspect.getmodule(func) == module:
            sig = inspect.signature(func)
            doc = inspect.getdoc(func)
            doc = doc.split('\n')[0]  # Only the first line of the docstring
            s += f'Function: {name}{sig}\nDocstring: {doc}\n\n'

    return s

def get_function_code_and_docstring(function_name):
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

        # TODO: Experiment with prompts; consider calling get_signatures_and_full_docstrings() instead
        # TODO: Check if the function exists in the transformations module and try to regenerate if it doesn't. See toolmaker for an example
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system",
                 "content": SELECT_TRANSFORMATION_PROMPT +
                            get_signatures_and_short_descriptions(transformations)
                 },
                {"role": "user",
                 "content": f"Select exactly one function to apply to the dataframe to achieve the following preprocessing step:"
                            f"\n\n{step}\n\n"
                            f"Info about the dataframe:"
                            f"\n\n{summary_to_str(summary)}\n"
                 },
            ]
        )
        return chat_completion.choices[0].message.content.split('(')[0]  # only return the function name, not the signature

    def generate_code(self, step: str, summary: Dict[str, str]) -> str:
        """
        Generate a code snippet that's ready to be executed.
        It should contain a function definition and a call to that function.
        """
        transformation = self._select_transformation(step, summary)
        if transformation == "None":
            # TODO create a function from scratch with toolmaker
            print('... Creating a function from with toolmaker because no function was selected ...')
            function_definition = 'Your function definition here'
        else:
            try:
                function_definition: str = get_function_code_and_docstring(transformation)
            except AttributeError:
                # TODO create a function from scratch with toolmaker
                print('... Creating a function from scratch with toolmaker '
                      'because a function was selected but it does not exist in transformations.py ...')
                print('!!! Consider changing the SELECT_TRANSFORMATION_PROMPT !!!')
                function_definition = 'Your function definition here'

        prompt: str = GENERATE_CODE_PROMPT\
            .replace('{function_definition}', function_definition)\
            .replace('{step}', step)\
            .replace('{summary_string}', summary_to_str(summary))

        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user",
                 "content": prompt
                 },
            ]
        )
        response = chat_completion.choices[0].message.content
        # TODO add some code correctness check like in toolmaker - maybe use some kind of linter?
        if '```python' in response:
            response = response.split('```python')[1].split('```')[0]
        return '# Apply this transformation: ' +\
            function_definition +\
            '\n# Call the function above\n' +\
            response


if __name__ == '__main__':
    print(get_function_code_and_docstring('drop_duplicates'))

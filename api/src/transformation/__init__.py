import re
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

class TransformationOrchestrator:
    def __init__(self, task: Task):
        self.task = task
        """Use this to access the state, i.e. the previous steps and their results."""

    def select_transformation(self, df: DataFrame, step: str, infos: Dict[str, str]) -> str:
        """
        Decides whether to use one of the predefined functions in transformations.py
        or to use toolmaker.tool_making to create a new function
        """
        infos_str = ""
        for key, value in infos.items():
            infos_str += f"{key}: {value}\n\n"

        # TODO: Experiment with prompts; consider calling get_signatures_and_full_docstrings() instead
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": TRANSFORMATION_ORCHESTRATOR_SYSTEM_PROMPT +
                            get_signatures_and_short_descriptions(transformations)
                 },
                {"role": "user",
                 "content": f"Select exactly one function to apply to the dataframe to achieve the following preprocessing step:"
                            f"\n\n{step}\n\n"
                            f"Info about the dataframe:"
                            f"\n\n{infos_str}\n"
                 },
            ]
        )
        return chat_completion.choices[0].message.content
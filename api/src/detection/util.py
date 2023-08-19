from typing import *

import pandas as pd
import io
import openai
import re
from pandas import DataFrame

from api.src.detection.prompts import DETECTOR_PROMPT

Steps = List[Dict[str, Union[int, str]]]
"""
Represents a number of steps in a particular order which an OpenAI model thinks are the best transformations. Sample Steps:
[
{'step': 1, 'description': "Convert column 'date' to datetime format."}, 
{'step': 2, 'description': "Remove leading/trailing whitespace from column 'country'."},
]
"""


def parse_to_json(s) -> Steps:
    # Use regex to extract step numbers and descriptions
    matches = re.findall(r'(\d+)\.\s(.*?)(?=\d+\.|$)', s, re.DOTALL)

    # Construct the list of dictionaries
    steps = [{"step": int(match[0]), "description": match[1].strip()} for match in matches]

    # Convert the list to a JSON string
    return steps


def _call_chatgpt(df: DataFrame, infos: Dict = {}):
    """Calls the chatgpt API to detect transformations."""
    query = ""
    for key, value in infos.items():
        query += f"{key}: {value}\n\n"
    query += "Transformations:"

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": DETECTOR_PROMPT
             },
            {"role": "user",
             "content": query}]
    )
    return chat_completion.choices[0].message.content


def get_steps_from_summary(df, summary: Dict = {}) -> Steps:
    transformation_str = _call_chatgpt(df, summary)
    steps = parse_to_json(transformation_str)

    return steps

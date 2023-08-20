from typing import *

import pandas as pd
import io
import openai
import re
from pandas import DataFrame
from tenacity import retry, stop_after_attempt, wait_fixed

from src.detection.prompts import DETECTOR_PROMPT

Steps = List[Dict[str, Union[int, str]]]


def parse_to_json(s) -> Steps:
    """
    Example output:
    [{'step': 1, 'description': "Convert column 'date' to datetime format."}]
    """
    matches = re.findall(r'Step (\d+): (.*?)(?=Step \d+:|$)', s, re.DOTALL)
    steps = [{"step": int(match[0]), "description": match[1].strip()} for match in matches]
    if not steps:
        raise ValueError("Steps not found")
    return steps


def _call_chatgpt(infos:str='', past_steps=[]):
    """Calls the chatgpt API to detect transformations."""
    query = infos + "\n\n"
    query += "Transformations:"

    chat_completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": DETECTOR_PROMPT
             },
             {"role": "system", "content": "AVOID DUPLICATING STEPS. Do not rename. Past steps:" + f"{', '.join([step['explanation'] for step in past_steps])}" if past_steps else "No past steps"},
            {"role": "user", "content": query}
        ],
    )
    return chat_completion.choices[0].message.content


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_steps_from_summary(summary: str='', past_steps=[]) -> Steps:
    transformation_str = _call_chatgpt(summary,past_steps)
    steps = parse_to_json(transformation_str)
    return steps

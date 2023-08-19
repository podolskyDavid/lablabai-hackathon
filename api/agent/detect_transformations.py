import pandas as pd
import io 
import openai
import re
from detection_modules import *

def parse_to_json(s):
    # Use regex to extract step numbers and descriptions
    matches = re.findall(r'(\d+)\.\s(.*?)(?=\d+\.|$)', s, re.DOTALL)

    # Construct the list of dictionaries
    steps = [{"step": int(match[0]), "description": match[1].strip()} for match in matches]

    # Convert the list to a JSON string
    return steps

def _call_chatgpt(df, infos:dict = {}):
    """Calls the chatgpt API to detect transformations."""
    query = ""
    for key, value in infos.items():
        query += f"{key}: {value}\n\n"
    query += "Transformations:"

    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", 
            "content": "You are a bot who is responsible to detect issues in a pandas dataframe. You are given the head of the dataframe (a few rows of data) and a description of each column. Suggest possible transformation to clean the dataframe and make it ready for analysis. Be really concrete, name the operation and the column you want to apply it on. Also consider the column types etc. We want to have a perfectly tidy dataframe at the end. Restrict the transformation to the provided columns."
            }, 
            {"role": "user", 
            "content": query}]
        )
    return chat_completion.choices[0].message.content

def detect_transformations(df, infos: dict = {}): 
    transformation_str = _call_chatgpt(df, infos)
    steps = parse_to_json(transformation_str)
    
    return steps
    
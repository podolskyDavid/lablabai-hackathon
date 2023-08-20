from typing import *

import pandas as pd
from sklearn.feature_selection import VarianceThreshold
import io
import os

from src.database import Task
import openai
import json
import dotenv
from src.detection.util import get_steps_from_summary, Steps

Steps = Steps

dotenv.load_dotenv()
dotenv.load_dotenv(dotenv.find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

class Detector:
    """Detects and creates a list of instructions using the OpenAI API to transform a DataFrame."""
    def __init__(self, task: Task):
        self.task = task
        self.openai_summary = None
        """Use this to access the state, i.e. the previous steps and their results."""
    
    def get_openai_summary(self, general_summary_dict, past_steps:list=None) -> str:
        messages = [
                {
                "role": "system", "content": "DATAFRAME sample and some stats:" +json.dumps(general_summary_dict)
                },
                {
                "role": "system", "content": "AVOID DUBLICATING STEPS"
                },
                {
                "role": "user", "content": """
        reason about what do you notice in the databaframe as the best kaggle competition master doing data cleaning
        make a summary about this data. brief compact structed way of this output.
        skip: 
        -skip ID
        -user name
        -memory
        be short and very precise.
        """}]
        if past_steps:
            # insert as first
            messages.insert(0, {"role": "system", "content": "ALREADY completed past steps and summarize them: "+', '.join([f'{step["explanation"]}' for step in past_steps])})
        print("Doing openai DF summary")
        response = openai.ChatCompletion.create(
                model='gpt-4',
                messages=messages,
                max_tokens=500,
                ).choices[0].message.content
        
        print("Summary\n", response)
        print("=====================================")
        self.openai_summary = response

    def get_initial_summary(self, df) -> str:
        summary = general_summary(df, n=5)
        if self.openai_summary is None:
            self.get_openai_summary(summary)
            buf = io.StringIO()
            df.info(buf=buf)
            info_str = buf.getvalue()
            self.openai_summary = self.openai_summary + "\n\nColumns:\n" + '\n'.join(list(df.columns)) + "\n\nINFO: " + info_str
        return self.openai_summary

    def get_steps_from_initial_df(self, df) -> Steps:
        """ Detects and creates a list of instructions for an initial DataFrame """
        summary = self.get_initial_summary(df)
        steps = get_steps_from_summary(summary)
        return steps

    def get_summary_from_former_steps(self) -> str:
        df = self.task.get_latest_df()  # only considers the latest df, i.e. latest state
        past_steps = self.task.retrieve_previous_steps()
        print("Past step: ", past_steps)
        summary_dict = general_summary(df, n=5)
        self.get_openai_summary(summary_dict, past_steps=past_steps)
        print("Updated Summary\n", self.openai_summary)
        return self.openai_summary, past_steps


    def get_steps_from_former_steps(self) -> Steps:
        """ Detects and creates a list of instructions for a DataFrame based on information from steps it's already taken """
        summary, past_steps = self.get_summary_from_former_steps()  # only considers the latest df, i.e. latest state
        steps = get_steps_from_summary(summary, past_steps)
        return steps


def general_summary(df, n=10):
    """
    Provides the first few rows of the DataFrame.

    Parameters:
    - df: DataFrame
    - n: Number of rows to return

    Returns:
    - Instructions what transformations to do in general based on a view of the data.
    """
    head = df.head(n)
    buf = io.StringIO()
    df.info(buf=buf)
    s = buf.getvalue()
    numerical = df.describe()
    num_rows = len(df)
    unique_values = df.nunique().to_string()
    try:
        value_counts = df.apply(lambda x: x.value_counts().index[0]).to_string()
    except IndexError:
        value_counts = df.apply(lambda x: x.value_counts()).to_string()

    summary = {
        "Description of the Numerical Columns": numerical.to_string(),
        "Head of the DataFrame": head.to_string(),
        "Column Infos": s,
        "Data Types": df.dtypes.to_string(),
        "Number of Rows": num_rows,
        "Unique Values": unique_values,
        "Value Counts": value_counts,
    }

    return summary


# def datatype_summary(df):
#     """
#     UNUSED
#     Provides the data types for each column.
#
#     Parameters:
#     - df: DataFrame
#
#     Returns:
#     - Instructions what transformations to do base don the data types.
#     """
#     overview = pd.DataFrame({
#         'Data Type': df.dtypes,
#         'Columns': df.columns,
#     })
#
#     steps = get_steps_from_summary(df, overview)
#
#     return steps


def unique_values_summary(df):
    """
    UNUSED
    Provides the number of unique values in each column of the dataset.

    Parameters:
    - df: DataFrame

    Returns:
    - Instructions what transformations to do to handle the unique values or lack of them.
    """
    overview = pd.DataFrame({
        'Column': df.columns,
        'Unique Values': df.nunique(),
        'Percentage': df.nunique() / len(df) * 100
    })

    summary = {
        "Unique Values": overview.to_string()
    }

    return summary


def detect_high_correlation(df, threshold=0.85):
    """
    UNUSED
    Detects highly correlated columns in a DataFrame.

    Args:
        df (DataFrame): DataFrame
        threshold (float, optional): Minimum correlation for highly-correlated features. Defaults to 0.85.

    Returns:
        _type_: _description_
    """
    corr_matrix = df.corr()
    correlated_features = set()

    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if abs(corr_matrix.iloc[i, j]) > threshold:
                colname = corr_matrix.columns[i]
                correlated_features.add(colname)

    summary = {
        "Highly Correlated Features": correlated_features,
        "Head": df.head().to_string(),
        "Correlation Matrix": corr_matrix.to_string()
    }

    return summary

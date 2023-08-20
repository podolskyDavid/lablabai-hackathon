from typing import *

import pandas as pd
from sklearn.feature_selection import VarianceThreshold
import io

from api.src.database import Task
from api.src.detection.util import get_steps_from_summary, Steps

Steps = Steps

class Detector:
    """Detects and creates a list of instructions using the OpenAI API to transform a DataFrame."""
    def __init__(self, task: Task):
        self.task = task
        """Use this to access the state, i.e. the previous steps and their results."""
        # TODO implement a method in task to easily retrieve all previous states

    def get_initial_summary(self, df) -> Dict[str, str]:
        # TODO experiment with this, possibly using another function from this file
        return general_summary(df)

    def get_steps_from_initial_df(self, df) -> Steps:
        """ Detects and creates a list of instructions for an initial DataFrame """
        summary = self.get_initial_summary(df)
        steps = get_steps_from_summary(summary)
        return steps

    def get_summary_from_former_steps(self) -> Dict[str, str]:
        # TODO experiment with this, possibly writing another function.
        # TODO possibly use a Task object with the provided task_id to retrieve former steps and the DataFrame.
        # TODO Prioritize experiments with this since it's directly responsible for improving the agent performance over multiple Steps.
        df = self.task.get_latest_df()  # only considers the latest df, i.e. latest state
        return general_summary(df)

    def get_steps_from_former_steps(self) -> Steps:
        """ Detects and creates a list of instructions for a DataFrame based on information from steps it's already taken """
        summary = self.get_summary_from_former_steps()  # only considers the latest df, i.e. latest state
        steps = get_steps_from_summary(summary)
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
    # TODO: use this function as input to make_tool(), possibly experiment with adding some more stats to the prompt
    head = df.head(n)
    buf = io.StringIO()
    df.info(buf=buf)
    s = buf.getvalue()
    numerical = df.describe()

    summary = {
        "Description of the Numerical Columns": numerical.to_string(),
        "Head of the DataFrame": head.to_string(),
        "Column Infos": s
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

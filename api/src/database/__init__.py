from src.database.task import Task
from pandas import DataFrame

def new_task(user_id: str, initial_df: DataFrame, initial_df_frontend: DataFrame | None = None):
    """ Create a new task for a new initial_df DataFrame or retrieve an existing task with task_id """
    return Task(user_id, None, initial_df, initial_df_frontend)


def get_task(user_id: str, task_id: int):
    """
    Retrieve an existing task with task_id.
    Call get_task(user_id, task_id)
    """
    return Task(user_id, task_id)

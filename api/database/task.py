from __init__ import table, bucket
from typing import *
from pandas import DataFrame


class Task:
    task_id: int
    user_id: str  # just the email for now
    max_step_count: int
    def __init__(self, user_id: str, task_id: int | None = None,
                 initial_df: DataFrame | None = None, initial_df_frontend: DataFrame | None = None):
        """ Create a new DataFrame cleaning task """
        self.user_id = user_id
        self.task_id = task_id

        if self.task_id is None:
            # create a new task
            task_ids: List = table.select('task_id').execute().data
            max_id = max([id['task_id'] for id in task_ids]) if not task_ids == [] else 0
            self.task_id = max_id + 1
            self.max_step_count = 0

            if initial_df is None:
                raise ValueError('initial_df must be provided when creating a new task, i.e. when task_id is None')
            if initial_df_frontend is None:
                initial_df_frontend = initial_df
            self.new_step('', 'Initial DataFrame', initial_df, initial_df_frontend)
        else:
            # find max step id within an existing task
            step_counts: List = table.select('task_id, step_count').eq('task_id', self.task_id).execute().data
            self.max_step_count = max([int(c['step_count']) for c in step_counts])

    def new_step(self, transformation: str, explanation: str, df_after: DataFrame, df_frontend: DataFrame):
        """ Create a new step in the task """
        assert isinstance(self.max_step_count, int)
        self.max_step_count += 1
        table.insert({
            'step_id': str(self.task_id) + '_' + str(self.max_step_count),
            'task_id': self.task_id,
            'step_count': self.max_step_count,
            'user_id': self.user_id,
            'transformation': transformation,
            'explanation': explanation,
        }).execute()


if __name__ == '__main__':
    # task = Task(user_id='test@example.com', initial_df=DataFrame({'a': [1, 2, 3]}))
    task = Task(user_id='nico@example.com', task_id=1)
    task.new_step('lambda x: x', 'test transformation - no change', None, None)
    print(task.task_id, task.user_id, task.max_step_count)

from __init__ import supabase, table, bucket
from typing import *
import os
import re
from pandas import DataFrame


class Task:
    task_id: int
    user_id: str  # just the email for now
    max_step_count: int
    def __init__(self, user_id: str, task_id: int | None = None,
                 initial_df: DataFrame | None = None, initial_df_frontend: DataFrame | None = None):
        """ Create a new task for a new initial_df DataFrame or retrieve an existing task with task_id """
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
            self.upload_new_step('', 'Initial DataFrame', initial_df, initial_df_frontend)
        else:
            # find max step id within an existing task
            step_counts: List = table.select('task_id, step_count').eq('task_id', self.task_id).execute().data
            self.max_step_count = max([int(c['step_count']) for c in step_counts])

    def upload_new_step(self, transformation: str, explanation: str, df_after: DataFrame, df_frontend: DataFrame):
        """ Upload a new step in the task to the DB """
        self.max_step_count += 1
        step_id = str(self.task_id) + '_' + str(self.max_step_count)

        # convert dataframes to csv
        os.makedirs('temp', exist_ok=True)
        df_after.to_csv('temp/df.csv', index=False)
        with open('temp/df.csv', 'rb') as f:
            filepath = f'{self.user_id}/df_after_{step_id}.csv'
            bucket.upload(filepath, f)
            df_after_url = bucket.get_public_url(filepath)
        df_frontend.to_csv('temp/df.csv', index=False)
        with open('temp/df.csv', 'rb') as f:
            filepath = f'{self.user_id}/df_frontend_{step_id}.csv'
            bucket.upload(filepath, f)
            df_frontend_url = bucket.get_public_url(filepath)
        os.remove('temp/df.csv')

        table.insert({
            'step_id': step_id,
            'task_id': self.task_id,
            'step_count': self.max_step_count,
            'user_id': self.user_id,
            'transformation': transformation,
            'explanation': explanation,
            'df_after': df_after_url,
            'df_frontend': df_frontend_url
        }).execute()


if __name__ == '__main__':
    my_df = DataFrame({'a': [1, 2, 3]})
    # task = Task(user_id='test@example.com', initial_df=my_df, initial_df_frontend=my_df)
    task = Task(user_id='nico@example.com', task_id=1)
    task.upload_new_step('lambda x: x', 'test transformation 1 - no change', my_df, my_df)
    task.upload_new_step('lambda x: x', 'test transformation 2 - no change', my_df, my_df)
    task.upload_new_step('lambda x: x', 'test transformation 3 - no change', my_df, my_df)
    # print(task.task_id, task.user_id, task.max_step_count)

    # with open('test_csv/test.csv', 'rb') as f:
    #     res = bucket.upload('test3.csv', f)
    #     print(res)
    #     print(bucket.get_public_url('test1.csv'))


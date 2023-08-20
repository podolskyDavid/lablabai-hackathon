import pandas as pd
import requests
from pandas import DataFrame

from api.src.database import Task
from api.src.detection import Detector, Steps
from api.src.transformation import *
from api.src.database import *
from api.src.transformation import toolmaker
import urllib

EXECUTOR_ENDPOINT = 'https://executor-dnrxaaj6sq-lm.a.run.app/execute'
MAX_NUM_STEPS = 5


def get_first_step(steps: Steps) -> str:
    # TODO: Implement a better function to select a step, not just the first one
    # TODO: This would correspond to the Planner in the diagram
    for step in steps:
        if step['step'] == 1:
            return step['description']


class Agent:
    def execute(self, code: str, explanation: str):
        # code = urllib.parse.quote(code)
        # explanation = urllib.parse.quote(explanation)
        response = requests.post(EXECUTOR_ENDPOINT, params={
            'code': code, 'explanation': explanation, 'task_name': self.task_name,
            'task_id': self.task.task_id, 'user_id': self.task.user_id
        })
        print(response)

    def __init__(self, initial_df: DataFrame, task: Task, task_name: str | None = None):
        self.task = task
        self.task_name = task_name if task_name is not None else self.task.task_name
        self.detector = Detector(task)
        print('=' * 70 + '  CREATING STEPS   ' + '=' * 70)
        initial_steps: Steps = self.detector.get_steps_from_initial_df(initial_df)
        # TODO display this in frontend?
        # for step in initial_steps:
        #     print(str(step['step']) + ' ---> ' + step['description'])
        initial_summary: Dict[str, str] = self.detector.get_initial_summary(initial_df)

        self.tro = TransformationOrchestrator(task)
        # curr_df = initial_df
        curr_step: str = get_first_step(initial_steps)
        curr_summary: Dict[str, str] = initial_summary
        for counter in range(1, MAX_NUM_STEPS):
            print('=' * 70 + f' ATTEMPTING STEP {counter} ' + '=' * 70)
            print(curr_step)

            print('=' * 70 + '  GENERATING CODE  ' + '=' * 70)
            code: str = self.tro.generate_code(curr_step, curr_summary)
            print(code)

            print('=' * 70 + '  EXECUTING CODE   ' + '=' * 70)
            self.execute(code, curr_step)
            print('Max step count in DB: ', task.max_step_count())
            if counter == MAX_NUM_STEPS - 1:
                break

            print('=' * 70 + '  CREATING STEPS   ' + '=' * 70)
            curr_step = get_first_step(self.detector.get_steps_from_former_steps())
            curr_summary = self.detector.get_summary_from_former_steps()


if __name__ == '__main__':
    # initial_df = pd.read_csv('test_csv/BL-Flickr-Images-Book.csv')
    initial_df = pd.read_csv('test_csv/Financials.csv')
    task = new_task(user_id='coder@example.com', task_name='coding', initial_df=initial_df)
    agent = Agent(initial_df, task)


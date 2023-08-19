import pandas as pd
from pandas import DataFrame

from api.src.database import Task
from api.src.detection import Detector, Steps
from api.src.transformation import *
from api.src.transformation import toolmaker

MAX_NUM_STEPS = 2


def _get_first_step(steps: Steps) -> str:
    for step in steps:
        if step['step'] == 1:
            return step['description']


class Agent:
    def __init__(self, initial_df: DataFrame, task: Task):
        self.detector = Detector(task)
        initial_steps: Steps = self.detector.get_steps_from_initial_df(initial_df)
        # TODO display this in frontend?
        # for step in initial_steps:
        #     print(str(step['step']) + ' ---> ' + step['description'])
        initial_summary: Dict[str, str] = self.detector.get_initial_summary(initial_df)

        self.tro = TransformationOrchestrator(task)
        curr_df = initial_df
        curr_step: str = _get_first_step(initial_steps)
        curr_summary: Dict[str, str] = initial_summary
        for counter in range(MAX_NUM_STEPS - 1):
            print(curr_step)
            print('=' * 100)
            code: str = self.tro.generate_code(curr_step, curr_summary)
            print(code)


if __name__ == '__main__':
    initial_df = pd.read_csv('test_csv/BL-Flickr-Images-Book.csv')
    agent = Agent(initial_df, None)
    # print(len(get_signatures_and_full_docstrings(transformations)))


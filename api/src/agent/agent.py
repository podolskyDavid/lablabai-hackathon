from pandas import DataFrame

from api.src.database import Task
from api.src.detection import Detector
from api.src.detection.detect_transformations import Steps


MAX_NUM_STEPS = 5


def _get_first_step(steps: Steps) -> str:
    for step in steps:
        if step['step'] == 1:
            return step['description']


class Agent:
    def __init__(self, initial_df: DataFrame, task: Task):
        self.detector = Detector()
        initial_steps: Steps = self.detector.get_steps_from_initial_df(initial_df)
        first_step: str = _get_first_step(initial_steps)

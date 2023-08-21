import pandas as pd
import requests
from pandas import DataFrame
from requests import Response

from src.database import Task
from src.detection import Detector, Steps
from src.transformation import *
from src.database import *
from src.transformation import toolmaker
import urllib
from tenacity import retry, stop_after_attempt, retry_if_result, wait_fixed
import openai
import re
import os
import dotenv


EXECUTOR_ENDPOINT = 'https://executor-dnrxaaj6sq-lm.a.run.app/execute'
MAX_NUM_STEPS = 8
openai.api_key = os.getenv("OPENAI_API_KEY")



REGENERATE_TO_FIX = """
Here is the current code
{code}
Here is the error message
{error_message}
Here is the explanation
{explanation}
Fix the code to make it work. avoid any other possible mistakes in this area. be smart.
try to fix completely everything that can ALSO happend if this error appear
act as the best python developer and data science expert
```python
```"""


def get_first_step(steps: Steps) -> str:
    for step in steps:
        return step['description']


class Agent:

    def execute(self, code: str, explanation: str):
        for line in code.splitlines():
            if "df = pd.read_csv(" in line:
                code = code.replace("df = pd.read_csv('df.csv')", "")
        response = requests.post(EXECUTOR_ENDPOINT, params={
            'code': code, 'explanation': explanation, 'task_name': self.task_name,
            'task_id': self.task.task_id, 'user_id': self.task.user_id
        })
        print("Response %s Content %s" % (response, response.content))
        if response.status_code != 200:
            print("regenerating code wait...")
            # take last two line
            self.error_message += "\n\n Error logs: " + '\n'.join(str(response.content.decode('utf-8')).splitlines()[-4:])
            raise Exception("Error in executing code")
    

    def regenerate_to_fix(self):
        """
        Regenerate the code if there is an error in execution.
        """
        prompt = REGENERATE_TO_FIX.format(code=self.temp_code, error_message=self.error_message, explanation=self.curr_step)
        params = {
            "model": "gpt-4",
            "max_tokens": 1000,
            "temperature": 0.5,
            "messages": [{"role": "user", "content": prompt}]
        }

        for retry in range(3):
            try:
                response = openai.ChatCompletion.create(**params)["choices"][0]["message"]["content"]
                new_code = "\n\n".join(re.findall(r"```python\n(.*?)```", response, re.DOTALL))
                return new_code
            except Exception as e:
                print("Retrying...")
                continue
        return None
   

        
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.5))
    def run_single_step(self):
        if self.error_message:
            self.temp_code = self.regenerate_to_fix()
        else:
            print("...generating the code...")
            self.temp_code = self.tro.generate_code(self.curr_step, self.curr_summary, self.initial_df.columns)
            
        print(self.temp_code)
        print('=' * 70 + '  EXECUTING CODE   ' + '=' * 70)
        self.execute(self.temp_code, self.curr_step)
        self.code = self.temp_code


    def __init__(self, initial_df: DataFrame, task: Task, task_name: str | None = None):
        self.temp_code = ''
        self.error_message = ''
        self.code = None
        self.task = task
        self.step_count = task.max_step_count()
        self.task_name = task_name if task_name is not None else self.task.task_name
        self.initial_df = initial_df
        self.curr_step = None

    def run(self):
        self.detector = Detector(self.task)
        print('=' * 70 + '  CREATING STEPS   ' + '=' * 70)
        initial_steps: Steps = self.detector.get_steps_from_initial_df(self.initial_df)
        print("INITIAL STEP\n", initial_steps[0])
        self.tro = TransformationOrchestrator(self.task)
        self.curr_step: str = get_first_step(initial_steps)
        self.curr_summary: Dict[str, str] = self.detector.get_initial_summary(self.initial_df)
        for counter in range(1, MAX_NUM_STEPS):
            print('=' * 70 + f' ATTEMPTING STEP {counter} ' + '=' * 70)
            print("Current step", self.curr_step)
            self.run_single_step()
            self.step_count = self.task.max_step_count()
            self.error_message = ''
            if counter == MAX_NUM_STEPS - 1:
                break

            print('=' * 70 + '  CREATING STEPS   ' + '=' * 70)
            self.curr_step = get_first_step(self.detector.get_steps_from_former_steps())
            self.curr_summary, _ = self.detector.get_summary_from_former_steps()

            print(self.task.get_latest_df().head())
    
    # def custom_message_execution(self, message: str):
    #     self.current_step_message = message
    #     self.error_message = ''
    #     self.code = ''
    #     self.run_single_step(message, self.detector.get_initial_summary(self.task.get_latest_df()), self.task.get_latest_df().columns)



if __name__ == '__main__':
    # initial_df = pd.read_csv('test_csv/BL-Flickr-Images-Book.csv')
    initial_df = pd.read_csv('../test_csv/Financials.csv')
    task = new_task(user_id='robert6@coder.com', task_name='coding', initial_df=initial_df)
    # agent = Agent(initial_df, task)
    agent = Agent(initial_df, task, task_name='coding')
    # agent.custom_message_execution("Convert column 'date' to datetime format.")
    agent.run()


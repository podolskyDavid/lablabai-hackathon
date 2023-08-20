import os
from tempfile import NamedTemporaryFile

import pandas as pd
from fastapi import FastAPI
from starlette.responses import JSONResponse
import subprocess
import logging
from src.database.task import Task

app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

os.system("pip install pandas")


def execute_code(code):
    try:
        output = subprocess.check_output(
            ["python3", "-c", code], stderr=subprocess.STDOUT, text=True
        )
        return output.strip()
    except subprocess.CalledProcessError as e:
        return (
            e.output
        )  # This captures both stdout and stderr, since we redirected stderr to stdout


@app.post("/execute")
async def execute(
    user_id: str,
    task_id: int,
    task_name: str,
    code: str,
    explanation: str,
):
    task = Task(
        user_id=user_id,
        task_id=task_id,
    )
    exec_result = ""
    try:
        df = task.get_latest_df()
        with NamedTemporaryFile(suffix=".csv") as f1, NamedTemporaryFile(
            suffix=".csv", mode="w+"
        ) as f2:
            df.to_csv(f1.name, index=False)

            import_line = f"""\
import pandas as pd
df = pd.read_csv('{f1.name}')
"""
            end_line = f"""\
df.to_csv('{f2.name}', index=False)
"""
            f2.seek(0)
            full_code = import_line + code + end_line
            exec_result = execute_code(full_code)
            if os.path.exists(f2.name):
                new_df = pd.read_csv(f2.name)
            else:
                logger("File does not exist")

        task = Task(user_id=user_id, task_id=task_id, task_name=task_name)
        task.upload_new_step(
            transformation=code,
            explanation=explanation,
            df_after=new_df,
            df_frontend=new_df,
        )
        logger.error("Task id, task max step count: %s_%s", task_id, task.max_step_count())
    except Exception as e:
        logger.error(e)
        logger.error("Exec result: %s", exec_result)
        return JSONResponse(
            {
                "code_output": exec_result
            }, 
            status_code=500)
    return JSONResponse({"code_output": exec_result})

from typing import Annotated
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, File
import pandas as pd
import io

from api.src.agent.agent import Agent
from api.src.database import new_task

app = FastAPI()
task = None
task_id = None

@app.get("/")
def root():
    return "This is the API endpoint which receives the user's file"


@app.post("/upload/")
def upload_file(user_id: str, task_name: str | None = None, file: UploadFile = File(...)):
    """
    Receive a file from the frontend. Upload it to the DB and trigger the agent to execute the steps on it.
    :returns: task_id
    """
    try:
        contents = file.file.read()
        df = pd.read_csv(io.BytesIO(contents))

        task_name = task_name if task_name is not None else file.filename
        global task, task_id
        task = new_task(user_id, task_name, df)
        task_id = task.task_id

        agent = Agent(df, task)
        return {'task_id': agent.task.task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

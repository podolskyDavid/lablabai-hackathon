import time
from typing import *

import asyncio
import uvicorn
from fastapi import FastAPI, UploadFile, HTTPException, File, BackgroundTasks
import pandas as pd
import io

from sse_starlette import EventSourceResponse
from starlette.requests import Request

from api.src.agent.agent import Agent
from api.src.database import new_task, Task

# STATE_CHECK_DELAY = 0.1  # seconds
STREAM_DELAY = 3  # seconds
RETRY_TIMEOUT = 15_000  # miliseconds


app = FastAPI()
app.state_storage = {}


@app.get("/")
def root(task_id: int):
    return {
            key: value for key, value in app.state_storage[task_id].items()
            if key != 'agent'
        }

@app.get("/test")
def test():
    app.state_storage[111] = {
        'df_after_url': None,
        'df_frontend_url': None,
        'code': None,
        'explanation': None,
        'step_count': -1,
    }


@app.post("/upload")
def upload_file(user_id: str, task_name: str | None = None, file: UploadFile = File(...),
                background_tasks: BackgroundTasks = None):
    """
    Receive a file from the frontend. Upload it to the DB and launch the agent which will start executing the steps.
    :returns: task_id
    """
    
    try:
        print('INIT UPLOAD')
        contents = file.file.read()
        df = pd.read_csv(io.BytesIO(contents))

        task_name = task_name if task_name is not None else file.filename
        task = new_task(user_id, task_name, df)
        task_id = task.task_id
        agent = Agent(df, task)
        print(f"READY TO UPDATE STATE STORAGE {task_id}")
        app.state_storage[task_id] = {
            'agent': agent,
            'df_after_url': None,
            'df_frontend_url': None,
            'code': None,
            'explanation': None,
            'step_count': -1,
        }
        print(f"UPDATED STATE STORAGE WITH {task_id}")
        print(app.state_storage)
        background_tasks.add_task(agent.run)
        return {'task_id': task_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

def update_storage(a: Agent, task_id: int):
    # Update storage
    data_dict: Dict = a.task.get_latest_data()
    print('DATA_DICT: ', data_dict)
    app.state_storage[task_id] = {
        'agent': a,
        'df_after_url': data_dict['df_after'],
        'df_frontend_url': data_dict['df_frontend'],
        'code': data_dict['transformation'],
        'explanation': data_dict['explanation'],
        'step_count': int(a.step_count),
    }


def new_code_and_explanation(task_id: int):
    """
    Yield True if the internal code and explanation of the agent object have changed compared to the app.state_storage.
    This means that the agent has successfully generated code and explanation.
    """

    a: Agent = app.state_storage[task_id]['agent']
    if a.code is not None and a.code != app.state_storage[task_id]['code'] \
            and a.curr_step is not None and a.curr_step != app.state_storage[task_id]['explanation']:
        print(f'RETURNING TRUE from new_code_and_explanation\n'
              f'A_CODE           : {a.code[:100] if a.code is not None else None}\n'
              f'STATE_CODE       : {app.state_storage[task_id]["code"][:100] if app.state_storage[task_id]["code"] is not None else None}\n'
              f'A_CURR_STEP      : {a.curr_step}\n'
              f'STATE_EXPLANATION: {app.state_storage[task_id]["explanation"]}\n'
        )
        app.state_storage[task_id]['code'] = a.code
        app.state_storage[task_id]['explanation'] = a.curr_step
        return True


def new_step_count(task_id: int):
    """
    Yield True if step_count of the agent object has increased compared to the app.state_storage.
    This means that the agent has successfully executed code.
    """
    
    a: Agent = app.state_storage[task_id]['agent']
    if a.step_count > app.state_storage[task_id]['step_count']:
        print('RETURNING TRUE from new_step_count')
        app.state_storage[task_id]['step_count'] = int(a.step_count)
        time.sleep(STREAM_DELAY)  # before accessing Supabase
        data_dict: Dict = a.task.get_latest_data()
        app.state_storage[task_id]['df_after_url'] = data_dict['df_after']
        app.state_storage[task_id]['df_frontend_url'] = data_dict['df_frontend']
        return True

async def event_generator(request, task_id):
    # at this point, it's guaranteed that app.state_storage[task_id] exists

    while True:
        # If client closes connection, stop sending events
        if await request.is_disconnected():
            break

        # If code and explanation were generated
        if new_code_and_explanation(task_id):
            # a: Agent = app.state_storage[task_id]['agent']
            # update_storage(a, task_id)

            # Don't yield dataframe URLs here: they still correspond to the previous step
            # because the code hasn't been executed yet
            yield {
                "event": 'Explanation and code generated (new_code_and_explanation)',
                "id": task_id,
                "retry": RETRY_TIMEOUT,
                "data": {
                    key: value for key, value in app.state_storage[task_id].items()
                    if key != 'agent' and key != 'df_after_url' and key != 'df_frontend_url'
                }
            }

        # If code was executed
        if new_step_count(task_id):
            # a: Agent = app.state_storage[task_id]['agent']
            # print('NEW STEP COUNT before update: ', a.step_count, app.state_storage[task_id]['step_count'])
            # update_storage(a, task_id)
            # print('NEW STEP COUNT after update : ', a.step_count, app.state_storage[task_id]['step_count'])

            # Yield everything besides the agent object
            yield {
                "event": 'Code executed (new_step_count)',
                "id": task_id,
                "retry": RETRY_TIMEOUT,
                "data": {
                    key: value for key, value in app.state_storage[task_id].items()
                    if key != 'agent'
                },
            }

        await asyncio.sleep(STREAM_DELAY)


@app.get('/stream')
async def message_stream(request: Request, task_id: int):
    if task_id not in app.state_storage:
        raise HTTPException(status_code=404, detail=f"Task with task_id={task_id} not found\n{app.state_storage}")
    return EventSourceResponse(event_generator(request, task_id))

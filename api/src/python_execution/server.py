from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
import docker
import uuid
import io
import tarfile
import json
import pandas as pd
from src.database.task import Task
from tempfile import NamedTemporaryFile


app = FastAPI()
client = docker.from_env()


def generate_container():
    container = client.containers.run(
        'python:3.11-slim', 
        command='''bash -c "
            apt-get update && 
            apt-get install -y python3-pip &&
            tail -f /dev/null"
        ''',
        detach=True,
        remove=True,
    )
    print(container.logs())

    container.exec_run(['pip', 'install', "pandas"])
    container.exec_run(['pip', 'install', "numpy"])
    container.exec_run(['pip', 'install', "scipy"])
    container.exec_run(['pip', 'install', "scikit-learn"])
    container.exec_run(['pip', 'install', "plotly"])
    # container.exec_run(['pip', 'install', "fuzzywuzzy"])
    # container.exec_run(['pip', 'install', "nltk"])
    # container.exec_run(['pip', 'install', "statsmodels"])
    # container.exec_run(['pip', 'install', "gensim"])

    return container

sessions = {}

@app.post("/start")
async def start(
    user_id: str,
    task_id: int
):

    session_id = str(uuid.uuid4())
    container = generate_container()
    sessions[session_id] = container
    tarstream = io.BytesIO()
    tar = tarfile.TarFile(fileobj=tarstream, mode='w')
    task = Task(
        user_id=user_id,
        task_id=task_id
    )
    df = task.get_latest_df()
    with NamedTemporaryFile() as f:
        df.to_csv(f.name, index=False)
        tar.add(f.name, arcname='df.csv')
        tar.close()
        tarstream.seek(0)
        container.put_archive('/', tarstream)
        tarstream.close()
    container.exec_run('ls /')
    print('container started')
    return JSONResponse({'session_id': session_id})

@app.post("/execute")
async def execute(
    session_id: str,
    user_id: str,
    task_id: int,
    task_name: str,
    code: str,
    explanation: str,
):
    container = sessions[session_id]
    import_line = """\
import pandas as pd
df = pd.read_csv('df.csv')
"""
    end_line = """

df.to_csv('df.csv', index=False)
"""
    code = import_line + code + end_line
    exec_result = container.exec_run(['python', '-c', code])
    # if error?
    code_output = exec_result.output.decode('utf-8')

    # putting it back to the bucket
    bits, stat = container.get_archive('df.csv')
    tar_data = b''.join(bits)

    with NamedTemporaryFile() as f:
        with io.BytesIO(tar_data) as tar_buffer:
            with tarfile.open(fileobj=tar_buffer) as tar:
                # save to temporary file
                with tar.extractfile('df.csv') as exfile:
                    with open(f.name, 'wb') as outfile:
                        outfile.write(exfile.read())
                f.seek(0)

                

                task = Task(
                    user_id=user_id,
                    task_id=task_id,
                    task_name=task_name
                )
                print(pd.read_csv(f.name).head())
                task.upload_new_step(
                    transformation=code,
                    explanation=explanation,
                    df_after=pd.read_csv(f.name),
                    df_frontend=pd.read_csv(f.name)
                )
                print('uploaded to bucket')

    return JSONResponse(
        {
            'code_output': code_output
        }
    )

# 'step_id': step_id, NO
#             'task_id': self.task_id, YES from backend
#             'task_name': self.task_name, YES from backend
#             'step_count': self.max_step_count, NO
#             'user_id': self.user_id, # YES from backend
#             'transformation': transformation, # YES from frontend
#             'explanation': explanation, # YES from frontend
#             'df_after': df_after_url, YES, calculated by me
#             'df_frontend': df_frontend_url # NO

@app.post("/end")
async def end(request: Request):
    data = await request.json()
    session_id = data['session_id']
    container = sessions[session_id]
    container.stop()
    container.remove()
    del sessions[session_id]

    return JSONResponse({ 'status': 'session ended' })
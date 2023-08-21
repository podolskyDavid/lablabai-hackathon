
# start a docker
in terminal: 
`make build run`


# 1. Starting a File

To initiate a session:

```python
import requests

def start_session(user_id, task_id, url="http://0.0.0.0:80/start"):
    response = requests.post(f"{url}?user_id={user_id}&task_id={task_id}")
    return response.json()['session_id']

session = start_session("alex@example.com", 1)
print(session)
```

### 3. Execute Code

To execute a specific code in the session:

```python
def execute_code_in_session(session_id, code, url="http://0.0.0.0:80/execute"):
    response = requests.post(f"{url}?session_id={session_id}&code={code}")
    return response.json()

code_output = execute_code_in_session(session, "print(df.head())")
print(code_output['code_output'])
```
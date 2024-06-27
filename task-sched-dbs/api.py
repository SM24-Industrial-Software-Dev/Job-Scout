from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from enum import Enum
from datetime import datetime, timezone
import isodate
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

app = FastAPI()

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
tasks = dynamodb.Table("Tasks")
executions = dynamodb.Table("Executions")
history = dynamodb.Table("History")

    



class Task(BaseModel):
    def __init__(self, task_function):
        self.task_function = task_function
    task_id: int
    user_id: int
    mode: Mode
    recurring: bool
    interval: str
    retries: int
    created: int


class UpdateTask(BaseModel):
    update_key: str
    update_value: str

class HistoryData(BaseModel):
    task_id: int
    exec_time: int
    status: str
    retries: int
    last_update: int


class ExecutionData(BaseModel):
    next_exec_time: int
    task_id: int

#adds the task to the tasks table as well as the executionData table
#if there's an error with either of those additions, throws an exception
@app.post("/tasks/")
def create_task(task: Task):
    try:
        tasks.put_item(
            Item={
                'task_id': task.task_id,
                'user_id': task.user_id,
                'mode': task.mode,
                'recurring': task.recurring,
                'interval': task.interval,
                'retries': task.retries,
                'created': task.created
            }
        )
        executions.put_item(
            Item={
                'task_id': task.task_id,
                'next_exec_time': datetime.now() + isodate.parse_duration(task.interval)
            }
        )
        return {"message": f"Task {task.task_id} created successfully."}
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    try:
        response = tasks.get_item(
            Key={
                'task_id': task_id
            }
        )
        item = response.get('Item')
        if item is not None:
            return item
        else:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: UpdateTask):
    try:
        response = tasks.update_item(
            Key={
                'task_id': task_id
            },
            UpdateExpression=f"set #attr = :val",
            ExpressionAttributeNames={
                '#attr': update.update_key
            },
            ExpressionAttributeValues={
                ':val': update.update_value
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    try:
        response = tasks.delete_item(
            Key={
                'task_id': task_id
            }
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def execute_task(task: Task):
    ##insert kafka listening code here
    if task.mode == Mode.NOTIFS:
        noti = task.task_function
    elif task.mode == Mode.REFRESH:
        refresh = task.task_function

def get_unix_timestamp_by_min(dt: datetime) -> int:
    # Set seconds and microseconds to zero
    dt = dt.replace(second=0, microsecond=0)
    
    # Convert to UNIX timestamp
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp

# To run the server, use the command below in your terminal
# uvicorn main:app --reload
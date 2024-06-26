from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

app = FastAPI()

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
tasks = dynamodb.Table("Tasks")
executions = dynamodb.Table("Executions")
history = dynamodb.Table("History")


class Task(BaseModel):
    task_id: int
    user_id: int
    type: bool
    recurring: bool
    interval: str
    retries: int
    created: int


class UpdateJob(BaseModel):
    update_key: str
    update_value: str

@app.post("/tasks/")
def create_task(job: Job):
    try:
        table.put_item(
            Item={
                'job_id': job.job_id,
                'title': job.title,
                'description': job.description,
                'company': job.company,
                'location': job.location
            }
        )
        return {"message": f"Job {job.job_id} created successfully."}
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        response = table.get_item(
            Key={
                'job_id': job_id
            }
        )
        item = response.get('Item')
        if item:
            return item
        else:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/jobs/{job_id}")
def update_job(job_id: str, update: UpdateJob):
    try:
        response = table.update_item(
            Key={
                'job_id': job_id
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

@app.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    try:
        response = table.delete_item(
            Key={
                'job_id': job_id
            }
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run the server, use the command below in your terminal
# uvicorn main:app --reload
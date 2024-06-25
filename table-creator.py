from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

app = FastAPI()

# Specify your region here
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  

class Job(BaseModel):
    job_id: str
    title: str
    description: str
    company: str
    location: str

class UpdateJob(BaseModel):
    update_key: str
    update_value: str

@app.post("/create-jobs-table/")
def create_jobs_table():
    try:
        table = dynamodb.create_table(
            TableName='Jobs',
            KeySchema=[
                {
                    'AttributeName': 'job_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'job_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName='Jobs')
        return {"message": "Table 'Jobs' created successfully."}
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            return {"message": "Table 'Jobs' already exists."}
        else:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs/")
def create_job(job: Job):
    try:
        table = dynamodb.Table('Jobs')
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
        table = dynamodb.Table('Jobs')
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
        table = dynamodb.Table('Jobs')
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
        table = dynamodb.Table('Jobs')
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
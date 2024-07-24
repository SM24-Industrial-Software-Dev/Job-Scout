from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

app = FastAPI()

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD:main.py
# Start the master scheduler in the background
master_thread = threading.Thread(target=master.run, daemon=True)
master_thread.start()

class TaskUpdateRequest(BaseModel):
    task_id: int
    new_task: Task
=======
# Specify your region here
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
>>>>>>> 9101702b0d4f996e8d3a90e47f61c2c19e5bb78b:table-creator.py
=======
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
table = dynamodb.Table("Jobs")
>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b


<<<<<<< HEAD
<<<<<<< HEAD:main.py
@app.post("/add_search/")
def add_job_search(job_search: Notifs):
    try:
        task_id = master.add_task(job_search)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/instant_search/")
def scrape_jobs():
    return master.scrape_jobs()

@app.get("/login")
def login(request: Request):
    google_oauth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        "&client_id={client_id}"
        "&redirect_uri={redirect_uri}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
    ).format(client_id=client_id, redirect_uri=redirect_uri)
    logging.info(f"Redirecting to Google OAuth URL: {google_oauth_url}")
    return RedirectResponse(google_oauth_url)

@app.get("/callback")
def callback(code: str, request: Request):
    logging.info(f"Received callback with code: {code}")
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
=======
=======
=======
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  
table = dynamodb.Table("Jobs")


>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b
class Job(BaseModel):
    job_id: str
    title: str
    description: str
    company: str
    location: str

<<<<<<< HEAD
>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b
=======
>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b
class UpdateJob(BaseModel):
    update_key: str
    update_value: str

@app.post("/jobs/")
def create_job(job: Job):
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
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 9101702b0d4f996e8d3a90e47f61c2c19e5bb78b:table-creator.py
=======
>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b
=======
>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b

# To run the server, use the command below in your terminal
# uvicorn main:app --reload
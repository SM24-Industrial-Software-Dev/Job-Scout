from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import requests
import threading
import subprocess
import uvicorn
import logging
import os
import sys
from pydantic import BaseModel

# Add the parent directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importing from your own modules
from task_sched_dbs.Master import Master
from task_sched_dbs.Tables import Notifs, Task
from flask_application import app as flask_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth configuration
client_id = '197014094036-rbrpc7ot7nmkkj401809qbb1nheakeis.apps.googleusercontent.com'
client_secret = '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'
redirect_uri = 'http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/callback'

# Initialize FastAPI app
app = FastAPI()
master = Master(18)

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

@app.delete("/delete_task/{task_id}")
def delete_task(task_id: int):
    result = master.delete_task(task_id)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

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
>>>>>>> 9101702b0d4f996e8d3a90e47f61c2c19e5bb78b:table-creator.py

    try:
        token_r = requests.post(token_url, data=token_data)
        token_r.raise_for_status()
        token_json = token_r.json()
        id_token = token_json.get("id_token")
        access_token = token_json.get("access_token")
        logging.info(f"Token response: {token_json}")

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        userinfo_params = {"access_token": access_token}
        userinfo_response = requests.get(userinfo_url, params=userinfo_params)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

        logging.info(userinfo)
        
        # Redirect to logged-in application
        return RedirectResponse("http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8502")  # Ensure this URL points to logged_in_app.py
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during token exchange: {e}")
        return {"error": str(e)}

@app.get("/is_logged_in")
def is_logged_in():
    # Implement a check for login status
    # For now, just return a dummy response
    return {"status": "success", "name": "John Doe"}

def run_fastapi():
    logging.info('Starting FastAPI on port 8000')
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

def run_flask():
    logging.info('Starting Flask app on port 8080')
    flask_app.run(host="0.0.0.0", port=8080)

def run_logged_in_app():
    subprocess.Popen(['streamlit', 'run', 'logged_in_app.py', '--server.port', '8502'])

def run_streamlit():
    subprocess.Popen(['streamlit', 'run', 'app.py', '--server.port', '8501'])

if __name__ == "__main__":
    fastapi_thread = threading.Thread(target=run_fastapi)
    flask_thread = threading.Thread(target=run_flask)
    streamlit_thread = threading.Thread(target=run_streamlit)
    logged_in_app_thread = threading.Thread(target=run_logged_in_app)

    fastapi_thread.start()
    flask_thread.start()
    streamlit_thread.start()
    logged_in_app_thread.start()

    fastapi_thread.join()
    flask_thread.join()
    streamlit_thread.join()
    logged_in_app_thread.join()
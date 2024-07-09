from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialize DynamoDB resource
try:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    dynamodb_client = boto3.client(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # Check if 'Users' table exists, create if not
    try:
        users_table = dynamodb.Table('Users')
        users_table.load()
    except dynamodb_client.exceptions.ResourceNotFoundException:
        dynamodb_client.create_table(
            TableName='Users',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        users_table = dynamodb.Table('Users')
    
    # Check if 'Tasks' table exists, create if not
    try:
        tasks_table = dynamodb.Table('Tasks')
        tasks_table.load()
    except dynamodb_client.exceptions.ResourceNotFoundException:
        dynamodb_client.create_table(
            TableName='Tasks',
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        tasks_table = dynamodb.Table('Tasks')
except Exception as e:
    print(f"Error initializing DynamoDB: {e}")

class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    preferred_job_type: Optional[str] = None
    preferred_location: Optional[str] = None

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    job_type: str
    location: str

class EmailSchema(BaseModel):
    subject: str
    recipients: List[EmailStr]
    body: str

def send_email(subject: str, recipients: List[str], body: str):
    try:
        server = smtplib.SMTP(host=SMTP_SERVER, port=SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = MAIL_FROM
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server.sendmail(MAIL_FROM, recipients, msg.as_string())
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register/")
async def register_user(user: User):
    try:
        users_table.put_item(Item=user.dict())
        return {"message": "User registered successfully."}
    except ClientError as e:
        raise HTTPException(status_code=500, detail=e.response['Error']['Message'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/")
async def create_task_and_notify(task: Task, background_tasks: BackgroundTasks):
    try:
        tasks_table.put_item(Item=task.dict())
    except ClientError as e:
        raise HTTPException(status_code=500, detail=e.response['Error']['Message'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        response = users_table.scan()
        users = response.get('Items', [])

        # Filter users based on preferences
        interested_users = [
            user for user in users
            if (user.get('preferred_job_type') == task.job_type or user.get('preferred_job_type') is None) and
               (user.get('preferred_location') == task.location or user.get('preferred_location') is None)
        ]
        
        recipient_emails = [user['email'] for user in interested_users]

        email = EmailSchema(
            subject=f"New Task Created: {task.title}",
            recipients=recipient_emails,
            body=f"Task '{task.title}' has been created with description: {task.description}"
        )

        background_tasks.add_task(send_email, email.subject, email.recipients, email.body)
        return task
    except ClientError as e:
        raise HTTPException(status_code=500, detail=e.response['Error']['Message'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
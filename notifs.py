import boto3
import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, NoRegionError
from boto3.dynamodb.conditions import Attr

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # Provide default region if not set
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
NOTIFS_QUEUE_URL = os.getenv("NOTIFS_QUEUE_URL")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT", 587)  # Provide default SMTP port if not set
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")

# Check if essential environment variables are missing
if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, NOTIFS_QUEUE_URL, SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, MAIL_FROM]):
    logger.error("One or more essential environment variables are missing.")
    raise SystemExit("Missing environment variables")

# Initialize SQS client
try:
    sqs_client = boto3.client(
        'sqs',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
except NoRegionError as e:
    logger.error(f"AWS region not specified: {str(e)}")
    raise

# Initialize DynamoDB resource
try:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
except NoRegionError as e:
    logger.error(f"AWS region not specified: {str(e)}")
    raise

# Function to send email
def send_email(subject: str, recipients: list, body: str):
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
        logger.error(f"Error sending email: {str(e)}")

# Function to process messages from Notifs Queue
def process_notifs_message():
    try:
        response = sqs_client.receive_message(
            QueueUrl=NOTIFS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        if 'Messages' in response:
            for message in response['Messages']:
                body = json.loads(message['Body'])
                job_title = body['job_title']
                location = body['location']
                company = body['company']
                user_email = body['email']

                # Perform search
                search_results = perform_search(job_title, location, company)

                # Send email with results
                send_email(
                    subject=f"Job Search Results for {job_title} in {location} at {company}",
                    recipients=[user_email],
                    body=f"Here are the job search results for {job_title} in {location} at {company}:\n\n{search_results}"
                )

                sqs_client.delete_message(
                    QueueUrl=NOTIFS_QUEUE_URL,
                    ReceiptHandle=message['ReceiptHandle']
                )
    except Exception as e:
        logger.error(f"Error processing notifs message: {str(e)}")

# Function to perform search
def perform_search(job_title, location, company):
    table = dynamodb.Table('Jobs')
    search_results = []

    # Scan the table for matching job_title and location
    response = table.scan(
        FilterExpression=Attr('title').contains(job_title) & Attr('location').contains(location) & Attr('company').contains(company)
    )
    for job in response['Items']:
        search_results.append(f"Title: {job['title']}, Company: {job['company']}, Location: {job['location']}, Link: {job['link']}")

    if not search_results:
        return "No matching jobs found."

    return "\n".join(search_results)

if __name__ == "__main__":
    while True:
        process_notifs_message()

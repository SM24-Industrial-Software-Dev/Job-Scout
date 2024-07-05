import streamlit as st
import boto3
import os
from os.path import join, dirname
from dotenv import load_dotenv
from boto3.dynamodb.conditions import Attr
import time

# Load environment variables from .env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Initialize SQS and DynamoDB clients
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION'))
queue_url = os.getenv("QUEUE_URL")
table_name = os.getenv("DYNAMODB_TABLE")

st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job \nlisting sites and saving "
    "user-defined searches. Utilizing a distributed work \nscheduler, it regularly updates the job listings database "
    "and notifies users of new \nopportunities. The application also features a user-friendly web interface for "
    "\nmanual queries and real-time results."
)

job_title = st.text_input("Job Title:")  # can add default value
states = [
    '', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
    'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
    'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
    'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia',
    'Wisconsin', 'Wyoming'
]
location = st.selectbox(label="Location:", options=states)  # make empty string the default for entire U.S.
company = st.text_input("Company:")  # can add default value

def read_jobs(job_title=None, location=None, company=None):
    table = dynamodb.Table(table_name)
    scan_kwargs = {}
    filter_expression = None
    if job_title:
        filter_expression = Attr('job_title').eq(job_title)
    if location:
        filter_expression = filter_expression & Attr('location').eq(location) if filter_expression else Attr(
            'location').eq(location)
    if company:
        filter_expression = filter_expression & Attr('company').eq(company) if filter_expression else Attr(
            'company').eq(company)

    if filter_expression:
        scan_kwargs['FilterExpression'] = filter_expression

    response = table.scan(**scan_kwargs)
    return response.get('Items', [])

if st.button("Search"):
    if job_title or location or company:
        # Send the search query to SQS
        message = {
            'job_title': job_title,
            'location': location,
            'company': company
        }
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=str(message)
        )
        st.write("Search query sent. Waiting for results...")

        # Simulate waiting for results and then reading from DynamoDB
        # In a real-world scenario, this should be replaced with logic to wait for processing to complete
        time.sleep(5)  # Simulate delay for processing

        results = read_jobs(job_title, location, company)
        if results:
            st.write("Results:", results)
        else:
            st.write("No matching jobs found.")
    else:
        st.error("Please enter at least one search criteria.")

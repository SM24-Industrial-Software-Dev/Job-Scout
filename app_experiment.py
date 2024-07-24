import os
from dotenv import load_dotenv
import streamlit as st
import boto3
import json
import requests
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_DEFAULT_REGION')

# Initialize a session using the provided credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region
)

# Initialize the DynamoDB client
dynamodb = session.resource('dynamodb')
table_name = 'Jobs'

try:
    table = dynamodb.Table(table_name)
    # Check if table exists
    table.load()
except ClientError as e:
    st.error(f"Could not connect to DynamoDB table: {e.response['Error']['Message']}")

# Initialize the SQS client
sqs = boto3.client('sqs', region_name='us-east-2')
queue_url = 'https://us-east-2.queue.amazonaws.com/767397805190/QueryJobsDB'  # Replace with your actual SQS Queue URL - replaced
=======

# Initialize the SQS client
sqs = boto3.client('sqs', region_name='us-east-2')
queue_url = 'https://us-east-2.queue.amazonaws.com/767397805190/QueryJobsDB'  # Replace with your actual SQS Queue URL

next_task_id_counter = 0

def next_task_id():
    global next_task_id_counter
    next_task_id_counter += 1
    return next_task_id_counter
>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b

st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job \nlisting sites and saving "
    "user-defined searches. Utilizing a distributed work \nscheduler, it regularly updates the job listings database "
    "and notifies users of new \nopportunities. The application also features a user-friendly web interface for "
    "\nmanual queries and real-time results.")

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

<<<<<<< HEAD
login_url = "http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/login"
logout_url = "http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/logout"
is_logged_in_url = "http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/is_logged_in"

if 'button_login_pressed' not in st.session_state:
    st.session_state.button_login_pressed = False

# Function to check login status
def check_login_status():
    response = requests.get(is_logged_in_url)
    if response.status_code == 200:
        data = response.json()
        st.session_state.button_login_pressed = data['logged_in']

# Function to handle login press
def handle_button_login_press():
    st.session_state.button_login_pressed = True
    st.markdown(f'<meta http-equiv="refresh" content="0; url={login_url}">', unsafe_allow_html=True)
    check_login_status()

# Function to handle logout press
def handle_button_logout_press():
    st.session_state.button_login_pressed = False
    st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)

# Sidebar for floating menu
with st.sidebar:
    st.header("Menu")
    # Display buttons based on the session state
    if not st.session_state.button_login_pressed:
        if st.button("Login with Google"):
            handle_button_login_press()
    else:
        if st.button("Logout"):
            handle_button_logout_press()

# Function to retrieve all jobs from DynamoDB
def get_all_jobs():
    try:
        response = table.scan()
        return response.get('Items', [])
    except ClientError as e:
        st.error(f"An error occurred: {e.response['Error']['Message']}")
        st.error(f"Error code: {e.response['Error']['Code']}")
        st.error(f"Request ID: {e.response['ResponseMetadata']['RequestId']}")
        return []

# Display the jobs in Streamlit
def display_jobs(jobs):
    for job in jobs:
        st.subheader(job.get('title', 'No Title'))
        st.write(f"Location: {job.get('location', 'Unknown')}")
        st.write(f"Company: {job.get('company', 'Unknown')}")
        st.write(f"Description: {job.get('description', 'No Description')}")
        st.write("---")

if st.button("search"):
    if job_title or location or company:
        try:
            # Send message to SQS
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=(
                    json.dumps({
                        'job_title': job_title,
                        'location': location,
                        'company': company
                    })
                )
            )
            st.error('Please Login to be able to use the saved search notification service.')
        except ClientError as e:
            st.error(f"Could not send message to SQS queue: {e.response['Error']['Message']}")
            st.error(f"Error code: {e.response['Error']['Code']}")
            st.error(f"Request ID: {e.response['ResponseMetadata']['RequestId']}")
    else:
        st.error("Please fill out a field before searching.")

# Fetch and display all jobs from the Jobs table
jobs = get_all_jobs()
display_jobs(jobs)

=======
if st.button("search"):
    if job_title or location or company:
        # Prepare the job search data

        ##HARDCODED RIGHT NOW -- NEED TO UPDATE
        job_search_data = {
            'task_id': next_task_id(),  # Example task_id, adjust as necessary
            'interval': "PT1M",  # Example interval, adjust as necessary
            'retries': 3,  # Example retries, adjust as necessary
            'type': "notif",  # Example type, adjust as necessary
            'user_id': 1,
            'email': "email",
            'job_id': None,
            'title': job_title,
            'description': None,
            'company': company,
            'location': location
        }

        # Convert job_id and description to the appropriate types
        job_search_data['job_id'] = job_search_data['job_id'] if job_search_data['job_id'] is not None else 0
        job_search_data['description'] = job_search_data['description'] if job_search_data['description'] is not None else ""

        try:
            # Send message to SQS
            #sqs_response = sqs.send_message(
            #    QueueUrl=queue_url,
            #    MessageBody=json.dumps(job_search_data)
            #)

            # Send job search data to FastAPI endpoint
            fastapi_response = requests.post(
                'http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8000/add_search/',  # Ensure this URL is correct
                json=job_search_data
            )

            if fastapi_response.status_code == 200:
                st.success('Search request sent! Check your results shortly.')
            else:
                st.error(f"Failed to add job search. Error: {fastapi_response.text}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

    else:
        st.error("Please fill out all fields before searching.")
>>>>>>> 708af31af46e05862e46f7c94ebc29a4a64ba30b

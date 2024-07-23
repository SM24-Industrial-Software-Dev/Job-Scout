import streamlit as st
import boto3
import json
import requests

# Initialize the SQS client
sqs = boto3.client('sqs', region_name='us-east-2')
queue_url = 'https://us-east-2.queue.amazonaws.com/767397805190/QueryJobsDB'  # Replace with your actual SQS Queue URL - replaced



st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job \nlisting sites and saving "
    "user-defined searches. Utilizing a distributed work \nscheduler, it regularly updates the job listings database "
    "and notifies users of new \nopportunities. The application also features a user-friendly web interface for "
    "\nmanual queries and real-time results.")

job_title = st.text_input("Job Title:") # can add default value
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
location = st.selectbox(label="Location:", options=states) # make empty string the default for entire U.S.
company = st.text_input("Company:") # can add default value

login_url = "http://localhost:8080/login"
logout_url = "http://localhost:8080/logout"
is_logged_in_url = "http://localhost:8080/is_logged_in"

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

# Function to retrieve messages from SQS
# def retrieve_messages():
#     response = sqs.receive_message(
#         QueueUrl=queue_url,
#         MaxNumberOfMessages=10,
#         WaitTimeSeconds=5
#     )
#     return response.get('Messages', [])


if st.button("search"):
    if job_title or location or company:
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
    else:
        st.error("Please fill out a field before searching.")

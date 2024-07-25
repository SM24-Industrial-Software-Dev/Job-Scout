import streamlit as st
import boto3
import json
import requests

# IMPORTANT INFO: To run using localhost use streamlit run logged_in_app.py --server.port 8502

# Initialize the SQS client
sqs = boto3.client('sqs', region_name='us-east-2')
queue_url = 'https://us-east-2.queue.amazonaws.com/767397805190/QueryJobsDB'  # Replace with your actual SQS Queue URL

# Initialize the next_task_id in Streamlit's session state
if 'next_task_id_counter' not in st.session_state:
    st.session_state.next_task_id_counter = 0
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def next_task_id():
    st.session_state.next_task_id_counter += 1
    return st.session_state.next_task_id_counter


st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job \nlisting sites and saving "
    "user-defined searches. Utilizing a distributed work \nscheduler, it regularly updates the job listings database "
    "and notifies users of new \nopportunities. The application also features a user-friendly web interface for "
    "\nmanual queries and real-time results.")


job_title = st.text_input("Job Title:")
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
location = st.selectbox(label="Location:", options=states)
company = st.text_input("Company:")

login_url = "http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/login"
logout_url = "http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/logout"

if 'button_login_pressed' not in st.session_state:
    st.session_state.button_login_pressed = False

# Function to handle logout press
def handle_button_logout_press():
    st.session_state.button_login_pressed = False
    # Redirect to logout URL and then to app.py
    st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)

# Sidebar for floating menu
with st.sidebar:
    if st.button("Logout"):
        handle_button_logout_press()

if st.button("search"):
    if job_title or location or company:
        user_id = st.session_state.user_info['sub']
        job_search_data = {
            'task_id': next_task_id(),
            'interval': "PT1M",
            'retries': 3,
            'type': "notif",
            'user_id': user_id,
            'email': "email",
            'job_id': None,
            'title': job_title,
            'description': None,
            'company': company,
            'location': location
        }

        job_search_data['job_id'] = job_search_data['job_id'] if job_search_data['job_id'] is not None else 0
        job_search_data['description'] = job_search_data['description'] if job_search_data['description'] is not None else ""

        try:
            fastapi_response = requests.post(
                'http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8000/add_search/',
                json=job_search_data
            )

            if fastapi_response.status_code == 200:
                st.success('Search request sent! Check your results shortly.')
            else:
                st.error(f"Failed to add job search. Error: {fastapi_response.text}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

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

    else:
        st.error("Please fill out a field before searching.")

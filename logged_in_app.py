import streamlit as st
import requests
import json
import boto3


# Initialize the SQS client
sqs = boto3.client('sqs', region_name='us-east-2')
queue_url = 'https://sqs.us-east-2.amazonaws.com/767397805190/refresh-queue'  # Replace with your actual SQS Queue URL

# Verify that the queue_url is set correctly
st.write(f"Queue URL: {queue_url}")

# Initialize the next_task_id in Streamlit's session state
if 'next_task_id_counter' not in st.session_state:
    st.session_state.next_task_id_counter = 0

if 'user' not in st.session_state:
    st.session_state.user_info = None

def next_task_id():
    st.session_state.next_task_id_counter += 1
    return st.session_state.next_task_id_counter

def check_login_status():
    try:
        response = requests.get('http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/is_logged_in')
        st.write("Response from login status check:", response.text)  # Debugging output
        if response.status_code == 200:
            data = response.json()
            st.write("Parsed response data:", data)  # Debugging output
            if data.get('logged_in'):
                st.session_state.user_info = data['user']
                return True
        return False
    except Exception as e:
        st.error(f"An error occurred while checking login status: {e}")
        return False

st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job \nlisting sites and saving "
    "user-defined searches. Utilizing a distributed work \nscheduler, it regularly updates the job listings database "
    "and notifies users of new \nopportunities. The application also features a user-friendly web interface for "
    "\nmanual queries and real-time results.")

# Check login status
if not st.session_state.user_info:
    st.write("User info not found in session state, checking login status...")  # Debugging output
    if not check_login_status():
        st.error("You must be logged in to use this application.")
else:
    st.write("User info found in session state:", st.session_state.user_info)  # Debugging output
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
            user_id = st.session_state.user_info['sub']  # Get the user ID
            job_search_data = {
                'task_id': next_task_id(),
                'interval': "PT1M",
                'retries': 3,
                'type': "notif",
                'user_id': user_id,  # Use the retrieved user ID
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
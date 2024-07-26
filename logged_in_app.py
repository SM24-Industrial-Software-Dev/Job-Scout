import streamlit as st
import requests
import json
import boto3
from datetime import datetime, timezone

def get_current_time() -> int:
    now = datetime.now(timezone.utc)
    return get_unix_timestamp_by_min(now)

def get_unix_timestamp_by_min(dt: datetime) -> int:
    dt = dt.replace(second=0, microsecond=0)
    return int(dt.timestamp())

# Initialize the SQS client
sqs = boto3.client('sqs', region_name='us-east-2')

queue_url = 'https://sqs.us-east-2.amazonaws.com/767397805190/refresh-queue'  # Replace with your actual SQS Queue URL

if 'next_task_id_counter' not in st.session_state:
    st.session_state.next_task_id_counter = 0

if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def next_task_id():
    st.session_state.next_task_id_counter += 1
    return st.session_state.next_task_id_counter

st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job listing sites and saving "
    "user-defined searches. Utilizing a distributed work scheduler, it regularly updates the job listings database "
    "and notifies users of new opportunities. The application also features a user-friendly web interface for "
    "manual queries and real-time results."
)

# Check if the user is logged in
query_params = st.experimental_get_query_params()
user_id = query_params.get("user_id", [None])[0]

if user_id:
    st.session_state.user_info = {"sub": user_id}
    st.write("User info found in session state:", st.session_state.user_info)
else:
    st.write("User not logged in.")

if st.session_state.user_info:
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
    
    frequency = ['', 'One-Time Instant Results', 'Every Minute (For Testing)', 'Daily', 'Biweekly', 'Weekly', 'Bimonthly', 'Monthly']
    frequencies = st.selectbox(label="How often would you like to be notified?:", options=frequency)

    login_url = "http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/login"
    logout_url = "http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/logout"

    if 'button_login_pressed' not in st.session_state:
        st.session_state.button_login_pressed = False

    def handle_button_logout_press():
        st.session_state.button_login_pressed = False
        st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)

    def convert_frequency_to_interval(frequency) -> str:
        if frequency == 'Every Minute (For Testing)':
            return "PT1M"
        elif frequency == 'Daily':
            return "P1D"
        elif frequency == 'Weekly':
            return "P7D"
        elif frequency == 'Bimonthly':
            return "P14D"
        elif frequency == 'Monthly':
            return "P30D"
        elif frequency == 'Biweekly':
            return "P3.5D"
        else:
            return "P7D"

    # Sidebar for floating menu
    with st.sidebar:
        if st.button("Logout"):
            handle_button_logout_press()

if st.button("search"):
    if job_title or location or company:
        if frequencies == 'One-Time Instant Results':
            job_search_data = {
            'title': job_title,
            'company': company,
            'location': location
            }
            try:
                # Build the URL with query parameters
                response = requests.get(
                    'http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8000/instant_search/',
                    params={
                        'role': job_title,  # Assuming job_title is used as role
                        'location': location,
                        'company': company
                    }
                )

                if response.status_code == 200:
                    # Parse the JSON response
                    results = response.json().get('results', [])
                    if not results:
                        st.write("No results found.")
                    
                    # Display the results in a formatted way
                    st.success('Search request sent! Check your results below:')
                    
                    for job in results:
                        title = job.get('title', 'N/A')
                        company = job.get('company', 'N/A')
                        location = job.get('location', 'N/A')
                        link = job.get('link', '#')
                        if title == 'No matching jobs found.':
                            st.write("Sorry, no matching jobs found. Please try another search.")
                        else:
                            st.write(f"**Title:** {title}")
                            st.write(f"**Company:** {company}")
                            st.write(f"**Location:** {location}")
                            st.markdown(f"[Link to Apply]({link})")  # Clickable link
                            st.write("---")  # Separator between jobs

                else:
                    st.error(f"Failed to add job search. Error: {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")    
        elif frequencies:
            #user_id = st.session_state.user_info['sub']
            interval = str(convert_frequency_to_interval(frequencies))
            job_search_data = {
                'task_id': next_task_id(),
                'interval': interval,
                'retries': 3,
                'created': int(get_current_time()),
                'type': "notif",
                'user_id': 1,
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
            st.error("Please choose a notification setting.")
    else:
        st.error("Please fill out a field before searching.")

import streamlit as st
import boto3
import json
import requests

# Initialize the SQS client
sqs = boto3.client('sqs', region_name='us-east-2')
queue_url = 'https://us-east-2.queue.amazonaws.com/767397805190/QueryJobsDB'  # Replace with your actual SQS Queue URL

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

if st.button("search"):
    if job_title or location or company:
        # Prepare the job search data

        ##HARDCODED RIGHT NOW -- NEED TO UPDATE
        job_search_data = {
            'task_id': 1,  # Example task_id, adjust as necessary
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

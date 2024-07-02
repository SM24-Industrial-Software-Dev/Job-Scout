import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Streamlit app title and description
st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job "
    "listing sites and saving user-defined searches. Utilizing a distributed work "
    "scheduler, it regularly updates the job listings database and notifies users of new "
    "opportunities. The application also features a user-friendly web interface for "
    "manual queries and real-time results."
)

# User inputs
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

# Search button
if st.button("search"):
    # if not job_title or not location:
    #     st.error("Please fill out both Job Title and Location.")
    # else:
    #     # DynamoDB read operation
    #     try:
    #         dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    #         table = dynamodb.Table('Jobs')  # Using the 'Jobs' table name
    #
    #         # Define a filter expression based on user inputs
    #         filter_expression = []
    #         if job_title:
    #             filter_expression.append(f"contains(title, :job_title)")
    #         if location:
    #             filter_expression.append(f"contains(location, :location)")
    #         if company:
    #             filter_expression.append(f"contains(company, :company)")
    #
    #         filter_expression = " and ".join(filter_expression)
    #
    #         expression_attribute_values = {
    #             ':job_title': job_title,
    #             ':location': location,
    #             ':company': company,
    #         }
    #
    #         response = table.scan(
    #             FilterExpression=filter_expression,
    #             ExpressionAttributeValues=expression_attribute_values
    #         )
    #
    #         items = response.get('Items', [])
    #
    #         if items:
    #             st.write("Job Listings found:")
    #             for item in items:
    #                 st.write(item)
    #         else:
    #             st.write("No job listings found.")
    #     except NoCredentialsError:
    #         st.error("No AWS credentials found.")
    #     except PartialCredentialsError:
    #         st.error("Incomplete AWS credentials.")
    #     except Exception as e:
    #         st.error(f"An error occurred: {e}")

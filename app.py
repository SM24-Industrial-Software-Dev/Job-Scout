import streamlit as st

st.title("JobScout")
st.text(
    "JobScout is a web application that simplifies job searching by querying multiple job \nlisting sites and saving "
    "user-defined searches. Utilizing a distributed work \nscheduler, it regularly updates the job listings database "
    "and notifies users of new \nopportunities. The application also features a user-friendly web interface for "
    "\nmanual queries and real-time results.")

job_title = st.text_input("Job Title:") # can add default value
location = st.text_input("Location:") # can add default value
company = st.text_input("Company:") # can add default value


### GET GOOGLE SSO INTEGRATED WITH STREAMLIT - https://discuss.streamlit.io/t/google-authentication-in-a-streamlit-app/43252 ###
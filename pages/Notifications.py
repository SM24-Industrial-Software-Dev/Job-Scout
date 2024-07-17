import streamlit as st

notifications = ['', 'never', 'hourly', 'daily', 'weekly']
notification_frequency = st.selectbox(label="Select how often you would like to be notified of new job listings:",
                                      options=notifications)

if st.button("apply") and len(notification_frequency) > 1:
    st.success('Your notification setting have successfully been updated!')

# user setting should be updated in database, and maybe we should send an email to the user as well

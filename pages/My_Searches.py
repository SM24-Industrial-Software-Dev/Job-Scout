import streamlit as st
import pandas as pd

# Define the initial DataFrame
df = pd.DataFrame(
    [
        {"job_title": "Software Engineer", "location": "New York", "company": "TechCorp", "date_of_search": "2024-07-01", "notification_frequency": "never"},
        {"job_title": "Data Scientist", "location": "San Francisco", "company": "DataInc", "date_of_search": "2024-07-02", "notification_frequency": "never"},
        {"job_title": "Product Manager", "location": "Chicago", "company": "ProductCo", "date_of_search": "2024-07-03", "notification_frequency": "never"},
    ]
)

# Define the notification options
notifications = ['', 'never', 'hourly', 'daily', 'weekly']

# Store selected values in a dictionary
selected_notifications = {}

# Display the table headers
cols = st.columns(5)
cols[0].write("Job Title")
cols[1].write("Location")
cols[2].write("Company")
cols[3].write("Date of Search")
cols[4].write("Notification Frequency")

# Display each row with input elements
for index, row in df.iterrows():
    cols = st.columns(5)
    cols[0].write(row["job_title"])
    cols[1].write(row["location"])
    cols[2].write(row["company"])
    cols[3].write(row["date_of_search"])
    selected_notifications[index] = cols[4].selectbox(
        f"Notification frequency for row {index}",
        options=notifications,
        index=notifications.index(row["notification_frequency"]) if row["notification_frequency"] in notifications else 0,
        key=f"notification_{index}"
    )

# Button to apply changes
if st.button("apply"):
    # Update the DataFrame with the selected notification frequencies
    for index in selected_notifications:
        df.at[index, "notification_frequency"] = selected_notifications[index]
    st.success('Your notification settings have successfully been updated!')

# Display the updated DataFrame
st.dataframe(df)

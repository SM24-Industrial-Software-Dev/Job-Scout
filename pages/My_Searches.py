import streamlit as st
import pandas as pd

# Define the initial DataFrame
df = pd.DataFrame(
    [
        {"command": "st.selectbox", "rating": 4, "is_widget": False, "notification_frequency": "never"},
        {"command": "st.balloons", "rating": 5, "is_widget": False, "notification_frequency": "never"},
        {"command": "st.time_input", "rating": 3, "is_widget": False, "notification_frequency": "never"},
    ]
)

# Define the notification options
notifications = ['', 'never', 'hourly', 'daily', 'weekly']

# Store selected values in a dictionary
selected_notifications = {}

# Display the table headers
cols = st.columns(4)
cols[0].write("Command")
cols[1].write("Rating")
cols[2].write("Is Widget")
cols[3].write("Notification Frequency")

# Display each row with input elements
for index, row in df.iterrows():
    cols = st.columns(4)
    cols[0].write(row["command"])
    cols[1].write(row["rating"])
    cols[2].write(row["is_widget"])
    selected_notifications[index] = cols[3].selectbox(
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
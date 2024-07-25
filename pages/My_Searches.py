# import streamlit as st
#
# st.table(data=None)

import streamlit as st
import pandas as pd

# Initialize session state for the DataFrame
if 'df' not in st.session_state:
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David'],
        'Age': [24, 27, 22, 32],
        'Occupation': ['Engineer', 'Doctor', 'Artist', 'Lawyer']
    }
    st.session_state.df = pd.DataFrame(data)


# Function to display the table with deletion checkboxes
def display_table():
    st.write("### Table with Deletion Checkboxes")

    # Create a column for checkboxes
    for idx in range(len(st.session_state.df)):
        st.session_state.df.at[idx, 'Delete'] = st.checkbox(
            label="", key=f"delete_{idx}", value=False
        )

    # Display the DataFrame
    st.table(st.session_state.df.drop(columns=['Delete']))


# Function to delete selected rows
def delete_rows():
    st.session_state.df = st.session_state.df[st.session_state.df['Delete'] == False]
    st.session_state.df.drop(columns=['Delete'], inplace=True)


# Display initial table
display_table()

# Button to delete selected rows
if st.button("Delete Selected Rows"):
    delete_rows()
    st.experimental_rerun()

# Display updated table
st.write("### Updated Table")
st.table(st.session_state.df)

# Inspired by GitHub: linkedin-jobs-webscraping/Linkedin_Scraper_Tutorial.ipynb


# Import dependencies
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd

title = "Python Developer"  # Job title
location = "New York"  # Job location
start = 0  # Starting point for pagination
# Construct the URL for LinkedIn job search
list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"

# Send a GET request to the URL and store the response
response = requests.get(list_url)

# Get the HTML, parse the response and find all list items(jobs postings)
list_data = response.text
list_soup = BeautifulSoup(list_data, "html.parser")
page_jobs = list_soup.find_all("li")

# Create an empty list to store the job postings
id_list = []
# Itetrate through job postings to find job ids
for job in page_jobs:
    base_card_div = job.find("div", {"class": "base-card"})
    job_id = base_card_div.get("data-entity-urn").split(":")[3]
    print(job_id)
    id_list.append(job_id)

# Initialize an empty list to store job information
job_list = []

# Loop through the list of job IDs and get each URL
for job_id in id_list:
    # Construct the URL for each job using the job ID
    job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

    # Send a GET request to the job URL and parse the reponse
    job_response = requests.get(job_url)
    print(job_response.status_code)
    job_soup = BeautifulSoup(job_response.text, "html.parser")

    # Create a dictionary to store job details
    job_post = {}

    # Try to extract and store the job title
    try:
        job_post["job_title"] = job_soup.find("h2", {
            "class": "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip()
    except:
        job_post["job_title"] = None

    # Try to extract and store the company name
    try:
        job_post["company_name"] = job_soup.find("a", {
            "class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
    except:
        job_post["company_name"] = None

    # Try to extract and store the time posted
    try:
        job_post["time_posted"] = job_soup.find("span", {
            "class": "posted-time-ago__text topcard__flavor--metadata"}).text.strip()
    except:
        job_post["time_posted"] = None

    # Try to extract and store the number of applicants
    try:
        job_post["num_applicants"] = job_soup.find("span", {
            "class": "num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet"}).text.strip()
    except:
        job_post["num_applicants"] = None

    # Append the job details to the job_list
    job_list.append(job_post)

#Check if the list contains all the desired data
job_list

# Create a pandas DataFrame using the list of job dictionaries 'job_list'
jobs_df = pd.DataFrame(job_list)
print(jobs_df.to_string())

#Save data to CSV file
# jobs_df.to_csv('New_York_Python_Developer.csv', index = False)
import json
import requests
from bs4 import BeautifulSoup
import time
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

data = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Jobs')

job_counter = 0

class Job(BaseModel):
    job_id: str
    title: str
    company: str
    location: str
    description: Optional[str] = 'N/A'

app = FastAPI()

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    try:
        response = table.get_item(Key={'job_id': job_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Job not found")
        return response['Item']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/jobs/{job_id}")
async def update_job(job_id: str, job: Job):
    try:
        response = table.update_item(
            Key={'job_id': job_id},
            UpdateExpression="set #t=:t, #c=:c, #l=:l, description=:d",
            ExpressionAttributeNames={
                '#t': 'title',
                '#c': 'company',
                '#l': 'location'
            },
            ExpressionAttributeValues={
                ':t': job.title,
                ':c': job.company,
                ':l': job.location,
                ':d': job.description
            },
            ReturnValues="UPDATED_NEW"
        )
        return response['Attributes']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    try:
        response = table.delete_item(Key={'job_id': job_id})
        return {"message": "Job deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def linkedin_scraper(job_title, location, page_number):
    global job_counter
    base_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job_title}&location={location}&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0&start='
    formatted_url = base_url.format(job_title=job_title.replace(' ', '%20'), location=location.replace(' ', '%20'))
    next_page = formatted_url + str(page_number)
    print(f"Scraping URL: {next_page}")

    response = requests.get(next_page, headers=headers, verify=False)

    if response.status_code != 200:
        print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    jobs = soup.find_all('div', class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')

    if not jobs:
        print(f"No jobs found on page {page_number}. Ending scrape.")
        return

    for job in jobs:
        job_title = job.find('h3', class_='base-search-card__title').text.strip()
        job_company = job.find('h4', class_='base-search-card__subtitle').text.strip()
        job_location = job.find('span', class_='job-search-card__location').text.strip()
        job_link = job.find('a', class_='base-card__full-link')['href']

        job_counter += 1
        
        job_id = job_counter  # Assuming the job_id can be extracted from the URL

        job_data = {
            'job_id': str(job_id),
            'title': job_title,
            'company': job_company,
            'location': job_location,
            'description': 'N/A'  # Description is not scraped, set a default value
        }

        # Save job data to DynamoDB
        try:
            table.put_item(Item=job_data)
            print(f"Inserted job {job_id} into DynamoDB")
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Failed to insert job {job_id} into DynamoDB: {str(e)}")

    print(f"Data updated with {len(jobs)} jobs from page {page_number}")

    if len(jobs) == 0 or page_number >= 100:
        with open('linkedin-jobs.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print('File closed')
        return

    # Adding a delay to avoid hitting the server too quickly
    time.sleep(1)

    linkedin_scraper(job_title, location, page_number + 25)

# User inputs for job title and location
job_title_input = input("Enter the job title: ")
location_input = input("Enter the location: ")

linkedin_scraper(job_title_input, location_input, 0)
import json
import requests
from bs4 import BeautifulSoup
import time

data = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def linkedin_scraper(job_title, location, page_number):
    base_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={job_title}&location={location}&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0&start='
    formatted_url = base_url.format(job_title=job_title.replace(' ', '%20'), location=location.replace(' ', '%20'))
    next_page = formatted_url + str(page_number)
    print(f"Scraping URL: {next_page}")

    response = requests.get(next_page, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    jobs = soup.find_all('div',
                         class_='base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')

    if not jobs:
        print(f"No jobs found on page {page_number}. Ending scrape.")
        return

    for job in jobs:
        job_title = job.find('h3', class_='base-search-card__title').text.strip()
        job_company = job.find('h4', class_='base-search-card__subtitle').text.strip()
        job_location = job.find('span', class_='job-search-card__location').text.strip()
        job_link = job.find('a', class_='base-card__full-link')['href']

        data.append({
            'Title': job_title,
            'Company': job_company,
            'Location': job_location,
            'Apply': job_link
        })

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

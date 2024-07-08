import requests
import json

# Use your actual Coresignal API key
API_KEY = 'eyJhbGciOiJFZERTQSIsImtpZCI6ImY3MDYzYTcyLWUxYjctYzA0OC05ZTM2LTlkODNkMzFmNDQzNCJ9.eyJhdWQiOiJtYWlsLnl1LmVkdSIsImV4cCI6MTc0OTE2MjA2NSwiaWF0IjoxNzE3NjA1MTEzLCJpc3MiOiJodHRwczovL29wcy5jb3Jlc2lnbmFsLmNvbTo4MzAwL3YxL2lkZW50aXR5L29pZGMiLCJuYW1lc3BhY2UiOiJyb290IiwicHJlZmVycmVkX3VzZXJuYW1lIjoibWFpbC55dS5lZHUiLCJzdWIiOiJmYTBjNGM5Yy1jMjFjLWZmZGYtYzBiOS00OGFlZDVhZjljMTYiLCJ1c2VyaW5mbyI6eyJzY29wZXMiOiJjZGFwaSJ9fQ.yJy2y1ny2VQyWQK-40PBwage72zOWTdAdi-fDwpUVzPvH2CDT9jFetBzZ7tCCNfbZ1Ednls9_4IYUrNSo_beAw'

# Placeholder endpoint, replace with the actual endpoint from Coresignal's API documentation
ENDPOINT = 'https://api.coresignal.com/v1/linkedin/jobs'

def fetch_linkedin_jobs(query, location, num_jobs):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
    }

    jobs = []
    page = 0
    per_page = 100  # Adjust as per the API's maximum page size

    while len(jobs) < num_jobs:
        params = {
            'query': query,
            'location': location,
            'page': page,
            'per_page': per_page,
        }

        response = requests.get(ENDPOINT, headers=headers, params=params)
        if response.status_code == 401:
            print("Error: Unauthorized. Please check your API key.")
            break
        elif response.status_code == 404:
            print("Error: Endpoint not found. Please check the API endpoint.")
            break
        elif response.status_code != 200:
            print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
            break

        response_data = response.json()
        if 'data' not in response_data:
            print(f"Unexpected response structure: {response_data}")
            break

        results = response_data['data']
        if not results:
            print("No more job listings found.")
            break

        for job in results:
            job_data = {
                'Title': job.get('title'),
                'Company': job.get('company_name'),
                'Location': job.get('location'),
                'Apply': job.get('url')
            }
            jobs.append(job_data)

        print(f"Fetched {len(results)} jobs from page {page}")
        page += 1

    return jobs[:num_jobs]

def main():
    query = input("Enter the job title: ")
    location = input("Enter the location: ")
    num_jobs = 1000  # You can adjust this number as needed

    jobs = fetch_linkedin_jobs(query, location, num_jobs)

    if jobs:
        # Save the jobs to a JSON file
        with open('linkedin_jobs.json', 'w', encoding='utf-8') as json_file:
            json.dump(jobs, json_file, ensure_ascii=False, indent=4)
        print(f"Saved {len(jobs)} job listings to linkedin_jobs.json")
    else:
        print("No job listings found.")

if __name__ == "__main__":
    main()

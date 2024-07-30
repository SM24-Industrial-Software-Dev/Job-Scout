import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from jobspy import scrape_jobs

class JobScraper:
    def __init__(self, region_name='us-east-2', table_name='Jobs'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.jobs = None

    def scrape_jobs(self):
        # Hardcoded parameters
        site_names = ["indeed", "linkedin", "zip_recruiter", "glassdoor"]
        search_term = ""  # Broad search
        location = ""     # Broad search
        results_wanted = 20
        hours_old = 72
        country_indeed = 'USA'
        proxies = None  # No proxies by default

        self.jobs = scrape_jobs(
            site_name=site_names,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed=country_indeed,
            proxies=proxies
        )
        self.save_jobs_to_db()
        return self.jobs

    def save_jobs_to_db(self):
        if self.jobs is not None:
            job_counter = 1
            for job in self.jobs:
                if isinstance(job, dict):  # Ensure job is a dictionary
                    item = {
                        'job_id': str(job_counter),  # Generate unique job_id
                        'title': job.get('job_title', 'N/A'),
                        'company': job.get('company', 'N/A'),
                        'location': job.get('location', 'N/A'),
                        'link': job.get('job_link', 'N/A'),
                        'description': job.get('job_description', 'N/A')
                    }
                    try:
                        self.table.put_item(Item=item)
                        print(f"Added job {item['job_id']} to DynamoDB")
                        job_counter += 1  # Increment the job counter
                    except (NoCredentialsError, PartialCredentialsError) as e:
                        print(f"Credentials error: {str(e)}")
                    except Exception as e:
                        print(f"Error adding job {item['job_id']} to DynamoDB: {str(e)}")

    def save_jobs_to_json(self, file_path):
        if self.jobs is not None:
            jobs_json = self.jobs.to_json(orient='records', lines=True)
            with open(file_path, "w") as file:
                file.write(jobs_json)

if __name__ == "__main__":
    scraper = JobScraper()
    scraper.scrape_jobs()
    scraper.save_jobs_to_json("jobs.json")




# import json
# import boto3
# from botocore.exceptions import NoCredentialsError, PartialCredentialsError
# from jobspy import scrape_jobs
#
# class JobScraper:
#     def __init__(self, region_name='us-east-2', table_name='Jobs'):
#         self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
#         self.table = self.dynamodb.Table(table_name)
#         self.jobs = None
#
#     def scrape_jobs(self):
#         # Hardcoded parameters
#         site_names = ["indeed", "linkedin", "zip_recruiter", "glassdoor"]
#         search_term = ""  # Broad search
#         location = ""     # Broad search
#         results_wanted = 20
#         hours_old = 72
#         country_indeed = 'USA'
#         proxies = None  # No proxies by default
#
#         self.jobs = scrape_jobs(
#             site_name=site_names,
#             search_term=search_term,
#             location=location,
#             results_wanted=results_wanted,
#             hours_old=hours_old,
#             country_indeed=country_indeed,
#             proxies=proxies
#         )
#         self.save_jobs_to_db()
#         return self.jobs
#
#     def save_jobs_to_db(self):
#         # if self.jobs is not None:
#         #     for job in self.jobs:
#         #         item = {
#         #             'job_id': job.get('job_id', 'N/A'),
#         #             'title': job.get('job_title', 'N/A'),
#         #             'company': job.get('company', 'N/A'),
#         #             'location': job.get('location', 'N/A'),
#         #             'PostDate': job.get('post_date', 'N/A'),
#         #             'description': job.get('job_description', 'N/A'),
#         #             'link': job.get('job_link', 'N/A')
#         #         }
#         #         try:
#         #             self.table.put_item(Item=item)
#         #             print(f"Added job {item['JobID']} to DynamoDB")
#         #         except (NoCredentialsError, PartialCredentialsError) as e:
#         #             print(f"Credentials error: {str(e)}")
#         #         except Exception as e:
#         #             print(f"Error adding job {item['JobID']} to DynamoDB: {str(e)}")
#         #
#         job_counter = 1
#         for job in self.jobs:
#             job_title = job.find('h3', class_='base-search-card__title').text.strip()
#             job_company = job.find('h4', class_='base-search-card__subtitle').text.strip()
#             job_location = job.find('span', class_='job-search-card__location').text.strip()
#             job_link = job.find('a', class_='base-card__full-link')['href']
#
#             job_counter += 1
#
#             job_data = {
#                 'job_id': int(job_counter),
#                 'title': job_title,
#                 'company': job_company,
#                 'location': job_location,
#                 'link': job_link,
#                 'description': 'N/A'  # Description is not scraped, set a default value
#             }
#
#             # Save job data to DynamoDB
#             try:
#                 self.table.put_item(Item=job_data)
#                 print(f"Inserted job {job_counter} into DynamoDB")
#             except (NoCredentialsError, PartialCredentialsError) as e:
#                 print(f"Failed to insert job {job_counter} into DynamoDB: {str(e)}")
#
#     def save_jobs_to_json(self, file_path):
#         if self.jobs is not None:
#             jobs_json = self.jobs.to_json(orient='records', lines=True)
#             with open(file_path, "w") as file:
#                 file.write(jobs_json)
#
# # Usage
# scraper = JobScraper()
# scraper.scrape_jobs()
# scraper.print_summary()
# scraper.save_jobs_to_json("jobs.json")


# import json
# from jobspy import scrape_jobs
#
# class JobScraper:
#     def __init__(self):
#         self.jobs = None
#
#     def scrape_jobs(self):
#         # Hardcoded parameters
#         site_names = ["indeed", "linkedin", "zip_recruiter", "glassdoor"]
#         search_term = ""  # Broad search
#         location = ""     # Broad search
#         results_wanted = 20
#         hours_old = 72
#         country_indeed = 'USA'
#         proxies = None  # No proxies by default
#
#         self.jobs = scrape_jobs(
#             site_name=site_names,
#             search_term=search_term,
#             location=location,
#             results_wanted=results_wanted,
#             hours_old=hours_old,
#             country_indeed=country_indeed,
#             proxies=proxies
#         )
#         return self.jobs
#
#     def save_jobs_to_json(self, file_path):
#         if self.jobs is not None:
#             jobs_json = self.jobs.to_json(orient='records', lines=True)
#             with open(file_path, "w") as file:
#                 file.write(jobs_json)
#             return f"Jobs saved to {file_path}"
#         else:
#             return "No jobs to save. Please scrape jobs first."
#
#     def print_summary(self):
#         if self.jobs is not None:
#             print(f"Found {len(self.jobs)} jobs")
#             print(self.jobs.head())
#         else:
#             print("No jobs to display. Please scrape jobs first.")
#
# # Usage
# scraper = JobScraper()
# scraper.scrape_jobs()
# scraper.print_summary()
# scraper.save_jobs_to_json("jobs.json")

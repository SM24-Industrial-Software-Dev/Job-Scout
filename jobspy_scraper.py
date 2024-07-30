import json
import boto3
from decimal import Decimal
import pandas as pd
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
        location = ""  # Broad search
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
        return self.jobs

    def save_jobs_to_json(self, file_path):
        if self.jobs is not None:
            jobs_json = self.jobs.to_json(orient='records', lines=True)
            with open(file_path, "w") as file:
                file.write(jobs_json)
            return f"Jobs saved to {file_path}"
        else:
            return "No jobs to save. Please scrape jobs first."

    def save_jobs_to_dynamodb(self):
        if self.jobs is not None:
            print("Columns in jobs DataFrame:", self.jobs.columns)

            # Replace NaN with None
            self.jobs = self.jobs.where(pd.notnull(self.jobs), None)

            with self.table.batch_writer() as batch:
                for index, job in self.jobs.iterrows():
                    item = {
                        'job_id': str(index),
                        'title': job['title'] or 'N/A',
                        'company': job['company'] or 'N/A',
                        'location': job['location'] or 'N/A',
                        'description': job.get('description', 'N/A'),  # Use get to handle missing keys
                        'link': job.get('job_url', 'N/A')  # Use get to handle missing keys
                    }
                    # Convert all numerical values to Decimal and handle None values
                    for key, value in item.items():
                        if isinstance(value, float):
                            item[key] = Decimal(str(value))
                        elif value is None:
                            item[key] = 'N/A'

                    print(f"Putting item into DynamoDB: {item}")  # Debugging line to check item structure

                    batch.put_item(Item=item)
            return "Jobs saved to DynamoDB"
        else:
            return "No jobs to save. Please scrape jobs first."

    def print_summary(self):
        if self.jobs is not None:
            print(f"Found {len(self.jobs)} jobs")
            print(self.jobs.head())
        else:
            print("No jobs to display. Please scrape jobs first.")

    def describe_table(self):
        try:
            response = self.table.meta.client.describe_table(TableName=self.table.name)
            print(json.dumps(response, indent=4, default=str))
        except Exception as e:
            print(f"Error describing table: {e}")


# Usage
scraper = JobScraper()
scraper.describe_table()  # Print the table schema for debugging
scraper.scrape_jobs()
scraper.print_summary()
scraper.save_jobs_to_json("jobs.json")
print(scraper.save_jobs_to_dynamodb())

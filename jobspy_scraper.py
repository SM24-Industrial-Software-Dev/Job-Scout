import json
from jobspy import scrape_jobs

<<<<<<< HEAD
class JobScraper:
    def __init__(self):
        self.jobs = None
=======
# Scrape jobs from different sites
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term="",
    location="",
    results_wanted=20,
    hours_old=72,  # (only Linkedin/Indeed is hour specific, others round up to days old)
    country_indeed='USA',  # only needed for indeed / glassdoor
>>>>>>> f2e5dd5ab7c79cfa0523c2ce111a9e7bb6aa8f5c

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
        return self.jobs

    def save_jobs_to_json(self, file_path):
        if self.jobs is not None:
            jobs_json = self.jobs.to_json(orient='records', lines=True)
            with open(file_path, "w") as file:
                file.write(jobs_json)
            return f"Jobs saved to {file_path}"
        else:
            return "No jobs to save. Please scrape jobs first."

    def print_summary(self):
        if self.jobs is not None:
            print(f"Found {len(self.jobs)} jobs")
            print(self.jobs.head())
        else:
            print("No jobs to display. Please scrape jobs first.")

# Usage
scraper = JobScraper()
scraper.scrape_jobs()
scraper.print_summary()
scraper.save_jobs_to_json("jobs.json")

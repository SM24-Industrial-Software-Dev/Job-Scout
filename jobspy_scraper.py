from jobspy import scrape_jobs

# Scrape jobs from different sites
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term="software engineer",
    location="Dallas, TX",
    results_wanted=20,
    hours_old=72,  # (only Linkedin/Indeed is hour specific, others round up to days old)
    country_indeed='USA',  # only needed for indeed / glassdoor

    # linkedin_fetch_description=True # get full description and direct job url for linkedin (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)

print(f"Found {len(jobs)} jobs")
print(jobs.head())

# Convert jobs DataFrame to JSON and save to a file
jobs_json = jobs.to_json(orient='records', lines=True)

with open("jobs.json", "w") as file:
    file.write(jobs_json)

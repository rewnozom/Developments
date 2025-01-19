import json
import re

# Path to the markdown file containing job listings
input_file_path = "./output/jobs.md"

# Output files
job_applications_file = "job_applications.json"
completed_job_applications_file = "completed_job_applications.json"

# Initialize data structures
job_applications = []
completed_job_applications = []

# Regex patterns to extract job information
job_pattern = re.compile(r"## \[(.+?)\]\((.+?)\)")
score_pattern = re.compile(r"\*\*Score:\*\* (\d+)")
company_pattern = re.compile(r"\*\*Company:\*\* (.+?)  ")
location_pattern = re.compile(r"\*\*Location:\*\* (.+?)  ")
posted_pattern = re.compile(r"\*\*Posted:\*\* (.+?)  ")
found_pattern = re.compile(r"\*\*Found:\*\* (.+?)  ")
description_pattern = re.compile(r"### Description\n(.+?)\n---", re.DOTALL)

# Read the markdown file
with open(input_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Extract job data
jobs = content.split("---")
for job in jobs:
    job_data = {}
    
    job_match = job_pattern.search(job)
    if job_match:
        job_data["title"] = job_match.group(1)
        job_data["url"] = job_match.group(2)
    
    score_match = score_pattern.search(job)
    if score_match:
        job_data["score"] = int(score_match.group(1))
    
    company_match = company_pattern.search(job)
    if company_match:
        job_data["company"] = company_match.group(1)
    
    location_match = location_pattern.search(job)
    if location_match:
        job_data["location"] = location_match.group(1)
    
    posted_match = posted_pattern.search(job)
    if posted_match:
        job_data["posted"] = posted_match.group(1)
    
    found_match = found_pattern.search(job)
    if found_match:
        job_data["found"] = found_match.group(1)
    
    description_match = description_pattern.search(job)
    if description_match:
        job_data["description"] = description_match.group(1).strip()
    
    if job_data:
        job_applications.append(job_data)

# Write the extracted jobs to a JSON file
with open(job_applications_file, 'w', encoding='utf-8') as file:
    json.dump(job_applications, file, ensure_ascii=False, indent=2)

# Initialize completed applications file if not present
try:
    with open(completed_job_applications_file, 'r', encoding='utf-8') as file:
        completed_job_applications = json.load(file)
except FileNotFoundError:
    with open(completed_job_applications_file, 'w', encoding='utf-8') as file:
        json.dump([], file, ensure_ascii=False, indent=2)

# Display the extracted data to ensure correctness
import ace_tools as tools; tools.display_dataframe_to_user(name="Extracted Job Applications", dataframe=json.dumps(job_applications))

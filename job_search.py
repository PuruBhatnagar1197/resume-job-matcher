import requests
import os

def search_jobs_rapidapi_post(keywords, location, job_type, results_wanted=10):
    url = "https://jobs-search-api.p.rapidapi.com/getjobs"
    payload = {
        "search_term": " ".join(keywords) if isinstance(keywords, list) else str(keywords),
        "location": location,
        "results_wanted": results_wanted,
        "site_name": ["indeed", "linkedin", "zip_recruiter", "glassdoor"],
        "distance": 50,
        "job_type": job_type.lower(),
        "is_remote": location.lower() == "remote",
        "linkedin_fetch_description": False,
        "hours_old": 72
    }
    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "jobs-search-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    print(headers, payload)
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("jobs", [])
    else:
        return []

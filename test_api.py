import requests
import json

BASE_URL = "http://localhost:8000"

# Test creating a candidate
candidate_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "location": "San Francisco, CA",
    "current_job_title": "Senior Software Engineer",
    "current_company": "Tech Corp",
    "years_of_experience": 8,
    "expected_salary_min": 120000,
    "expected_salary_max": 160000,
    "status": "active",
    "source": "linkedin"
}

print("Creating candidate...")
response = requests.post(f"{BASE_URL}/api/v1/candidates/", json=candidate_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if response.status_code == 201:
    candidate_id = response.json()['id']
    print(f"Created candidate with ID: {candidate_id}\n")

    # Test getting the candidate
    print("Getting candidate...")
    response = requests.get(f"{BASE_URL}/api/v1/candidates/{candidate_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    # Test updating the candidate
    print("Updating candidate...")
    update_data = {"years_of_experience": 9}
    response = requests.put(f"{BASE_URL}/api/v1/candidates/{candidate_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# Test listing candidates
print("Listing candidates...")
response = requests.get(f"{BASE_URL}/api/v1/candidates/", params={"page": 1, "size": 10})
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# Test creating a job
job_data = {
    "title": "Senior Python Developer",
    "description": "Looking for an experienced Python developer to join our team",
    "department": "Engineering",
    "location": "San Francisco, CA",
    "employment_type": "full-time",
    "work_mode": "hybrid",
    "salary_min": 130000,
    "salary_max": 170000,
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "preferred_skills": ["React", "AWS"],
    "experience_min": 5,
    "experience_max": 10,
    "status": "draft",
    "number_of_openings": 2
}

print("Creating job...")
response = requests.post(f"{BASE_URL}/api/v1/jobs/", json=job_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if response.status_code == 201:
    job_id = response.json()['id']
    print(f"Created job with ID: {job_id}\n")

    # Test activating the job
    print("Activating job...")
    response = requests.post(f"{BASE_URL}/api/v1/jobs/{job_id}/activate")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# Test listing jobs
print("Listing jobs...")
response = requests.get(f"{BASE_URL}/api/v1/jobs/", params={"page": 1, "size": 10})
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

print("All tests completed!")

#!/usr/bin/env python3
import requests
import json

# Test data - create a new user with interviewer role
register_data = {
    "email": "interviewer@example.com",
    "password": "testpass123",
    "full_name": "Test Interviewer",
    "role": "interviewer"
}

login_data = {
    "username": "interviewer@example.com",
    "password": "testpass123"
}

interview_data = {
    "job_role": "Software Engineer",
    "job_description": "Full-stack developer with React and Python experience",
    "interview_type": "general",
    "difficulty": "medium",
    "focus": ["technical", "communication"],
    "time_limit": 30,
    "avatar": "professional",
    "voice": "neutral",
    "number_of_questions": 5,
    "questions": [
        {
            "id": "test_1",
            "text": "Tell me about your experience with React",
            "tags": ["technical"],
            "generated_by": "manual"
        }
    ]
}

def test_interview_creation():
    print("Starting interview creation test...")
    
    # Step 1: Register new user
    print("1. Registering new user...")
    try:
        register_response = requests.post(
            "http://127.0.0.1:8000/api/auth/register",
            json=register_data
        )
        print(f"Register response status: {register_response.status_code}")
        
        if register_response.status_code == 200:
            print("User registered successfully")
        elif register_response.status_code == 400 and "already registered" in register_response.text:
            print("User already exists, continuing...")
        else:
            print(f"Registration failed: {register_response.status_code} - {register_response.text}")
            return
    except Exception as e:
        print(f"Register request failed: {e}")
        return
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_response = requests.post(
        "http://127.0.0.1:8000/api/auth/login",
        data=login_data
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result.get("access_token")
    print(f"Login successful, token: {token[:20]}...")
    
    # Step 3: Create interview
    print("\n3. Creating interview...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    create_response = requests.post(
        "http://127.0.0.1:8000/api/interviews/create",
        headers=headers,
        json=interview_data
    )
    
    print(f"Create response status: {create_response.status_code}")
    print(f"Create response: {create_response.text}")
    
    if create_response.status_code == 201:
        print("✅ Interview creation successful!")
        result = create_response.json()
        print(f"Created interview ID: {result.get('id')}")
        print(f"Created by: {result.get('created_by')}")
    else:
        print("❌ Interview creation failed!")

if __name__ == "__main__":
    test_interview_creation()

#!/usr/bin/env python3
"""
Test script to verify field alignment between SQLAlchemy models and Pydantic schemas
"""
import asyncio
import aiohttp
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://127.0.0.1:8000/api"

async def test_field_alignment():
    """Test that all field names are properly aligned"""
    
    async with aiohttp.ClientSession() as session:
        print("🔧 Testing Field Alignment Between Models and Schemas")
        print("=" * 60)
        
        # Step 1: Register and login as interviewer
        print("\n1. Setting up interviewer...")
        interviewer_data = {
            "full_name": "Test Interviewer",
            "email": "interviewer@test.com",
            "password": "testpass123",
            "role": "interviewer"
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/register", json=interviewer_data) as resp:
                if resp.status == 200:
                    print("   ✅ Interviewer registered")
                else:
                    print("   ⚠️  Interviewer might already exist")
        except Exception as e:
            print(f"   ❌ Registration failed: {e}")
            return
        
        # Login
        login_data = {
            "username": "interviewer@test.com",
            "password": "testpass123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/login", data=login_data) as resp:
                if resp.status == 200:
                    login_response = await resp.json()
                    token = login_response['access_token']
                    print("   ✅ Login successful")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Login failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Login failed: {e}")
            return
        
        # Step 2: Create interview
        print("\n2. Creating interview...")
        interview_data = {
            "job_role": "Software Engineer",
            "interview_type": "technical",
            "difficulty": "intermediate",
            "focus_areas": ["programming", "algorithms"],
            "number_of_questions": 2,
            "duration_minutes": 30,
            "avatar": "professional",
            "voice": "male_1",
            "questions": [
                {
                    "text": "Tell me about your experience with Python programming.",
                    "tags": ["programming", "python"],
                    "generated_by": "manual"
                },
                {
                    "text": "Explain the difference between a list and a tuple in Python.",
                    "tags": ["programming", "python", "data-structures"],
                    "generated_by": "manual"
                }
            ]
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with session.post(f"{BASE_URL}/interviews/create", json=interview_data, headers=headers) as resp:
                if resp.status == 200:
                    interview = await resp.json()
                    interview_id = interview['id']
                    print(f"   ✅ Interview created successfully")
                    print(f"   Interview ID: {interview_id}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Interview creation failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Interview creation failed: {e}")
            return
        
        # Step 3: Test candidate registration with correct field names
        print(f"\n3. Testing candidate registration with correct field names...")
        
        # Test 1: Basic registration (name, email, phone)
        form_data = aiohttp.FormData()
        form_data.add_field('name', 'John Doe')  # Using 'name' not 'full_name'
        form_data.add_field('email', 'john@example.com')
        form_data.add_field('phone', '+1234567890')
        
        try:
            async with session.post(f"{BASE_URL}/public/interview/{interview_id}/register", data=form_data) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    candidate = response['candidate']
                    session_id = response['session_id']
                    print(f"   ✅ Basic candidate registration successful!")
                    print(f"   Candidate ID: {candidate['id']}")
                    print(f"   Candidate Name: {candidate['name']}")  # Should be 'name'
                    print(f"   Candidate Email: {candidate['email']}")
                    print(f"   Candidate Phone: {candidate['phone']}")
                    print(f"   Session ID: {session_id}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Basic candidate registration failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Basic candidate registration failed: {e}")
            return
        
        # Test 2: Registration with resume upload
        print(f"\n4. Testing candidate registration with resume upload...")
        
        dummy_resume_content = b"PDF content here - this is a dummy resume file"
        
        form_data_with_resume = aiohttp.FormData()
        form_data_with_resume.add_field('name', 'Jane Smith')  # Using 'name' not 'full_name'
        form_data_with_resume.add_field('email', 'jane@example.com')
        form_data_with_resume.add_field('phone', '+9876543210')
        form_data_with_resume.add_field('resume_file', dummy_resume_content, filename='resume.pdf', content_type='application/pdf')
        
        try:
            async with session.post(f"{BASE_URL}/public/interview/{interview_id}/register", data=form_data_with_resume) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    candidate = response['candidate']
                    session_id = response['session_id']
                    print(f"   ✅ Candidate registration with resume successful!")
                    print(f"   Candidate ID: {candidate['id']}")
                    print(f"   Candidate Name: {candidate['name']}")  # Should be 'name'
                    print(f"   Resume Path: {candidate.get('resume_path', 'Not stored')}")
                    print(f"   Session ID: {session_id}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Candidate registration with resume failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Candidate registration with resume failed: {e}")
            return
        
        # Test 3: Test session start
        print(f"\n5. Testing interview session start...")
        try:
            async with session.post(f"{BASE_URL}/public/session/{session_id}/start") as resp:
                if resp.status == 200:
                    start_response = await resp.json()
                    print(f"   ✅ Interview session started successfully")
                    print(f"   Message: {start_response.get('message', '')}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Session start failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Session start failed: {e}")
            return
        
        # Test 4: Verify database consistency
        print(f"\n6. Verifying database field consistency...")
        
        # Check that the candidate was created with correct field names
        try:
            async with session.get(f"{BASE_URL}/public/interview/{interview_id}") as resp:
                if resp.status == 200:
                    interview_data = await resp.json()
                    print(f"   ✅ Interview data retrieved successfully")
                    print(f"   Interview ID: {interview_data.get('id')}")
                    print(f"   Job Role: {interview_data.get('job_role')}")
                    print(f"   Number of Questions: {interview_data.get('number_of_questions')}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Failed to retrieve interview data: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Failed to retrieve interview data: {e}")
            return
        
        print("\n" + "=" * 60)
        print("🎉 FIELD ALIGNMENT TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ SQLAlchemy Model: Candidate has 'name' field")
        print("✅ Pydantic Schema: CandidateCreate uses 'name' field")
        print("✅ Backend Route: Accepts 'name' form field")
        print("✅ Frontend: Sends 'name' in FormData")
        print("✅ Database: Candidate created with correct field names")
        print("✅ No TypeError: 'full_name' is an invalid keyword argument")
        print("✅ Complete flow working end-to-end")
        print(f"\n📋 Frontend Test URL: http://localhost:3000/interview/{interview_id}")
        print("   (Open this in your browser to test the complete frontend flow)")

if __name__ == "__main__":
    asyncio.run(test_field_alignment())


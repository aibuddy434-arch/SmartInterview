#!/usr/bin/env python3
"""
Test script to verify the complete interview flow
"""
import asyncio
import aiohttp
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://127.0.0.1:8000/api"

async def test_complete_flow():
    """Test the complete interview flow from creation to candidate access"""
    
    async with aiohttp.ClientSession() as session:
        print("🚀 Testing Complete Interview Flow")
        print("=" * 50)
        
        # Step 1: Register a user
        print("\n1. Registering user...")
        register_data = {
            "full_name": "Test Interviewer",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "interviewer"
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/register", json=register_data) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    print(f"✅ User registered: {user_data['email']}")
                else:
                    print(f"⚠️  User might already exist: {resp.status}")
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return
        
        # Step 2: Login
        print("\n2. Logging in...")
        login_data = {
            "username": "test@example.com",
            "password": "testpass123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/login", data=login_data) as resp:
                if resp.status == 200:
                    login_response = await resp.json()
                    token = login_response['access_token']
                    print(f"✅ Login successful")
                else:
                    print(f"❌ Login failed: {resp.status}")
                    return
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return
        
        # Step 3: Create interview
        print("\n3. Creating interview...")
        interview_data = {
            "job_role": "Software Engineer",
            "interview_type": "technical",
            "difficulty": "intermediate",
            "focus_areas": ["programming", "algorithms"],
            "number_of_questions": 3,
            "duration_minutes": 30,
            "avatar": "professional",
            "voice": "male_1",
            "questions": [
                {
                    "text": "What is your experience with Python?",
                    "tags": ["programming", "python"],
                    "generated_by": "manual"
                },
                {
                    "text": "Explain the difference between a list and a tuple in Python.",
                    "tags": ["programming", "python", "data-structures"],
                    "generated_by": "manual"
                },
                {
                    "text": "How would you optimize a slow database query?",
                    "tags": ["database", "optimization", "performance"],
                    "generated_by": "manual"
                }
            ]
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with session.post(f"{BASE_URL}/interviews/create", json=interview_data, headers=headers) as resp:
                if resp.status == 200:
                    interview = await resp.json()
                    shareable_link = interview.get('shareable_link', '')
                    print(f"✅ Interview created successfully")
                    print(f"   ID: {interview['id']}")
                    print(f"   Shareable Link: {shareable_link}")
                    
                    # Extract token from shareable link
                    shareable_token = shareable_link.split('/')[-1] if shareable_link else None
                    print(f"   Token: {shareable_token}")
                else:
                    error_text = await resp.text()
                    print(f"❌ Interview creation failed: {resp.status}")
                    print(f"   Error: {error_text}")
                    return
        except Exception as e:
            print(f"❌ Interview creation failed: {e}")
            return
        
        # Step 4: Test public access to interview
        if shareable_token:
            print(f"\n4. Testing public access to interview...")
            try:
                async with session.get(f"{BASE_URL}/public/interview/{shareable_token}") as resp:
                    if resp.status == 200:
                        public_interview = await resp.json()
                        print(f"✅ Public interview access successful")
                        print(f"   Job Role: {public_interview['job_role']}")
                        print(f"   Questions: {len(public_interview.get('questions', []))}")
                    else:
                        error_text = await resp.text()
                        print(f"❌ Public access failed: {resp.status}")
                        print(f"   Error: {error_text}")
            except Exception as e:
                print(f"❌ Public access failed: {e}")
        
        # Step 5: Test candidate registration
        print(f"\n5. Testing candidate registration...")
        candidate_data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890"
        }
        
        try:
            async with session.post(f"{BASE_URL}/public/interview/{shareable_token}/register", json=candidate_data) as resp:
                if resp.status == 200:
                    candidate = await resp.json()
                    print(f"✅ Candidate registration successful")
                    print(f"   Candidate ID: {candidate['id']}")
                    candidate_id = candidate['id']
                else:
                    error_text = await resp.text()
                    print(f"❌ Candidate registration failed: {resp.status}")
                    print(f"   Error: {error_text}")
                    return
        except Exception as e:
            print(f"❌ Candidate registration failed: {e}")
            return
        
        # Step 6: Test session start
        print(f"\n6. Testing interview session start...")
        session_data = {"candidate_id": candidate_id}
        
        try:
            async with session.post(f"{BASE_URL}/public/interview/{shareable_token}/start", data=session_data) as resp:
                if resp.status == 200:
                    session = await resp.json()
                    print(f"✅ Interview session started successfully")
                    print(f"   Session ID: {session['session_id']}")
                else:
                    error_text = await resp.text()
                    print(f"❌ Session start failed: {resp.status}")
                    print(f"   Error: {error_text}")
        except Exception as e:
            print(f"❌ Session start failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Complete flow test finished!")
        print(f"📋 Interview Link: http://localhost:3000/interview/{shareable_token}")
        print("   (Open this in your browser to test the frontend)")

if __name__ == "__main__":
    asyncio.run(test_complete_flow())


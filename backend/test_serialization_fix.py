#!/usr/bin/env python3
"""
Test script to verify serialization fix for ORM models
"""
import asyncio
import aiohttp
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://127.0.0.1:8000/api"

async def test_serialization_fix():
    """Test that all ORM models are properly serialized"""
    
    async with aiohttp.ClientSession() as session:
        print("🔧 Testing Serialization Fix for ORM Models")
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
        
        headers = {"Authorization": f"Bearer {token}"}
        
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
        
        # Step 3: Test candidate registration (should return CandidateOut)
        print(f"\n3. Testing candidate registration serialization...")
        
        form_data = aiohttp.FormData()
        form_data.add_field('name', 'John Doe')
        form_data.add_field('email', 'john@example.com')
        form_data.add_field('phone', '+1234567890')
        
        try:
            async with session.post(f"{BASE_URL}/public/interview/{interview_id}/register", data=form_data) as resp:
                if resp.status == 200:
                    response = await resp.json()
                    candidate = response['candidate']
                    session_id = response['session_id']
                    print(f"   ✅ Candidate registration successful!")
                    print(f"   Candidate ID: {candidate['id']}")
                    print(f"   Candidate Name: {candidate['name']}")
                    print(f"   Candidate Email: {candidate['email']}")
                    print(f"   Candidate Phone: {candidate['phone']}")
                    print(f"   Candidate Created At: {candidate['created_at']}")
                    print(f"   Candidate Updated At: {candidate['updated_at']}")
                    print(f"   Session ID: {session_id}")
                    
                    # Verify the response is properly serialized (no ORM objects)
                    if isinstance(candidate, dict) and 'id' in candidate:
                        print("   ✅ Candidate response is properly serialized (Pydantic model)")
                    else:
                        print("   ❌ Candidate response is not properly serialized")
                        return
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Candidate registration failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Candidate registration failed: {e}")
            return
        
        # Step 4: Test session retrieval (should return InterviewSessionOut)
        print(f"\n4. Testing session retrieval serialization...")
        
        try:
            async with session.get(f"{BASE_URL}/public/session/{session_id}") as resp:
                if resp.status == 200:
                    session_data = await resp.json()
                    print(f"   ✅ Session retrieval successful!")
                    print(f"   Session ID: {session_data['session_id']}")
                    print(f"   Interview Config ID: {session_data['interview_config_id']}")
                    print(f"   Candidate ID: {session_data['candidate_id']}")
                    print(f"   Status: {session_data['status']}")
                    print(f"   Current Question: {session_data['current_question']}")
                    print(f"   Created At: {session_data['created_at']}")
                    print(f"   Updated At: {session_data['updated_at']}")
                    
                    # Verify the response is properly serialized (no ORM objects)
                    if isinstance(session_data, dict) and 'session_id' in session_data:
                        print("   ✅ Session response is properly serialized (Pydantic model)")
                    else:
                        print("   ❌ Session response is not properly serialized")
                        return
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Session retrieval failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Session retrieval failed: {e}")
            return
        
        # Step 5: Test candidate listing (admin route - should return List[CandidateOut])
        print(f"\n5. Testing candidate listing serialization...")
        
        try:
            async with session.get(f"{BASE_URL}/candidates/", headers=headers) as resp:
                if resp.status == 200:
                    candidates = await resp.json()
                    print(f"   ✅ Candidate listing successful!")
                    print(f"   Number of candidates: {len(candidates)}")
                    
                    if candidates:
                        candidate = candidates[0]
                        print(f"   First candidate ID: {candidate['id']}")
                        print(f"   First candidate Name: {candidate['name']}")
                        print(f"   First candidate Email: {candidate['email']}")
                        print(f"   First candidate Created At: {candidate['created_at']}")
                        
                        # Verify the response is properly serialized (no ORM objects)
                        if isinstance(candidate, dict) and 'id' in candidate:
                            print("   ✅ Candidate listing response is properly serialized (Pydantic models)")
                        else:
                            print("   ❌ Candidate listing response is not properly serialized")
                            return
                    else:
                        print("   ⚠️  No candidates found")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Candidate listing failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Candidate listing failed: {e}")
            return
        
        # Step 6: Test candidate sessions listing (admin route - should return List[InterviewSessionOut])
        print(f"\n6. Testing candidate sessions listing serialization...")
        
        try:
            async with session.get(f"{BASE_URL}/candidates/{candidate['id']}/sessions", headers=headers) as resp:
                if resp.status == 200:
                    sessions = await resp.json()
                    print(f"   ✅ Candidate sessions listing successful!")
                    print(f"   Number of sessions: {len(sessions)}")
                    
                    if sessions:
                        session_data = sessions[0]
                        print(f"   First session ID: {session_data['id']}")
                        print(f"   First session Session ID: {session_data['session_id']}")
                        print(f"   First session Status: {session_data['status']}")
                        print(f"   First session Created At: {session_data['created_at']}")
                        
                        # Verify the response is properly serialized (no ORM objects)
                        if isinstance(session_data, dict) and 'session_id' in session_data:
                            print("   ✅ Candidate sessions response is properly serialized (Pydantic models)")
                        else:
                            print("   ❌ Candidate sessions response is not properly serialized")
                            return
                    else:
                        print("   ⚠️  No sessions found")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Candidate sessions listing failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Candidate sessions listing failed: {e}")
            return
        
        # Step 7: Test interview listing (admin route - should return List[InterviewConfig])
        print(f"\n7. Testing interview listing serialization...")
        
        try:
            async with session.get(f"{BASE_URL}/interviews/configs", headers=headers) as resp:
                if resp.status == 200:
                    interviews = await resp.json()
                    print(f"   ✅ Interview listing successful!")
                    print(f"   Number of interviews: {len(interviews)}")
                    
                    if interviews:
                        interview_data = interviews[0]
                        print(f"   First interview ID: {interview_data['id']}")
                        print(f"   First interview Job Role: {interview_data['job_role']}")
                        print(f"   First interview Interview Type: {interview_data['interview_type']}")
                        print(f"   First interview Created At: {interview_data['created_at']}")
                        
                        # Verify the response is properly serialized (no ORM objects)
                        if isinstance(interview_data, dict) and 'id' in interview_data:
                            print("   ✅ Interview listing response is properly serialized (Pydantic models)")
                        else:
                            print("   ❌ Interview listing response is not properly serialized")
                            return
                    else:
                        print("   ⚠️  No interviews found")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Interview listing failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Interview listing failed: {e}")
            return
        
        print("\n" + "=" * 60)
        print("🎉 SERIALIZATION FIX TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ CandidateOut schema working correctly")
        print("✅ InterviewSessionOut schema working correctly")
        print("✅ All routes returning Pydantic models instead of ORM objects")
        print("✅ No PydanticSerializationError for unknown types")
        print("✅ FastAPI can serialize all responses properly")
        print("✅ Complete end-to-end serialization working")
        print(f"\n📋 Frontend Test URL: http://localhost:3000/interview/{interview_id}")
        print("   (Open this in your browser to test the complete frontend flow)")

if __name__ == "__main__":
    asyncio.run(test_serialization_fix())


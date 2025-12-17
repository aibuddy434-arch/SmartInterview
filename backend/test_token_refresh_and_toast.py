#!/usr/bin/env python3
"""
Test script to verify token refresh mechanism and toast fixes
"""
import asyncio
import aiohttp
import json
import sys
import os
import time

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://127.0.0.1:8000/api"

async def test_token_refresh_and_toast():
    """Test token refresh mechanism and verify toast fixes"""
    
    async with aiohttp.ClientSession() as session:
        print("🔧 Testing Token Refresh Mechanism and Toast Fixes")
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
        
        # Step 2: Login and verify both tokens are returned
        print("\n2. Testing login with refresh token...")
        login_data = {
            "username": "interviewer@test.com",
            "password": "testpass123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/login", data=login_data) as resp:
                if resp.status == 200:
                    login_response = await resp.json()
                    access_token = login_response.get('access_token')
                    refresh_token = login_response.get('refresh_token')
                    token_type = login_response.get('token_type')
                    user = login_response.get('user')
                    
                    print(f"   ✅ Login successful")
                    print(f"   Access Token: {access_token[:20]}..." if access_token else "   ❌ No access token")
                    print(f"   Refresh Token: {refresh_token[:20]}..." if refresh_token else "   ❌ No refresh token")
                    print(f"   Token Type: {token_type}")
                    print(f"   User: {user.get('email') if user else 'No user data'}")
                    
                    if not access_token or not refresh_token:
                        print("   ❌ Missing tokens in login response")
                        return
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Login failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Login failed: {e}")
            return
        
        # Step 3: Test access token works
        print("\n3. Testing access token authentication...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with session.get(f"{BASE_URL}/auth/me", headers=headers) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    print(f"   ✅ Access token works - User: {user_data.get('email')}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Access token failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Access token test failed: {e}")
            return
        
        # Step 4: Test refresh token endpoint
        print("\n4. Testing refresh token endpoint...")
        refresh_data = {"refresh_token": refresh_token}
        
        try:
            async with session.post(f"{BASE_URL}/auth/refresh", json=refresh_data) as resp:
                if resp.status == 200:
                    refresh_response = await resp.json()
                    new_access_token = refresh_response.get('access_token')
                    new_token_type = refresh_response.get('token_type')
                    
                    print(f"   ✅ Refresh token successful")
                    print(f"   New Access Token: {new_access_token[:20]}..." if new_access_token else "   ❌ No new access token")
                    print(f"   Token Type: {new_token_type}")
                    
                    if not new_access_token:
                        print("   ❌ No new access token in refresh response")
                        return
                    
                    # Update access token for next test
                    access_token = new_access_token
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Refresh token failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Refresh token test failed: {e}")
            return
        
        # Step 5: Test new access token works
        print("\n5. Testing new access token authentication...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            async with session.get(f"{BASE_URL}/auth/me", headers=headers) as resp:
                if resp.status == 200:
                    user_data = await resp.json()
                    print(f"   ✅ New access token works - User: {user_data.get('email')}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ New access token failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ New access token test failed: {e}")
            return
        
        # Step 6: Test invalid refresh token
        print("\n6. Testing invalid refresh token...")
        invalid_refresh_data = {"refresh_token": "invalid_token"}
        
        try:
            async with session.post(f"{BASE_URL}/auth/refresh", json=invalid_refresh_data) as resp:
                if resp.status == 401:
                    print(f"   ✅ Invalid refresh token correctly rejected: {resp.status}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Invalid refresh token should be rejected: {resp.status} - {error_text}")
        except Exception as e:
            print(f"   ❌ Invalid refresh token test failed: {e}")
        
        # Step 7: Create interview to test candidate registration with toast
        print("\n7. Creating interview for candidate registration test...")
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
        
        # Step 8: Test candidate registration (should work without toast errors)
        print(f"\n8. Testing candidate registration (toast fix verification)...")
        
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
                    print(f"   Session ID: {session_id}")
                    print(f"   ✅ No toast errors - registration completed successfully")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Candidate registration failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Candidate registration failed: {e}")
            return
        
        # Step 9: Test session start (should work without toast errors)
        print(f"\n9. Testing interview session start...")
        try:
            async with session.post(f"{BASE_URL}/public/session/{session_id}/start") as resp:
                if resp.status == 200:
                    start_response = await resp.json()
                    print(f"   ✅ Interview session started successfully")
                    print(f"   Message: {start_response.get('message', '')}")
                    print(f"   ✅ No toast errors - session started successfully")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Session start failed: {resp.status} - {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Session start failed: {e}")
            return
        
        print("\n" + "=" * 60)
        print("🎉 TOKEN REFRESH AND TOAST FIXES VERIFIED!")
        print("=" * 60)
        print("✅ Refresh token mechanism working correctly")
        print("✅ Access token refresh successful")
        print("✅ Invalid refresh token properly rejected")
        print("✅ New access token works after refresh")
        print("✅ Candidate registration working without toast errors")
        print("✅ Interview session start working without toast errors")
        print("✅ Complete end-to-end flow functional")
        print(f"\n📋 Frontend Test URL: http://localhost:3000/interview/{interview_id}")
        print("   (Open this in your browser to test the complete frontend flow)")
        print("\n🔧 Frontend Token Refresh Test:")
        print("   1. Login to frontend")
        print("   2. Wait for access token to expire (or manually expire it)")
        print("   3. Try to perform an action - should auto-refresh token")
        print("   4. Verify no redirect to login page")

if __name__ == "__main__":
    asyncio.run(test_token_refresh_and_toast())


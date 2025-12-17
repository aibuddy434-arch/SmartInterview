#!/usr/bin/env python3
"""
Debug script to test authentication flow
"""
import asyncio
import aiohttp
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://127.0.0.1:8000/api"

async def debug_auth():
    """Debug the authentication flow step by step"""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Debugging Authentication Flow")
        print("=" * 50)
        
        # Step 1: Register a user
        print("\n1. Registering user...")
        register_data = {
            "full_name": "Debug User",
            "email": "debug@example.com",
            "password": "debugpass123",
            "role": "interviewer"
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/register", json=register_data) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    user_data = await resp.json()
                    print(f"   ✅ User registered: {user_data['email']}")
                    print(f"   User ID: {user_data['id']}")
                else:
                    error_text = await resp.text()
                    print(f"   ⚠️  Registration response: {error_text}")
        except Exception as e:
            print(f"   ❌ Registration failed: {e}")
            return
        
        # Step 2: Login
        print("\n2. Logging in...")
        login_data = {
            "username": "debug@example.com",
            "password": "debugpass123"
        }
        
        try:
            async with session.post(f"{BASE_URL}/auth/login", data=login_data) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    login_response = await resp.json()
                    token = login_response.get('access_token')
                    token_type = login_response.get('token_type')
                    user_info = login_response.get('user')
                    
                    print(f"   ✅ Login successful")
                    print(f"   Token: {token[:20]}...")
                    print(f"   Token Type: {token_type}")
                    print(f"   User: {user_info['email'] if user_info else 'None'}")
                    
                    if not token:
                        print("   ❌ No access_token in response!")
                        return
                else:
                    error_text = await resp.text()
                    print(f"   ❌ Login failed: {error_text}")
                    return
        except Exception as e:
            print(f"   ❌ Login failed: {e}")
            return
        
        # Step 3: Test /me endpoint
        print("\n3. Testing /me endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with session.get(f"{BASE_URL}/auth/me", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                if resp.status == 200:
                    me_data = await resp.json()
                    print(f"   ✅ /me endpoint successful")
                    print(f"   User: {me_data['email']}")
                else:
                    error_text = await resp.text()
                    print(f"   ❌ /me endpoint failed: {error_text}")
                    print(f"   Response headers: {dict(resp.headers)}")
        except Exception as e:
            print(f"   ❌ /me endpoint failed: {e}")
        
        # Step 4: Test token validation manually
        print("\n4. Testing token validation...")
        try:
            from jose import jwt
            from app.config import settings
            
            # Decode the token
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            print(f"   ✅ Token decoded successfully")
            print(f"   Payload: {payload}")
            
            # Check if email exists in payload
            email = payload.get("sub")
            if email:
                print(f"   ✅ Email found in token: {email}")
            else:
                print(f"   ❌ No email in token payload!")
                
        except Exception as e:
            print(f"   ❌ Token validation failed: {e}")
        
        print("\n" + "=" * 50)
        print("🎯 Debug complete!")

if __name__ == "__main__":
    asyncio.run(debug_auth())


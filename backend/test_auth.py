#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

from app.repositories.user_repository import UserRepository
from app.db import AsyncSessionLocal
from utils.auth import get_password_hash, verify_password

async def test_auth():
    print("Testing authentication...")
    
    # Test password hashing
    password = "testpass123"
    hashed = get_password_hash(password)
    print(f"Password hashed: {hashed[:50]}...")
    
    # Test password verification
    is_valid = verify_password(password, hashed)
    print(f"Password verification: {is_valid}")
    
    # Test user creation
    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        
        # Test user data
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",  # This should be removed
            "password_hash": hashed,
            "full_name": "Test User",
            "role": "candidate"
        }
        
        try:
            # Check if user exists
            existing_user = await user_repo.get_user_by_email("test@example.com")
            if existing_user:
                print("User already exists, testing login...")
                # Test login
                login_user = await user_repo.authenticate_user("test@example.com", "testpass123")
                if login_user:
                    print(f"Login successful: {login_user.email}")
                else:
                    print("Login failed")
            else:
                print("Creating new user...")
                created_user = await user_repo.create_user(user_data)
                print(f"User created: {created_user.email}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_auth())

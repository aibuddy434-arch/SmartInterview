#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

from app.repositories.user_repository import UserRepository
from app.db import AsyncSessionLocal

async def check_and_update_user():
    print("Checking user role...")
    
    async with AsyncSessionLocal() as db:
        user_repo = UserRepository(db)
        
        # Get user by email
        user = await user_repo.get_user_by_email("test@example.com")
        if user:
            print(f"User found: {user.email}")
            print(f"Current role: {user.role}")
            
            # Update role to interviewer
            if user.role != "interviewer":
                print("Updating role to interviewer...")
                await user_repo.update_user(user.id, {"role": "interviewer"})
                print("Role updated successfully!")
            else:
                print("User already has interviewer role")
        else:
            print("User not found")

if __name__ == "__main__":
    try:
        asyncio.run(check_and_update_user())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close any remaining connections
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.close()
        except:
            pass

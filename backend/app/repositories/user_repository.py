from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.orm_models import User
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        try:
            # Remove password field if it exists (should be password_hash instead)
            if 'password' in user_data:
                del user_data['password']
            
            user = User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """Get users by role"""
        try:
            result = await self.db.execute(
                select(User).where(User.role == role)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get users by role {role}: {e}")
            return []
    
    async def update_user(self, user_id: str, update_data: dict) -> Optional[User]:
        """Update user"""
        try:
            result = await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            if result.rowcount > 0:
                return await self.get_user_by_id(user_id)
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user {user_id}: {e}")
            return None
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        try:
            user = await self.get_user_by_id(user_id)
            if user:
                await self.db.delete(user)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False
    
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination"""
        try:
            result = await self.db.execute(
                select(User)
                .limit(limit)
                .offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            return []
    
    async def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        try:
            result = await self.db.execute(
                select(User.id).where(User.email == email)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Failed to check if user exists: {e}")
            return False
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            
            # Import here to avoid circular imports
            from utils.auth import verify_password
            
            if not verify_password(password, user.password_hash):
                return None
            
            return user
        except Exception as e:
            logger.error(f"Failed to authenticate user: {e}")
            return None


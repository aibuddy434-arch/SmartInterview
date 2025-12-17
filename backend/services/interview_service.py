import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets
from app.repositories.interview_repository import InterviewRepository
from app.repositories.session_repository import SessionRepository
from models.interview import InterviewConfig, InterviewConfigCreate, Question
from models.user import User

logger = logging.getLogger(__name__)

class InterviewService:
    def __init__(self, db_session):
        self.repository = InterviewRepository(db_session)
        self.session_repository = SessionRepository(db_session)
    
    async def create_interview_config(self, config_data: InterviewConfigCreate, user_id: str) -> InterviewConfig:
        """Create a new interview configuration"""
        try:
            # Convert to dict and add metadata
            config_dict = config_data.model_dump()
            config_dict["created_by"] = user_id
            
            # Create the interview configuration
            created_config = await self.repository.create_interview_config(config_dict)
            
            logger.info(f"Interview config created by user {user_id}: {created_config.id}")
            return created_config

        except Exception as e:
            logger.error(f"Failed to create interview config: {e}")
            raise Exception(f"Failed to create interview config: {str(e)}")
    
    async def get_interview_config(self, config_id: str) -> Optional[InterviewConfig]:
        """Get interview configuration by ID"""
        try:
            return await self.repository.get_interview_config(config_id)
        except Exception as e:
            logger.error(f"Failed to get interview config {config_id}: {e}")
            return None
    
    async def get_interview_configs_by_user(self, user_id: str) -> List[InterviewConfig]:
        """Get all interview configurations created by a user"""
        try:
            return await self.repository.get_interview_configs_by_user(user_id)
        except Exception as e:
            logger.error(f"Failed to get interview configs for user {user_id}: {e}")
            return []
    
    async def update_interview_config(self, config_id: str, update_data: Dict[str, Any], user_id: str) -> Optional[InterviewConfig]:
        """Update interview configuration"""
        try:
            return await self.repository.update_interview_config(config_id, update_data, user_id)
        except Exception as e:
            logger.error(f"Failed to update interview config {config_id}: {e}")
            return None
    
    async def delete_interview_config(self, config_id: str, user_id: str) -> bool:
        """Delete interview configuration"""
        try:
            return await self.repository.delete_interview_config(config_id, user_id)
        except Exception as e:
            logger.error(f"Failed to delete interview config {config_id}: {e}")
            return False
    
    async def add_questions_to_config(self, config_id: str, questions: List[Question], user_id: str) -> Optional[InterviewConfig]:
        """Add questions to an interview configuration"""
        try:
            # Convert questions to dict format
            questions_dict = [q.model_dump() for q in questions]
            
            return await self.repository.add_questions_to_config(config_id, questions_dict, user_id)
        except Exception as e:
            logger.error(f"Failed to add questions to config {config_id}: {e}")
            return None
    
    async def generate_shareable_link(self, config_id: str) -> str:
        """Generate a shareable link for the interview"""
        # In a real implementation, you might want to generate a secure token
        return f"/interview/{config_id}"
    
    async def get_interview_stats(self, config_id: str, user_id: str) -> Dict[str, Any]:
        """Get statistics for an interview configuration"""
        try:
            config = await self.get_interview_config(config_id)
            if not config or config.created_by != user_id:
                return {}
            
            # You can add more stats here like candidate count, completion rate, etc.
            return {
                "total_candidates": config.total_candidates,
                "completed_sessions": config.completed_sessions,
                "is_active": config.is_active,
                "created_at": config.created_at,
                "updated_at": config.updated_at
            }
        except Exception as e:
            logger.error(f"Failed to get stats for config {config_id}: {e}")
            return {}

# Create service instance (will be initialized with db session)
interview_service = None

def get_interview_service(db_session):
    """Factory function to get interview service with db session"""
    global interview_service
    if interview_service is None:
        interview_service = InterviewService(db_session)
    return interview_service

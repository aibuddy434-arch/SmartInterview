from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.orm_models import InterviewConfig, Question
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class InterviewRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_interview_config(self, config_data: dict) -> InterviewConfig:
        """Create a new interview configuration"""
        try:
            # Extract questions from config_data
            questions_data = config_data.pop('questions', [])
            
            # Create the interview config without questions first
            interview_config = InterviewConfig(**config_data)
            self.db.add(interview_config)
            await self.db.flush()  # Flush to get the ID
            
            # Now update with shareable link using the generated ID
            interview_config.shareable_link = f"/interview/{interview_config.id}"
            await self.db.commit()
            
            # Create questions separately with unique IDs
            for question_data in questions_data:
                # Generate unique ID if not provided or if it's a duplicate pattern
                question_id = question_data.get('id')
                if not question_id or question_id.startswith('ai_'):
                    import uuid
                    question_id = str(uuid.uuid4())
                
                question = Question(
                    id=question_id,
                    text=question_data['text'],
                    tags=question_data.get('tags', []),
                    generated_by=question_data.get('generated_by', 'manual'),
                    interview_config_id=interview_config.id
                )
                self.db.add(question)
            
            await self.db.commit()
            
            # Reload the interview config with questions using eager loading
            result = await self.db.execute(
                select(InterviewConfig)
                .options(selectinload(InterviewConfig.questions))
                .where(InterviewConfig.id == interview_config.id)
            )
            interview_config_with_questions = result.scalar_one()
            return interview_config_with_questions
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create interview config: {e}")
            raise
    
    async def get_interview_config(self, config_id: str) -> Optional[InterviewConfig]:
        """Get interview configuration by ID with questions"""
        try:
            result = await self.db.execute(
                select(InterviewConfig)
                .options(selectinload(InterviewConfig.questions))
                .where(InterviewConfig.id == config_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get interview config {config_id}: {e}")
            return None
    
    async def get_interview_config_by_shareable_link(self, shareable_link: str) -> Optional[InterviewConfig]:
        """Get interview configuration by shareable link with questions"""
        try:
            result = await self.db.execute(
                select(InterviewConfig)
                .options(selectinload(InterviewConfig.questions))
                .where(InterviewConfig.shareable_link == shareable_link)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get interview config by shareable link {shareable_link}: {e}")
            return None
    
    async def get_interview_configs_by_user(self, user_id: str) -> List[InterviewConfig]:
        """Get all interview configurations created by a user"""
        try:
            result = await self.db.execute(
                select(InterviewConfig)
                .options(selectinload(InterviewConfig.questions))
                .where(InterviewConfig.created_by == user_id)
                .order_by(InterviewConfig.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get interview configs for user {user_id}: {e}")
            return []
    
    async def update_interview_config(self, config_id: str, update_data: dict, user_id: str) -> Optional[InterviewConfig]:
        """Update interview configuration"""
        try:
            result = await self.db.execute(
                update(InterviewConfig)
                .where(InterviewConfig.id == config_id, InterviewConfig.created_by == user_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            if result.rowcount > 0:
                return await self.get_interview_config(config_id)
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update interview config {config_id}: {e}")
            return None
    
    async def delete_interview_config(self, config_id: str, user_id: str) -> bool:
        """Delete interview configuration"""
        try:
            result = await self.db.execute(
                delete(InterviewConfig)
                .where(InterviewConfig.id == config_id, InterviewConfig.created_by == user_id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete interview config {config_id}: {e}")
            return False
    
    async def add_questions_to_config(self, config_id: str, questions_data: List[dict], user_id: str) -> Optional[InterviewConfig]:
        """Add questions to an interview configuration"""
        try:
            # First verify the config belongs to the user
            config = await self.get_interview_config(config_id)
            if not config or config.created_by != user_id:
                return None
            
            # Delete existing questions
            await self.db.execute(
                delete(Question).where(Question.interview_config_id == config_id)
            )
            
            # Add new questions
            for question_data in questions_data:
                question_data['interview_config_id'] = config_id
                question = Question(**question_data)
                self.db.add(question)
            
            await self.db.commit()
            
            # Return updated config
            return await self.get_interview_config(config_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to add questions to config {config_id}: {e}")
            return None
    
    async def get_active_interview_configs(self) -> List[InterviewConfig]:
        """Get all active interview configurations"""
        try:
            result = await self.db.execute(
                select(InterviewConfig)
                .options(selectinload(InterviewConfig.questions))
                .where(InterviewConfig.is_active == True)
                .order_by(InterviewConfig.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get active interview configs: {e}")
            return []
    
    async def update_interview_stats(self, config_id: str, stats: Dict[str, Any]) -> bool:
        """Update interview configuration statistics"""
        try:
            result = await self.db.execute(
                update(InterviewConfig)
                .where(InterviewConfig.id == config_id)
                .values(**stats)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update interview stats for {config_id}: {e}")
            return False
    
    async def get_interview_config_by_id(self, config_id: str) -> Optional[InterviewConfig]:
        """Get interview configuration by ID (alias for get_interview_config)"""
        return await self.get_interview_config(config_id)
    
    async def create_interview(self, interview_data: dict) -> InterviewConfig:
        """Create a new interview (alias for create_interview_config)"""
        return await self.create_interview_config(interview_data)
    
    async def get_all_interviews(self) -> List[InterviewConfig]:
        """Get all interview configurations"""
        try:
            result = await self.db.execute(
                select(InterviewConfig)
                .options(selectinload(InterviewConfig.questions))
                .order_by(InterviewConfig.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get all interviews: {e}")
            return []
    
    async def get_interview_by_id(self, interview_id: str) -> Optional[InterviewConfig]:
        """Get interview by ID (alias for get_interview_config)"""
        return await self.get_interview_config(interview_id)
    
    async def update_interview(self, interview_id: str, update_data: dict) -> Optional[InterviewConfig]:
        """Update interview (alias for update_interview_config)"""
        try:
            result = await self.db.execute(
                update(InterviewConfig)
                .where(InterviewConfig.id == interview_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            if result.rowcount > 0:
                return await self.get_interview_config(interview_id)
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update interview {interview_id}: {e}")
            return None
    
    async def delete_interview(self, interview_id: str) -> bool:
        """Delete interview (alias for delete_interview_config)"""
        try:
            result = await self.db.execute(
                delete(InterviewConfig)
                .where(InterviewConfig.id == interview_id)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete interview {interview_id}: {e}")
            return False


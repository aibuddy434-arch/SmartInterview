from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.orm_models import Candidate, InterviewSession
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CandidateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_candidate(self, candidate_data: dict) -> Candidate:
        """Create a new candidate"""
        try:
            candidate = Candidate(**candidate_data)
            self.db.add(candidate)
            await self.db.commit()
            await self.db.refresh(candidate)
            return candidate
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create candidate: {e}")
            raise
    
    async def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Get candidate by ID with interview sessions"""
        try:
            result = await self.db.execute(
                select(Candidate)
                .options(selectinload(Candidate.interview_sessions))
                .where(Candidate.id == candidate_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get candidate by ID {candidate_id}: {e}")
            return None
    
    async def get_candidate_by_email(self, email: str) -> Optional[Candidate]:
        """Get candidate by email"""
        try:
            result = await self.db.execute(
                select(Candidate).where(Candidate.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get candidate by email {email}: {e}")
            return None
    
    async def update_candidate(self, candidate_id: str, update_data: dict) -> Optional[Candidate]:
        """Update candidate"""
        try:
            result = await self.db.execute(
                update(Candidate)
                .where(Candidate.id == candidate_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            if result.rowcount > 0:
                return await self.get_candidate_by_id(candidate_id)
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update candidate {candidate_id}: {e}")
            return None
    
    async def delete_candidate(self, candidate_id: str) -> bool:
        """Delete candidate"""
        try:
            candidate = await self.get_candidate_by_id(candidate_id)
            if candidate:
                await self.db.delete(candidate)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete candidate {candidate_id}: {e}")
            return False
    
    async def get_all_candidates(self, limit: int = 100, offset: int = 0) -> List[Candidate]:
        """Get all candidates with pagination"""
        try:
            result = await self.db.execute(
                select(Candidate)
                .options(selectinload(Candidate.interview_sessions))
                .limit(limit)
                .offset(offset)
                .order_by(Candidate.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get all candidates: {e}")
            return []
    
    async def update_resume_path(self, candidate_id: str, resume_path: str) -> bool:
        """Update candidate's resume path"""
        try:
            result = await self.db.execute(
                update(Candidate)
                .where(Candidate.id == candidate_id)
                .values(resume_path=resume_path)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update resume path for candidate {candidate_id}: {e}")
            return False
    
    async def get_candidates_by_interview_config(self, config_id: str) -> List[Candidate]:
        """Get candidates who have sessions for a specific interview config"""
        try:
            result = await self.db.execute(
                select(Candidate)
                .join(InterviewSession)
                .where(InterviewSession.interview_config_id == config_id)
                .distinct()
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get candidates for interview config {config_id}: {e}")
            return []
    
    async def candidate_exists(self, email: str) -> bool:
        """Check if candidate exists by email"""
        try:
            result = await self.db.execute(
                select(Candidate.id).where(Candidate.email == email)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Failed to check if candidate exists: {e}")
            return False


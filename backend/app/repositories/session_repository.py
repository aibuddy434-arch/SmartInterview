# Replace the entire contents of session_repository.py with this code

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.orm_models import InterviewSession, Response
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_interview_session(self, session_data: dict) -> InterviewSession:
        """Create a new interview session"""
        try:
            session = InterviewSession(**session_data)
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)
            return session
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create interview session: {e}")
            raise

    async def get_interview_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get interview session by ID with responses"""
        try:
            result = await self.db.execute(
                select(InterviewSession)
                .options(
                    selectinload(InterviewSession.responses),
                    selectinload(InterviewSession.interview_config),
                    selectinload(InterviewSession.candidate)
                )
                .where(InterviewSession.session_id == session_id)  # <-- FIXED
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get interview session {session_id}: {e}")
            return None

    async def get_session_by_session_id(self, session_id: str) -> Optional[InterviewSession]:
        """Get interview session by session_id field"""
        try:
            result = await self.db.execute(
                select(InterviewSession)
                .options(
                    selectinload(InterviewSession.responses),
                    selectinload(InterviewSession.interview_config),
                    selectinload(InterviewSession.candidate)
                )
                .where(InterviewSession.session_id == session_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get interview session by session_id {session_id}: {e}")
            return None

    # Alias for get_session_by_session_id
    async def get_session_by_id(self, session_id: str) -> Optional[InterviewSession]:
        """Alias for get_session_by_session_id"""
        return await self.get_session_by_session_id(session_id)

    async def get_sessions_by_candidate(self, candidate_id: str) -> List[InterviewSession]:
        """Get all interview sessions for a candidate"""
        try:
            result = await self.db.execute(
                select(InterviewSession)
                .options(
                    selectinload(InterviewSession.responses),
                    selectinload(InterviewSession.interview_config)
                )
                .where(InterviewSession.candidate_id == candidate_id)
                .order_by(InterviewSession.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get sessions for candidate {candidate_id}: {e}")
            return []

    async def get_sessions_by_interview_config(self, config_id: str) -> List[InterviewSession]:
        """Get all interview sessions for an interview config"""
        try:
            result = await self.db.execute(
                select(InterviewSession)
                .options(
                    selectinload(InterviewSession.responses),
                    selectinload(InterviewSession.candidate)
                )
                .where(InterviewSession.interview_config_id == config_id)
                .order_by(InterviewSession.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get sessions for interview config {config_id}: {e}")
            return []

    async def update_session_status(self, session_id: str, status: str) -> bool:
        """Update interview session status"""
        try:
            result = await self.db.execute(
                update(InterviewSession)
                .where(InterviewSession.session_id == session_id)  # <-- FIXED
                .values(status=status)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update session status for {session_id}: {e}")
            return False

    async def update_session_score(self, session_id: str, score: float, feedback: str = None) -> bool:
        """Update interview session score and feedback"""
        try:
            update_data = {"score": score}
            if feedback:
                update_data["feedback"] = feedback

            result = await self.db.execute(
                update(InterviewSession)
                .where(InterviewSession.session_id == session_id)  # <-- FIXED
                .values(**update_data)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update session score for {session_id}: {e}")
            return False

    async def add_response(self, response_data: dict) -> Response:
        """Add a response to an interview session"""
        try:
            response = Response(**response_data)
            self.db.add(response)
            await self.db.commit()
            await self.db.refresh(response)
            return response
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to add response: {e}")
            raise

    async def get_session_responses(self, session_id: str) -> List[Response]:
        """Get all responses for an interview session"""
        try:
            result = await self.db.execute(
                select(Response)
                .where(Response.session_id == session_id)
                .order_by(Response.question_number)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get responses for session {session_id}: {e}")
            return []

    async def delete_session(self, session_id: str) -> bool:
        """Delete interview session and all related data"""
        try:
            session = await self.get_interview_session(session_id)
            if session:
                await self.db.delete(session)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    async def create_session(self, session_data: dict) -> InterviewSession:
        """Create a new session (alias for create_interview_session)"""
        return await self.create_interview_session(session_data)

    async def get_session_by_id(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by ID (alias for get_interview_session)"""
        return await self.get_interview_session(session_id)

    async def update_session(self, session_id: str, update_data: dict) -> bool:
        """Update session with any fields"""
        try:
            result = await self.db.execute(
                update(InterviewSession)
                .where(InterviewSession.session_id == session_id)  # <-- FIXED
                .values(**update_data)
            )
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    async def create_response(self, response_data: dict) -> Response:
        """Create a response (alias for add_response)"""
        return await self.add_response(response_data)
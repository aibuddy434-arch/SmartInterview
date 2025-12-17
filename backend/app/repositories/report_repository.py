from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.orm_models import Report, InterviewSession, Candidate
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_report(self, report_data: dict) -> Report:
        """Create a new report"""
        try:
            report = Report(**report_data)
            self.db.add(report)
            await self.db.commit()
            await self.db.refresh(report)
            return report
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create report: {e}")
            raise
    
    async def get_report_by_id(self, report_id: str) -> Optional[Report]:
        """Get report by ID with related data"""
        try:
            result = await self.db.execute(
                select(Report)
                .options(
                    selectinload(Report.interview_session),
                    selectinload(Report.candidate)
                )
                .where(Report.id == report_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get report by ID {report_id}: {e}")
            return None
    
    async def get_report_by_session_id(self, session_id: str) -> Optional[Report]:
        """Get report by session ID"""
        try:
            result = await self.db.execute(
                select(Report)
                .options(
                    selectinload(Report.interview_session),
                    selectinload(Report.candidate)
                )
                .where(Report.session_id == session_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get report by session ID {session_id}: {e}")
            return None
    
    async def get_reports_by_candidate(self, candidate_id: str) -> List[Report]:
        """Get all reports for a candidate"""
        try:
            result = await self.db.execute(
                select(Report)
                .options(
                    selectinload(Report.interview_session),
                    selectinload(Report.interview_session).selectinload(InterviewSession.interview_config)
                )
                .where(Report.candidate_id == candidate_id)
                .order_by(Report.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get reports for candidate {candidate_id}: {e}")
            return []
    
    async def get_reports_by_interview_config(self, config_id: str) -> List[Report]:
        """Get all reports for an interview config"""
        try:
            result = await self.db.execute(
                select(Report)
                .join(InterviewSession)
                .options(
                    selectinload(Report.candidate)
                )
                .where(InterviewSession.interview_config_id == config_id)
                .order_by(Report.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get reports for interview config {config_id}: {e}")
            return []
    
    async def update_report(self, report_id: str, update_data: dict) -> Optional[Report]:
        """Update report"""
        try:
            result = await self.db.execute(
                update(Report)
                .where(Report.id == report_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            if result.rowcount > 0:
                return await self.get_report_by_id(report_id)
            return None
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update report {report_id}: {e}")
            return None
    
    async def delete_report(self, report_id: str) -> bool:
        """Delete report"""
        try:
            report = await self.get_report_by_id(report_id)
            if report:
                await self.db.delete(report)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete report {report_id}: {e}")
            return False
    
    async def get_all_reports(self, limit: int = 100, offset: int = 0) -> List[Report]:
        """Get all reports with pagination"""
        try:
            result = await self.db.execute(
                select(Report)
                .options(
                    selectinload(Report.interview_session),
                    selectinload(Report.candidate)
                )
                .limit(limit)
                .offset(offset)
                .order_by(Report.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get all reports: {e}")
            return []
    
    async def get_reports_by_score_range(self, min_score: float, max_score: float) -> List[Report]:
        """Get reports within a score range"""
        try:
            result = await self.db.execute(
                select(Report)
                .options(
                    selectinload(Report.interview_session),
                    selectinload(Report.candidate)
                )
                .where(Report.overall_score >= min_score, Report.overall_score <= max_score)
                .order_by(Report.overall_score.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Failed to get reports by score range: {e}")
            return []
    
    async def get_average_score_by_config(self, config_id: str) -> Optional[float]:
        """Get average score for an interview config"""
        try:
            result = await self.db.execute(
                select(Report.overall_score)
                .join(InterviewSession)
                .where(InterviewSession.interview_config_id == config_id)
            )
            scores = result.scalars().all()
            if scores:
                return sum(scores) / len(scores)
            return None
        except Exception as e:
            logger.error(f"Failed to get average score for config {config_id}: {e}")
            return None


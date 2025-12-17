import logging
from typing import Dict, Any, List
from datetime import datetime
from app.repositories.session_repository import SessionRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.interview_repository import InterviewRepository
from models.interview import InterviewSession
from models.candidate import Candidate

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, db_session):
        self.session_repository = SessionRepository(db_session)
        self.candidate_repository = CandidateRepository(db_session)
        self.interview_repository = InterviewRepository(db_session)
        self.db = db_session
    
    async def generate_interview_report(self, session_id: str) -> Dict[str, Any]:
        """Generate a comprehensive interview report with detailed question/answer analysis"""
        try:
            # Get session with all related data
            session = await self.session_repository.get_session_by_id(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Get candidate
            candidate = await self.candidate_repository.get_candidate_by_id(session.candidate_id)
            if not candidate:
                raise ValueError(f"Candidate not found for session {session_id}")
            
            # Get interview config with questions
            interview_config = await self.interview_repository.get_interview_config_by_id(session.interview_config_id)
            if not interview_config:
                raise ValueError(f"Interview config not found for session {session_id}")
            
            # Eager load questions
            await self.db.refresh(interview_config, ['questions'])
            questions = interview_config.questions
            
            # Get all responses
            responses = await self.session_repository.get_session_responses(session_id)
            
            # Build detailed response list with question text
            detailed_responses = []
            for response in responses:
                q_index = response.question_number - 1  # 0-based index
                question_text = ""
                question_tags = []
                
                if 0 <= q_index < len(questions):
                    question_text = questions[q_index].text
                    question_tags = questions[q_index].tags or []
                
                # Analyze the response
                analysis = self._analyze_response(response.transcript, question_text, interview_config.job_role)
                
                detailed_responses.append({
                    "question_number": response.question_number,
                    "question_text": question_text,
                    "question_tags": question_tags,
                    "candidate_answer": response.transcript or "[No response recorded]",
                    "audio_path": response.audio_path,
                    "answer_quality": analysis.get("quality", "Unknown"),
                    "key_points": analysis.get("key_points", []),
                    "improvement_areas": analysis.get("improvements", []),
                    "created_at": response.created_at
                })
            
            # Calculate scores
            scores = await self._calculate_scores(responses, interview_config)
            
            # Generate overall assessment
            overall_assessment = self._generate_assessment(scores, detailed_responses, interview_config.job_role)
            
            # Generate report
            report = {
                "session_id": session_id,
                "candidate": {
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "resume_path": candidate.resume_path
                },
                "interview": {
                    "id": interview_config.id,
                    "job_role": interview_config.job_role,
                    "job_description": interview_config.job_description,
                    "interview_type": interview_config.interview_type,
                    "difficulty": interview_config.difficulty,
                    "focus_areas": interview_config.focus
                },
                "session": {
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                    "duration_minutes": self._calculate_duration(session.start_time, session.end_time),
                    "status": session.status,
                    "total_questions": len(questions),
                    "answered_questions": len(responses)
                },
                "scores": scores,
                "responses": detailed_responses,
                "overall_assessment": overall_assessment,
                "generated_at": datetime.utcnow(),
                "overall_rating": self._calculate_overall_rating(scores)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report for session {session_id}: {e}")
            raise
    
    def _analyze_response(self, transcript: str, question: str, job_role: str) -> Dict[str, Any]:
        """Analyze a single response for quality and key points"""
        if not transcript or len(transcript.strip()) < 10:
            return {
                "quality": "Poor",
                "key_points": [],
                "improvements": ["No substantial response provided"]
            }
        
        transcript_lower = transcript.lower()
        word_count = len(transcript.split())
        
        # Determine quality based on length and content
        quality = "Good"
        if word_count < 20:
            quality = "Needs Improvement"
        elif word_count > 50:
            quality = "Excellent"
        
        # Extract key points (simple heuristic - sentences with keywords)
        key_points = []
        sentences = transcript.split('.')
        for sentence in sentences[:3]:  # First 3 sentences
            if len(sentence.strip()) > 20:
                key_points.append(sentence.strip())
        
        # Generate improvement suggestions
        improvements = []
        if word_count < 30:
            improvements.append("Consider providing more detailed answers")
        if "experience" not in transcript_lower and "project" not in transcript_lower:
            improvements.append("Include specific examples from your experience")
        if "result" not in transcript_lower and "outcome" not in transcript_lower:
            improvements.append("Mention measurable outcomes or results")
        
        return {
            "quality": quality,
            "key_points": key_points if key_points else ["Response recorded but key points could not be extracted"],
            "improvements": improvements if improvements else ["Good response overall"]
        }
    
    def _generate_assessment(self, scores: Dict, responses: List, job_role: str) -> Dict[str, Any]:
        """Generate overall assessment summary"""
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        
        strengths = []
        weaknesses = []
        
        if scores.get("communication", 0) >= 70:
            strengths.append("Strong communication skills")
        else:
            weaknesses.append("Communication could be more clear and structured")
        
        if scores.get("technical", 0) >= 70:
            strengths.append("Good technical knowledge")
        else:
            weaknesses.append("Technical depth needs improvement")
        
        if scores.get("confidence", 0) >= 70:
            strengths.append("Confident presentation")
        else:
            weaknesses.append("Could project more confidence")
        
        if scores.get("completeness", 0) >= 70:
            strengths.append("Thorough and complete answers")
        else:
            weaknesses.append("Answers could be more comprehensive")
        
        # Hiring recommendation
        if avg_score >= 80:
            recommendation = "Strongly Recommend"
            recommendation_detail = f"Candidate shows excellent potential for the {job_role} role."
        elif avg_score >= 60:
            recommendation = "Recommend with Reservations"
            recommendation_detail = f"Candidate has potential but may need additional training for {job_role}."
        elif avg_score >= 40:
            recommendation = "Consider for Junior Role"
            recommendation_detail = "Candidate may be suitable for a more junior position."
        else:
            recommendation = "Not Recommended"
            recommendation_detail = "Candidate's performance does not meet the requirements."
        
        return {
            "strengths": strengths,
            "areas_for_improvement": weaknesses,
            "recommendation": recommendation,
            "recommendation_detail": recommendation_detail,
            "average_score": round(avg_score, 1)
        }

    
    async def _calculate_scores(self, responses: List, interview_config) -> Dict[str, Any]:
        """Calculate various scores based on responses"""
        if not responses:
            return {
                "communication": 0,
                "technical": 0,
                "confidence": 0,
                "completeness": 0
            }
        
        # Filter out failed transcriptions
        valid_responses = [r for r in responses if r.transcript and 
                          not r.transcript.startswith("[") and 
                          len(r.transcript.strip()) > 10]
        
        total_responses = len(responses)
        valid_count = len(valid_responses)
        
        # Base completion rate
        completion_rate = valid_count / total_responses if total_responses > 0 else 0
        
        # Calculate average response length (only for valid responses)
        if valid_responses:
            avg_response_length = sum(len(r.transcript or "") for r in valid_responses) / valid_count
        else:
            avg_response_length = 0
        
        # Communication score (based on response length, structure, and clarity)
        # Give base score plus bonuses for length and valid responses
        communication_score = 20  # Base score for participating
        if valid_count > 0:
            communication_score += (completion_rate * 40)  # Up to 40 for completion
            communication_score += min(30, (avg_response_length / 100) * 30)  # Up to 30 for length
            # Bonus for using complete sentences (simple heuristic)
            sentences_per_response = sum(r.transcript.count('.') + r.transcript.count('!') + r.transcript.count('?') 
                                        for r in valid_responses) / valid_count
            communication_score += min(10, sentences_per_response * 2)  # Up to 10 for structure
        communication_score = min(100, communication_score)
        
        # Technical score (based on keywords and technical terms)
        technical_keywords = self._extract_technical_keywords(
            interview_config.job_role, 
            interview_config.focus,
            interview_config.job_description if hasattr(interview_config, 'job_description') else ""
        )
        technical_score = self._calculate_technical_score(valid_responses if valid_responses else responses, technical_keywords)
        # Ensure minimum score if candidate responded
        if valid_count > 0 and technical_score < 15:
            technical_score = 15 + (completion_rate * 10)  # Minimum 15-25 if they answered
        
        # Confidence score (based on response length and consistency)
        confidence_score = 15  # Base score
        if valid_count > 0:
            confidence_score += (avg_response_length / 150) * 40  # Length indicates confidence
            confidence_score += (completion_rate * 35)  # Answering questions shows confidence
            # Consistency bonus - if all responses are similar length
            if valid_count > 1:
                lengths = [len(r.transcript) for r in valid_responses]
                avg_len = sum(lengths) / len(lengths)
                variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
                if variance < 10000:  # Low variance = consistent
                    confidence_score += 10
        confidence_score = min(100, confidence_score)
        
        # Completeness score
        completeness_score = (valid_count / total_responses) * 100 if total_responses > 0 else 0
        
        return {
            "communication": round(communication_score, 1),
            "technical": round(technical_score, 1),
            "confidence": round(confidence_score, 1),
            "completeness": round(completeness_score, 1)
        }
    
    def _extract_technical_keywords(self, job_role: str, focus_areas: List[str], job_description: str = "") -> List[str]:
        """Extract technical keywords based on job role, focus areas, and job description"""
        keywords = []
        
        # Job role specific keywords - expanded list
        role_keywords = {
            "software engineer": ["programming", "code", "algorithm", "data structure", "debugging", "testing", 
                                 "api", "database", "git", "agile", "scrum", "python", "java", "javascript",
                                 "framework", "architecture", "design pattern", "optimization", "performance"],
            "software developer": ["programming", "code", "development", "api", "testing", "debugging",
                                  "frontend", "backend", "database", "git", "deploy", "framework"],
            "data scientist": ["machine learning", "statistics", "python", "r", "data analysis", "model",
                              "tensorflow", "pandas", "numpy", "visualization", "prediction", "classification"],
            "data analyst": ["data", "analysis", "sql", "excel", "visualization", "reporting", "insights",
                            "dashboard", "metrics", "trends", "statistics"],
            "product manager": ["strategy", "roadmap", "stakeholder", "metrics", "user experience", "agile",
                               "prioritization", "requirements", "mvp", "sprint", "backlog", "user story"],
            "designer": ["user experience", "ui", "ux", "prototype", "wireframe", "design system",
                        "figma", "sketch", "user research", "usability", "accessibility", "responsive"],
            "frontend": ["html", "css", "javascript", "react", "vue", "angular", "responsive", "ui",
                        "accessibility", "performance", "webpack", "npm"],
            "backend": ["api", "database", "server", "authentication", "authorization", "sql", "nosql",
                       "microservices", "rest", "graphql", "security", "scalability"],
            "devops": ["deployment", "ci/cd", "docker", "kubernetes", "aws", "azure", "terraform",
                      "monitoring", "automation", "infrastructure", "pipeline"],
            "full stack": ["frontend", "backend", "database", "api", "deployment", "full stack",
                          "javascript", "react", "node", "mongodb", "sql"]
        }
        
        job_role_lower = job_role.lower()
        for role, words in role_keywords.items():
            if role in job_role_lower:
                keywords.extend(words)
        
        # Extract keywords from job description
        if job_description:
            common_tech_terms = ["experience", "project", "team", "lead", "develop", "implement",
                                "design", "build", "create", "optimize", "improve", "manage",
                                "collaborate", "communicate", "problem", "solution", "skill"]
            desc_lower = job_description.lower()
            for term in common_tech_terms:
                if term in desc_lower:
                    keywords.append(term)
        
        # Add focus area keywords
        if focus_areas:
            if isinstance(focus_areas, list):
                keywords.extend(focus_areas)
            elif isinstance(focus_areas, str):
                keywords.extend(focus_areas.split(','))
        
        # Always include some generic professional keywords
        keywords.extend(["experience", "project", "team", "result", "challenge", "solution"])
        
        return list(set(keywords))  # Remove duplicates
    
    def _calculate_technical_score(self, responses: List, keywords: List[str]) -> float:
        """Calculate technical score based on keyword usage"""
        if not responses or not keywords:
            return 0
        
        total_score = 0
        valid_responses = 0
        
        for response in responses:
            if not response.transcript or response.transcript.startswith("["):
                continue
            
            valid_responses += 1
            response_lower = response.transcript.lower()
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in response_lower)
            # Calculate percentage but cap contribution per-response
            match_percentage = min(100, (keyword_matches / max(1, len(keywords))) * 150)  # Boost multiplier
            total_score += match_percentage
        
        if valid_responses == 0:
            return 0
            
        return total_score / valid_responses
    
    def _calculate_duration(self, start_time: datetime, end_time: datetime) -> int:
        """Calculate duration in minutes"""
        if not start_time or not end_time:
            return 0
        
        duration = end_time - start_time
        return int(duration.total_seconds() / 60)
    
    def _calculate_overall_rating(self, scores: Dict[str, float]) -> str:
        """Calculate overall rating based on scores"""
        avg_score = sum(scores.values()) / len(scores)
        
        if avg_score >= 90:
            return "Excellent"
        elif avg_score >= 80:
            return "Good"
        elif avg_score >= 70:
            return "Satisfactory"
        elif avg_score >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
    
    async def save_report(self, session_id: str, report: Dict[str, Any]) -> str:
        """Save report to database"""
        try:
            # In a real implementation, you would save this to a reports table
            # For now, we'll just log it
            logger.info(f"Report generated for session {session_id}: {report['overall_rating']}")
            return f"report_{session_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        except Exception as e:
            logger.error(f"Failed to save report for session {session_id}: {e}")
            raise

# Create service instance
report_service = None

# Factory function to get report service with db session
def get_report_service(db_session):
    """Factory function to get report service with db session"""
    # Create new instance each time to ensure correct db session is used
    return ReportService(db_session)



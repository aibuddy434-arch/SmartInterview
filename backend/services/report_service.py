import logging
import asyncio
import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv
import json
import aiohttp

# Load .env file first!
load_dotenv()

from app.repositories.session_repository import SessionRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.interview_repository import InterviewRepository
from models.interview import InterviewSession
from models.candidate import Candidate

logger = logging.getLogger(__name__)

# Read API keys from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# OpenRouter (Primary)
openrouter_service = None
try:
    from services.openrouter_service import openrouter_service as _openrouter_service
    if OPENROUTER_API_KEY:
        openrouter_service = _openrouter_service
        logger.info(f"✅ OpenRouter configured for report analysis (Primary)")
except ImportError as e:
    logger.warning(f"OpenRouter not available: {e}")

# Groq (Fallback)
if GROQ_API_KEY:
    logger.info(f"✅ Groq API key loaded (Fallback)")
else:
    logger.warning("❌ GROQ_API_KEY not found")

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
            
            # Build Q&A pairs for AI analysis
            # Track follow-up counts per preset question for labeling
            preset_followup_counts = {}  # {preset_qnum: count}
            qa_pairs = []
            display_number = 1
            
            for response in responses:
                q_index = response.question_number - 1  # 0-based index
                
                # Use stored question_text if available, fallback to preset lookup
                question_text = getattr(response, 'question_text', None) or ""
                question_type = getattr(response, 'question_type', None) or "preset"
                question_tags = []
                
                # Get tags from preset if it's a preset question
                if question_type == "preset" and 0 <= q_index < len(questions):
                    if not question_text:
                        question_text = questions[q_index].text
                    question_tags = questions[q_index].tags or []
                
                # Build display label (e.g., "Q1", "Q1 Follow-up 1", "Resume Question")
                if question_type == "follow_up":
                    preset_qnum = response.question_number
                    if preset_qnum not in preset_followup_counts:
                        preset_followup_counts[preset_qnum] = 0
                    preset_followup_counts[preset_qnum] += 1
                    display_label = f"Q{preset_qnum} Follow-up {preset_followup_counts[preset_qnum]}"
                elif question_type == "resume":
                    display_label = "Resume Question"
                else:
                    display_label = f"Q{display_number}"
                    display_number += 1
                
                qa_pairs.append({
                    "question_number": response.question_number,
                    "display_label": display_label,  # NEW: Human-readable label
                    "question_type": question_type,  # NEW: preset/follow_up/resume
                    "question_text": question_text,
                    "question_tags": question_tags,
                    "candidate_answer": response.transcript or "[No response recorded]",
                    "audio_path": response.audio_path
                })
            
            # Try AI-powered analysis first, fall back to heuristics
            if GROQ_API_KEY and qa_pairs:
                try:
                    logger.info(f"Using AI-powered analysis for session {session_id}")
                    ai_analysis = await self._analyze_with_ai(
                        qa_pairs, 
                        interview_config.job_role, 
                        interview_config.job_description
                    )
                    
                    # Use AI analysis results
                    detailed_responses = ai_analysis.get("detailed_responses", [])
                    scores = ai_analysis.get("scores", {})
                    overall_assessment = ai_analysis.get("overall_assessment", {})
                    
                except Exception as e:
                    logger.error(f"AI analysis failed, falling back to heuristics: {e}")
                    detailed_responses, scores, overall_assessment = await self._analyze_with_heuristics(
                        qa_pairs, responses, interview_config
                    )
            else:
                logger.info(f"Using heuristic-based analysis for session {session_id}")
                detailed_responses, scores, overall_assessment = await self._analyze_with_heuristics(
                    qa_pairs, responses, interview_config
                )
            
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
    
    async def _analyze_with_ai(self, qa_pairs: List[Dict], job_role: str, job_description: str) -> Dict[str, Any]:
        """Use Groq LLM to analyze interview responses with comprehensive dynamic analysis"""
        
        logger.info(f"Starting comprehensive AI analysis for {len(qa_pairs)} Q&A pairs")
        
        # Build the Q&A text with full context
        qa_text = ""
        for qa in qa_pairs:
            answer = qa['candidate_answer']
            if len(answer) > 600:
                answer = answer[:600] + "..."
            qa_text += f"\nQ{qa['question_number']}: {qa['question_text']}\n"
            qa_text += f"A{qa['question_number']}: {answer}\n"
        
        # Comprehensive prompt for dynamic report generation
        prompt = f"""Analyze this interview for a {job_role} position and provide a COMPREHENSIVE evaluation.

JOB DESCRIPTION: {job_description[:500]}

INTERVIEW TRANSCRIPT:
{qa_text}

You MUST return this EXACT JSON structure with your analysis:

{{
  "scores": {{
    "communication": 0,
    "technical": 0,
    "problem_solving": 0,
    "confidence": 0,
    "relevance": 0,
    "depth": 0
  }},
  "per_answer_analysis": [
    {{
      "q_num": 1,
      "quality": "Good",
      "key_points": ["Point 1 from answer", "Point 2 from answer", "Point 3 from answer"],
      "improvement": "Specific suggestion for this answer"
    }}
  ],
  "key_insights": [
    "Insight 1 based on actual interview content",
    "Insight 2 based on actual interview content",
    "Insight 3 based on actual interview content"
  ],
  "strengths": [
    "Specific strength based on their answers",
    "Another specific strength"
  ],
  "weaknesses": [
    "Specific area needing improvement",
    "Another area to work on"
  ],
  "candidate_mastery": [
    "Best skill/strength shown in interview",
    "Second best skill demonstrated"
  ],
  "verdict": "pass",
  "recommendation": "Detailed 1-2 sentence hiring recommendation"
}}

SCORING GUIDE (0-100):
- communication: Clarity, structure, articulation of answers
- technical: Depth of technical knowledge for {job_role}
- problem_solving: Analytical thinking, approach to challenges
- confidence: Assertiveness, conviction in responses
- relevance: How well answers relate to the job requirements
- depth: Detail level, specific examples, quantified results

QUALITY RATINGS: "Excellent", "Good", "Average", "Needs Improvement", "Poor"

⚠️ CRITICAL RULES FOR per_answer_analysis:

1. **EACH ANSWER MUST HAVE DIFFERENT key_points!** 
   - key_points MUST be 2-4 short phrases (max 10 words each)
   - Extract keywords/concepts from THAT SPECIFIC answer ONLY
   - Do NOT copy key_points from one answer to another!
   - If Q1 is about "machine learning" and Q2 is about "hyperspectral imaging", they CANNOT have the same key_points!

2. Example for different questions:
   - Q1 (about ML): ["Model accuracy", "Training data", "Overfitting"]
   - Q2 (about NLP): ["Sentiment analysis", "Tokenization", "Chatbot response"]
   - Q3 (about computer vision): ["Object detection", "Image preprocessing", "CNN architecture"]

3. improvement MUST be SPECIFIC to that answer (not generic advice)
4. key_insights MUST reference actual content from their answers
5. strengths/weaknesses MUST be based on demonstrated behavior
6. If answer was empty/failed, give it "Poor" quality with key_points: ["No response provided"]

⚠️ NEVER use the same key_points for multiple questions! Each question's key_points must be UNIQUE!

Return ONLY valid JSON. No markdown. No extra text."""

        # --- Try OpenRouter FIRST (Primary) ---
        global openrouter_service
        if openrouter_service:
            try:
                logger.info("[OpenRouter] Sending report analysis request...")
                ai_result = await openrouter_service.generate_report_analysis(prompt)
                logger.info(f"[OpenRouter] Report analysis successful")
                return self._process_ai_analysis(ai_result, qa_pairs)
            except Exception as e:
                logger.error(f"[OpenRouter] Report analysis failed: {e}")
        
        # --- Fallback to Groq ---
        logger.info("[Groq] Sending report analysis request (OpenRouter failed)...")
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "You are an expert interview analyst. Output ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"}
                }
                
                async with session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    response_status = response.status
                    response_text = await response.text()
                    
                    logger.info(f"Groq API response status: {response_status}")
                    
                    if response_status != 200:
                        logger.error(f"Groq API error: {response_status} - {response_text}")
                        raise RuntimeError(f"Groq API error: {response_status}")
                    
                    result = json.loads(response_text)
                    content = result["choices"][0]["message"]["content"]
                    
                    logger.info(f"Groq raw response length: {len(content)} chars")
                    
                    # Parse the comprehensive JSON response
                    ai_result = json.loads(content)
                    
                    # Extract and validate scores
                    scores = ai_result.get("scores", {})
                    final_scores = {
                        "communication": min(100, max(0, int(scores.get("communication", 50)))),
                        "technical": min(100, max(0, int(scores.get("technical", 50)))),
                        "problem_solving": min(100, max(0, int(scores.get("problem_solving", 50)))),
                        "confidence": min(100, max(0, int(scores.get("confidence", 50)))),
                        "relevance": min(100, max(0, int(scores.get("relevance", 50)))),
                        "depth": min(100, max(0, int(scores.get("depth", 50))))
                    }
                    
                    # Get per-answer analysis from AI
                    per_answer = ai_result.get("per_answer_analysis", [])
                    
                    # Build detailed responses with AI-generated insights
                    detailed_responses = []
                    for i, qa in enumerate(qa_pairs):
                        # Find matching AI analysis for this question
                        ai_analysis = next(
                            (a for a in per_answer if a.get("q_num") == qa["question_number"]),
                            {"quality": "Average", "key_points": ["Response recorded"], "improvement": "Add more detail"}
                        )
                        
                        # Handle both old key_point (string) and new key_points (array) formats
                        key_points = ai_analysis.get("key_points", [])
                        if not key_points:
                            # Fallback to old format
                            old_key_point = ai_analysis.get("key_point", "Response provided")
                            key_points = [old_key_point] if old_key_point else ["Response provided"]
                        
                        detailed_responses.append({
                            "question_number": qa["question_number"],
                            "question_text": qa["question_text"],
                            "question_tags": qa["question_tags"],
                            "candidate_answer": qa["candidate_answer"],
                            "audio_path": qa.get("audio_path"),
                            "answer_quality": ai_analysis.get("quality", "Average"),
                            "key_points": key_points,
                            "improvement_areas": [ai_analysis.get("improvement", "Continue practicing")]
                        })
                    
                    # Calculate average score
                    avg_score = sum(final_scores.values()) / len(final_scores)
                    
                    # Get AI-generated insights and assessment
                    key_insights = ai_result.get("key_insights", ["Interview completed"])
                    strengths = ai_result.get("strengths", ["Shows potential"])
                    weaknesses = ai_result.get("weaknesses", ["Room for improvement"])
                    candidate_mastery = ai_result.get("candidate_mastery", ["Skills demonstrated"])
                    
                    # Generate recommendation
                    if avg_score >= 80:
                        rec = "Strongly Recommend"
                    elif avg_score >= 65:
                        rec = "Recommend"
                    elif avg_score >= 50:
                        rec = "Consider with Training"
                    elif avg_score >= 35:
                        rec = "Consider for Junior Role"
                    else:
                        rec = "Not Recommended"
                    
                    ai_recommendation = ai_result.get("recommendation", f"Based on overall performance score of {avg_score:.0f}%")
                    
                    overall_assessment = {
                        "key_insights": key_insights[:5],  # Max 5 insights
                        "strengths": strengths[:4],  # Max 4 strengths
                        "areas_for_improvement": weaknesses[:4],  # Max 4 weaknesses
                        "candidate_mastery": candidate_mastery[:3],  # Max 3 mastery points
                        "recommendation": rec,
                        "recommendation_detail": ai_recommendation,
                        "average_score": round(avg_score, 1),
                        "verdict": ai_result.get("verdict", "pending")
                    }
                    
                    logger.info(f"Comprehensive AI analysis successful. Scores: {final_scores}")
                    
                    return {
                        "detailed_responses": detailed_responses,
                        "scores": final_scores,
                        "overall_assessment": overall_assessment
                    }
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            raise
        except asyncio.TimeoutError:
            logger.error("Groq API request timed out")
            raise
        except Exception as e:
            logger.error(f"AI analysis failed: {type(e).__name__}: {e}")
            raise
    
    def _process_ai_analysis(self, ai_result: Dict, qa_pairs: List[Dict]) -> Dict[str, Any]:
        """Process AI analysis result (used by both OpenRouter and Groq)."""
        # Extract and validate scores
        scores = ai_result.get("scores", {})
        final_scores = {
            "communication": min(100, max(0, int(scores.get("communication", 50)))),
            "technical": min(100, max(0, int(scores.get("technical", 50)))),
            "problem_solving": min(100, max(0, int(scores.get("problem_solving", 50)))),
            "confidence": min(100, max(0, int(scores.get("confidence", 50)))),
            "relevance": min(100, max(0, int(scores.get("relevance", 50)))),
            "depth": min(100, max(0, int(scores.get("depth", 50))))
        }
        
        # Get per-answer analysis from AI
        per_answer = ai_result.get("per_answer_analysis", [])
        
        # Build detailed responses with AI-generated insights
        detailed_responses = []
        for i, qa in enumerate(qa_pairs):
            ai_analysis = next(
                (a for a in per_answer if a.get("q_num") == qa["question_number"]),
                {"quality": "Average", "key_points": ["Response recorded"], "improvement": "Add more detail"}
            )
            
            key_points = ai_analysis.get("key_points", [])
            if not key_points:
                old_key_point = ai_analysis.get("key_point", "Response provided")
                key_points = [old_key_point] if old_key_point else ["Response provided"]
            
            detailed_responses.append({
                "question_number": qa["question_number"],
                "display_label": qa.get("display_label", f"Q{qa['question_number']}"),  # NEW
                "question_type": qa.get("question_type", "preset"),  # NEW
                "question_text": qa["question_text"],
                "question_tags": qa["question_tags"],
                "candidate_answer": qa["candidate_answer"],
                "audio_path": qa.get("audio_path"),
                "answer_quality": ai_analysis.get("quality", "Average"),
                "key_points": key_points,
                "improvement_areas": [ai_analysis.get("improvement", "Continue practicing")]
            })
        
        # Calculate average score
        avg_score = sum(final_scores.values()) / len(final_scores)
        
        # Get AI-generated insights and assessment
        key_insights = ai_result.get("key_insights", ["Interview completed"])
        strengths = ai_result.get("strengths", ["Shows potential"])
        weaknesses = ai_result.get("weaknesses", ["Room for improvement"])
        candidate_mastery = ai_result.get("candidate_mastery", ["Skills demonstrated"])
        
        # Generate recommendation
        if avg_score >= 80:
            rec = "Strongly Recommend"
        elif avg_score >= 65:
            rec = "Recommend"
        elif avg_score >= 50:
            rec = "Consider with Training"
        elif avg_score >= 35:
            rec = "Consider for Junior Role"
        else:
            rec = "Not Recommended"
        
        ai_recommendation = ai_result.get("recommendation", f"Based on overall performance score of {avg_score:.0f}%")
        
        overall_assessment = {
            "key_insights": key_insights[:5],
            "strengths": strengths[:4],
            "areas_for_improvement": weaknesses[:4],
            "candidate_mastery": candidate_mastery[:3],
            "recommendation": rec,
            "recommendation_detail": ai_recommendation,
            "average_score": round(avg_score, 1),
            "verdict": ai_result.get("verdict", "pending")
        }
        
        logger.info(f"AI analysis processed. Scores: {final_scores}")
        
        return {
            "detailed_responses": detailed_responses,
            "scores": final_scores,
            "overall_assessment": overall_assessment
        }
    
    async def _analyze_with_heuristics(self, qa_pairs: List[Dict], responses: List, interview_config) -> tuple:
        """Fallback heuristic-based analysis"""
        detailed_responses = []
        for qa in qa_pairs:
            analysis = self._analyze_response(qa["candidate_answer"], qa["question_text"], interview_config.job_role)
            detailed_responses.append({
                "question_number": qa["question_number"],
                "display_label": qa.get("display_label", f"Q{qa['question_number']}"),  # NEW
                "question_type": qa.get("question_type", "preset"),  # NEW
                "question_text": qa["question_text"],
                "question_tags": qa["question_tags"],
                "candidate_answer": qa["candidate_answer"],
                "audio_path": qa.get("audio_path"),
                "answer_quality": analysis.get("quality", "Unknown"),
                "key_points": analysis.get("key_points", []),
                "improvement_areas": analysis.get("improvements", [])
            })
        
        scores = await self._calculate_scores(responses, interview_config)
        overall_assessment = self._generate_assessment(scores, detailed_responses, interview_config.job_role)
        
        return detailed_responses, scores, overall_assessment
    
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
        """Generate overall assessment summary with dynamic insights"""
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        
        strengths = []
        weaknesses = []
        key_insights = []
        candidate_mastery = []
        
        # Analyze each score category
        if scores.get("communication", 0) >= 70:
            strengths.append("Clear and articulate communication")
            candidate_mastery.append("Strong verbal communication")
        elif scores.get("communication", 0) >= 50:
            key_insights.append("Communication is adequate but could be more structured")
        else:
            weaknesses.append("Work on clearer answer structure")
        
        if scores.get("technical", 0) >= 70:
            strengths.append(f"Solid technical knowledge for {job_role}")
            candidate_mastery.append(f"Technical competence in {job_role} domain")
        elif scores.get("technical", 0) >= 50:
            key_insights.append("Has foundational technical knowledge")
        else:
            weaknesses.append("Deepen technical expertise")
        
        if scores.get("problem_solving", 0) >= 70:
            strengths.append("Good analytical and problem-solving approach")
        elif scores.get("problem_solving", 0) < 50:
            weaknesses.append("Practice structured problem-solving")
        
        if scores.get("confidence", 0) >= 70:
            strengths.append("Confident and assertive presentation")
        elif scores.get("confidence", 0) < 50:
            weaknesses.append("Project more confidence in responses")
        
        if scores.get("relevance", 0) >= 70:
            key_insights.append("Answers were highly relevant to job requirements")
        elif scores.get("relevance", 0) < 50:
            weaknesses.append("Focus answers more on job-specific requirements")
        
        if scores.get("depth", 0) >= 70:
            strengths.append("Provides detailed, specific examples")
        elif scores.get("depth", 0) < 50:
            weaknesses.append("Include more specific examples and details")
        
        # Generate key insights from responses
        valid_responses = [r for r in responses if r.get("answer_quality") in ["Excellent", "Good"]]
        if len(valid_responses) >= len(responses) * 0.7:
            key_insights.append("Consistently good performance across questions")
        elif len(valid_responses) < len(responses) * 0.3:
            key_insights.append("Performance was inconsistent across questions")
        
        # Hiring recommendation
        if avg_score >= 80:
            recommendation = "Strongly Recommend"
            recommendation_detail = f"Excellent fit for {job_role}. Demonstrated strong skills across all areas."
        elif avg_score >= 65:
            recommendation = "Recommend"
            recommendation_detail = f"Good candidate for {job_role} with potential for growth."
        elif avg_score >= 50:
            recommendation = "Consider with Training"
            recommendation_detail = f"Has potential but would benefit from mentorship in {job_role} role."
        elif avg_score >= 35:
            recommendation = "Consider for Junior Role"
            recommendation_detail = "May suit a more entry-level position."
        else:
            recommendation = "Not Recommended"
            recommendation_detail = "Current skill level does not meet requirements."
        
        return {
            "key_insights": key_insights[:5] if key_insights else ["Interview completed - review individual responses for details"],
            "strengths": strengths[:4] if strengths else ["Shows willingness to learn"],
            "areas_for_improvement": weaknesses[:4] if weaknesses else ["General skill development recommended"],
            "candidate_mastery": candidate_mastery[:3] if candidate_mastery else ["Potential identified in interview"],
            "recommendation": recommendation,
            "recommendation_detail": recommendation_detail,
            "average_score": round(avg_score, 1)
        }

    
    async def _calculate_scores(self, responses: List, interview_config) -> Dict[str, Any]:
        """Calculate 6-dimension scores based on responses"""
        if not responses:
            return {
                "communication": 0,
                "technical": 0,
                "problem_solving": 0,
                "confidence": 0,
                "relevance": 0,
                "depth": 0
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
        
        # 1. Communication score (clarity, structure, articulation)
        communication_score = 20
        if valid_count > 0:
            communication_score += (completion_rate * 35)
            communication_score += min(25, (avg_response_length / 100) * 25)
            sentences_per_response = sum(r.transcript.count('.') + r.transcript.count('!') + r.transcript.count('?') 
                                        for r in valid_responses) / valid_count
            communication_score += min(20, sentences_per_response * 4)
        communication_score = min(100, communication_score)
        
        # 2. Technical score (domain knowledge)
        technical_keywords = self._extract_technical_keywords(
            interview_config.job_role, 
            interview_config.focus,
            interview_config.job_description if hasattr(interview_config, 'job_description') else ""
        )
        technical_score = self._calculate_technical_score(valid_responses if valid_responses else responses, technical_keywords)
        if valid_count > 0 and technical_score < 20:
            technical_score = 20 + (completion_rate * 15)
        
        # 3. Problem-solving score (analytical approach, structured thinking)
        problem_keywords = ["because", "therefore", "approach", "solution", "solved", "analyzed", "considered", 
                           "first", "then", "finally", "step", "process", "method", "strategy"]
        problem_score = 25
        if valid_count > 0:
            problem_matches = sum(1 for r in valid_responses 
                                 for kw in problem_keywords if kw in r.transcript.lower())
            problem_score += min(50, (problem_matches / valid_count) * 15)
            problem_score += (completion_rate * 25)
        problem_score = min(100, problem_score)
        
        # 4. Confidence score (assertiveness, conviction)
        confidence_score = 20
        if valid_count > 0:
            confidence_score += (avg_response_length / 150) * 35
            confidence_score += (completion_rate * 30)
            if valid_count > 1:
                lengths = [len(r.transcript) for r in valid_responses]
                avg_len = sum(lengths) / len(lengths)
                variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
                if variance < 10000:
                    confidence_score += 15
        confidence_score = min(100, confidence_score)
        
        # 5. Relevance score (job-related content)
        job_keywords = interview_config.job_role.lower().split() + \
                      (interview_config.focus if isinstance(interview_config.focus, list) else [])
        relevance_score = 30
        if valid_count > 0:
            relevance_matches = sum(1 for r in valid_responses 
                                   for kw in job_keywords if kw.lower() in r.transcript.lower())
            relevance_score += min(50, (relevance_matches / max(1, valid_count)) * 20)
            relevance_score += (completion_rate * 20)
        relevance_score = min(100, relevance_score)
        
        # 6. Depth score (specific examples, quantified results)
        depth_keywords = ["example", "specifically", "percent", "%", "increased", "decreased", 
                         "project", "result", "outcome", "achieved", "number", "million", "thousand"]
        depth_score = 25
        if valid_count > 0:
            depth_matches = sum(1 for r in valid_responses 
                               for kw in depth_keywords if kw in r.transcript.lower())
            depth_score += min(45, (depth_matches / valid_count) * 15)
            depth_score += min(30, (avg_response_length / 200) * 30)
        depth_score = min(100, depth_score)
        
        return {
            "communication": round(communication_score, 1),
            "technical": round(technical_score, 1),
            "problem_solving": round(problem_score, 1),
            "confidence": round(confidence_score, 1),
            "relevance": round(relevance_score, 1),
            "depth": round(depth_score, 1)
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



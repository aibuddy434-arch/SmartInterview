import logging
import random
import asyncio
import aiohttp
import os
from typing import List, Dict, Any, Optional
from models.interview import Question, FocusArea, DifficultyLevel, InterviewConfig
import json
from enum import Enum
from dotenv import load_dotenv

# Load .env file FIRST
load_dotenv()

logger = logging.getLogger(__name__)

# Read API keys directly from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Google AI (Gemini) - PRIMARY (Best free tier!) ---
google_ai_available = False
gemini_model = None
try:
    import google.generativeai as genai
    if GOOGLE_API_KEY:
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            gemini_model = genai.GenerativeModel(model_name=os.getenv("GOOGLE_MODEL_NAME", "gemini-2.0-flash"))
            google_ai_available = True
            logger.info(f"✅ Google AI (Gemini) configured (PRIMARY)")
        except Exception as e:
            logger.error(f"Failed to configure Google AI: {e}")
    else:
        logger.warning("GOOGLE_API_KEY not set")
except ImportError:
    logger.warning("Google AI library not installed")

# --- Groq (Fallback #1) ---
if GROQ_API_KEY:
    logger.info(f"✅ Groq API key loaded (Fallback #1)")
else:
    logger.warning("❌ GROQ_API_KEY not found")

# --- OpenRouter (Fallback #2 - Optional backup) ---
openrouter_available = False
openrouter_service = None
try:
    from services.openrouter_service import openrouter_service as _openrouter_service
    if OPENROUTER_API_KEY:
        openrouter_service = _openrouter_service
        openrouter_available = True
        logger.info(f"✅ OpenRouter API configured (Fallback #2)")
    else:
        logger.info("OpenRouter not configured (optional)")
except ImportError as e:
    logger.info(f"OpenRouter not available (optional): {e}")
# --- End LLM Initialization ---

class AIQuestionService:
    def __init__(self):
        # Keep template questions as a fallback or for initial generation
        self.template_questions = {
            "communication": {
                "easy": [
                    "Can you tell me about yourself?",
                    "What are your strengths and weaknesses?",
                    "Why are you interested in this position?",
                    "Where do you see yourself in 5 years?",
                    "Describe a challenging situation you faced at work."
                ],
                "medium": [
                    "How do you handle constructive criticism?",
                    "Tell me about a time you had to explain a complex concept to someone.",
                    "How do you prioritize your work when you have multiple deadlines?",
                    "Describe a situation where you had to work with a difficult colleague.",
                    "How do you stay motivated during challenging projects?"
                ],
                "hard": [
                    "How would you handle a situation where your manager disagrees with your approach?",
                    "Describe a time when you had to influence stakeholders without direct authority.",
                    "How do you handle situations where you need to deliver bad news?",
                    "Tell me about a time you had to resolve a conflict between team members.",
                    "How do you ensure effective communication in a remote team setting?"
                ]
            },
            "technical": {
                "easy": [
                    "What programming languages are you most comfortable with?",
                    "Can you explain the difference between frontend and backend development?",
                    "What is version control and why is it important?",
                    "Describe a simple project you've worked on.",
                    "What tools do you use for debugging?"
                ],
                "medium": [
                    "Explain the concept of RESTful APIs.",
                    "How would you optimize a slow-performing database query?",
                    "Describe your experience with testing methodologies.",
                    "How do you handle security in your applications?",
                    "Explain the difference between synchronous and asynchronous operations."
                ],
                "hard": [
                    "How would you design a scalable microservices architecture?",
                    "Explain how you would implement a caching strategy for a high-traffic application.",
                    "Describe your approach to handling distributed system failures.",
                    "How would you design a system to handle millions of concurrent users?",
                    "Explain your strategy for database sharding and partitioning."
                ]
            },
            "overall": {
                "easy": [
                    "What motivates you in your work?",
                    "How do you handle stress and pressure?",
                    "What do you do to stay updated with industry trends?",
                    "How do you approach learning new technologies?",
                    "What's your preferred work environment?"
                ],
                "medium": [
                    "How do you balance quality with speed in your work?",
                    "Describe your ideal team dynamic.",
                    "How do you handle ambiguity in project requirements?",
                    "What's your approach to mentoring junior developers?",
                    "How do you measure success in your projects?"
                ],
                "hard": [
                    "How would you lead a team through a major technical transition?",
                    "Describe your strategy for managing technical debt.",
                    "How do you approach making architectural decisions?",
                    "What's your philosophy on code quality vs. delivery speed?",
                    "How would you handle a situation where business requirements conflict with technical best practices?"
                ]
            }
        }


    # --- NEW: Main generate_questions function ---
    async def generate_questions(
        self,
        job_role: str,
        job_description: str,
        focus_areas: List[FocusArea],
        difficulty: DifficultyLevel,
        number_of_questions: int
    ) -> List[Question]:
        """
        Generate INITIAL interview questions.
        Tries to use Google AI (Gemini) first, then Groq, then falls back to templates.
        """
        global google_ai_available, gemini_model, groq_available, groq_api_key
        
        focus_area_strings = [area.value if isinstance(area, Enum) else area for area in focus_areas]
        difficulty_string = difficulty.value if isinstance(difficulty, Enum) else difficulty

        prompt = self._build_initial_questions_prompt(
            job_role, job_description, focus_area_strings, difficulty_string, number_of_questions
        )

        # Try Google AI first
        if google_ai_available and gemini_model:
            try:
                logger.info(f"Attempting to generate questions using Google AI for job: {job_role}")

                generation_config = genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048, # Allow for more tokens for a list
                    response_mime_type="application/json" # Request JSON
                )

                response = await gemini_model.generate_content_async(
                    prompt,
                    generation_config=generation_config
                )

                # Extract and parse JSON response
                llm_response_content = ""
                if response.parts:
                    llm_response_content = "".join(part.text for part in response.parts if hasattr(part, 'text'))
                elif hasattr(response, 'text'):
                     llm_response_content = response.text
                
                llm_response_content = llm_response_content.strip().lstrip('```json').rstrip('```').strip()
                logger.info(f"Received raw question generation response from Google AI: {llm_response_content}")
                
                response_data = json.loads(llm_response_content)
                questions_data = response_data.get("questions", [])

                if not questions_data or not isinstance(questions_data, list):
                     raise ValueError("AI returned invalid data format.")

                # Convert JSON to Question objects
                questions = []
                for q_data in questions_data:
                    if isinstance(q_data, dict) and "text" in q_data and "tags" in q_data:
                        # Get AI-suggested time, default to 120 seconds if not provided
                        suggested_time = q_data.get("suggested_time_seconds", 120)
                        # Clamp time between 60-180 seconds
                        suggested_time = max(60, min(180, suggested_time))
                        
                        questions.append(Question(
                            text=q_data["text"],
                            tags=q_data["tags"],
                            generated_by="ai",
                            suggested_time_seconds=suggested_time
                        ))
                
                if questions:
                     logger.info(f"Successfully generated {len(questions)} questions using Google AI with dynamic timing.")
                     return questions[:number_of_questions] # Return exact number
                else:
                    logger.warning("AI generation succeeded but returned no questions.")

            except Exception as e:
                logger.error(f"Google AI question generation failed: {e}. Trying Groq fallback...")
        else:
            logger.warning("Google AI not available. Trying Groq fallback...")

        # Try Groq as fallback
        if GROQ_API_KEY:
            try:
                logger.info(f"Attempting to generate questions using Groq for job: {job_role}")
                questions = await self._generate_questions_with_groq(
                    prompt, focus_area_strings, number_of_questions
                )
                if questions:
                    return questions
            except Exception as e:
                logger.error(f"Groq question generation failed: {e}. Falling back to templates.")
        
        # --- Fallback Logic ---
        logger.warning("All LLMs failed. Using template questions.")
        return self._generate_template_questions(
            focus_areas, difficulty, number_of_questions
        )

    async def _generate_questions_with_groq(
        self, 
        prompt: str, 
        focus_areas: List[str], 
        number_of_questions: int
    ) -> List[Question]:
        """Generate questions using Groq API as fallback"""
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are an expert interview question creator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "response_format": {"type": "json_object"}
            }
            
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Groq API error: {response.status} - {error_text}")
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse the JSON response
                response_data = json.loads(content)
                questions_data = response_data.get("questions", [])
                
                questions = []
                for q_data in questions_data:
                    if isinstance(q_data, dict) and "text" in q_data:
                        tags = q_data.get("tags", focus_areas[:1] if focus_areas else ["general"])
                        # Get AI-suggested time, default to 120 seconds if not provided
                        suggested_time = q_data.get("suggested_time_seconds", 120)
                        # Clamp time between 60-180 seconds
                        suggested_time = max(60, min(180, suggested_time))
                        
                        questions.append(Question(
                            text=q_data["text"],
                            tags=tags,
                            generated_by="ai",
                            suggested_time_seconds=suggested_time
                        ))
                
                if questions:
                    logger.info(f"Successfully generated {len(questions)} questions using Groq with dynamic timing.")
                    return questions[:number_of_questions]
                
        return []

    # --- NEW: Helper for building the initial question prompt ---
    def _build_initial_questions_prompt(
        self,
        job_role: str,
        job_description: str,
        focus_areas: List[str],
        difficulty: str,
        number_of_questions: int
    ) -> str:
        """Helper to construct the prompt for initial question generation."""
        
        focus_areas_str = ", ".join(focus_areas)
        job_desc_snippet = job_description[:500] 

        prompt = f"""
        You are an AI assistant tasked with creating interview questions with appropriate time allocations.
        
        **Role Context:**
        - Job Role: {job_role}
        - Job Description: {job_desc_snippet}...
        - Focus Areas: {focus_areas_str}
        - Difficulty: {difficulty}
        - Number of Questions to Generate: {number_of_questions}

        **Your Task:**
        Generate exactly {number_of_questions} high-quality interview questions based *only* on the context provided.
        - Each question must be relevant to the job role, description, and focus areas.
        - The questions' difficulty must match '{difficulty}'.
        - For each question, you MUST provide a 'tags' list. Use the Focus Areas ({focus_areas_str}) as tags.
        - For each question, estimate the 'suggested_time_seconds' - how long a candidate should have to answer.
        
        **Time Allocation Guidelines:**
        - Simple behavioral questions: 60-90 seconds
        - Moderate technical questions: 90-120 seconds  
        - Complex technical/scenario questions: 120-180 seconds
        - Deep dive technical questions: 150-180 seconds
        
        **Respond ONLY with a valid JSON object with a single key "questions".**
        The value of "questions" must be a JSON list, where each item has "text", "tags", and "suggested_time_seconds" keys.

        **Example JSON Response:**
        {{
          "questions": [
            {{
              "text": "Can you describe a challenging {difficulty} project you completed using Python, as mentioned in the job description?",
              "tags": ["technical"],
              "suggested_time_seconds": 120
            }},
            {{
              "text": "How would you explain a complex technical concept to a non-technical stakeholder?",
              "tags": ["communication"],
              "suggested_time_seconds": 90
            }}
          ]
        }}

        **Your JSON Response:**
        """
        return prompt

    # --- NEW: Original logic refactored into this helper ---
    def _generate_template_questions(
        self,
        focus_areas: List[FocusArea],
        difficulty: DifficultyLevel,
        number_of_questions: int
    ) -> List[Question]:
        """Generate INITIAL interview questions using templates."""
        logger.info("Generating questions from templates (fallback).")
        questions = []
        
        # Simple logic to divide questions among focus areas
        q_per_area = (number_of_questions // len(focus_areas)) + 1 if focus_areas else number_of_questions
        
        for area in focus_areas:
            area_str = area.value if isinstance(area, Enum) else area
            q_texts = self._generate_focus_area_questions(area, difficulty, q_per_area)
            for text in q_texts:
                questions.append(Question(text=text, tags=[area_str], generated_by="template"))

        # Trim to the exact number requested
        final_questions = questions[:number_of_questions]
        
        # If not enough, add fallbacks
        if len(final_questions) < number_of_questions:
             needed = number_of_questions - len(final_questions)
             final_questions.extend(self._generate_fallback_questions(focus_areas, difficulty, needed))
             
        return final_questions[:number_of_questions]

    def _generate_focus_area_questions( # Keep this helper
        self,
        focus_area: FocusArea,
        difficulty: DifficultyLevel,
        count: int
    ) -> List[str]:
         # Ensure focus_area.value and difficulty.value are used correctly
        area_key = focus_area.value if isinstance(focus_area, Enum) else focus_area
        difficulty_key = difficulty.value if isinstance(difficulty, Enum) else difficulty
        
        questions = []
        if area_key in self.template_questions:
            difficulty_questions = self.template_questions[area_key].get(difficulty_key, [])
            if difficulty_questions:
                selected = random.sample(difficulty_questions, min(count, len(difficulty_questions)))
                questions.extend(selected)
        return questions

    def _generate_fallback_questions( # Keep this helper
        self,
        focus_areas: List[FocusArea],
        difficulty: DifficultyLevel,
        count: int
    ) -> List[Question]:
        fallback_texts = [
            "Tell me about your experience related to this role.",
            "What challenges do you anticipate in this position?",
            "How do you typically approach problem-solving?",
            "What are your long-term career aspirations?",
            "How do you respond to constructive feedback?"
        ]
        selected_texts = random.sample(fallback_texts, min(count, len(fallback_texts)))
        
        # Ensure focus_areas are strings for tags
        tags = [area.value if isinstance(area, Enum) else area for area in focus_areas]
        
        return [Question(text=text, tags=tags, generated_by="fallback") for text in selected_texts]
    # --- End of template helpers ---


    async def determine_next_step(
        self,
        interview_config: InterviewConfig,
        session_history: List[Dict[str, str]],
        current_question_index: int, # 0-based index of question JUST answered
        candidate_transcript: str,
        resume_text: str,
        elapsed_seconds: int = 0,  # NEW: How much time has passed
        time_limit_seconds: int = 600  # NEW: Total interview time in seconds
    ) -> Dict[str, Any]:
        """
        Analyzes the latest response and determines the next action.
        Priority: OpenRouter -> Gemini -> Groq -> Simple fallback
        Returns: Dict like {"action": "preset/follow_up/resume/complete", "question_text": "...", "next_index": #}
        """
        global google_ai_available, gemini_model, openrouter_available, openrouter_service
        
        prompt = self._build_llm_prompt(
            interview_config, session_history, current_question_index, candidate_transcript, resume_text,
            elapsed_seconds, time_limit_seconds  # Pass time info
        )
        
        # --- Try Gemini FIRST (Primary - Best FREE tier!) ---
        if google_ai_available and gemini_model is not None:
            try:
                logger.info(f"[Gemini] Determining next step (after Q index {current_question_index})...")
                return await self._determine_next_step_with_gemini(
                    interview_config, session_history, current_question_index,
                    candidate_transcript, resume_text, prompt,
                    elapsed_seconds, time_limit_seconds  # Pass time info
                )
            except Exception as e:
                logger.error(f"[Gemini] Failed: {e}")
        
        # --- Try Groq as Fallback #1 ---
        if GROQ_API_KEY:
            try:
                logger.info(f"[Groq] Determining next step (Gemini failed)...")
                return await self._determine_next_step_with_groq(
                    interview_config, session_history, current_question_index,
                    candidate_transcript, resume_text,
                    elapsed_seconds, time_limit_seconds  # Pass time info
                )
            except Exception as e:
                logger.error(f"[Groq] Failed: {e}")
        
        # --- Try OpenRouter as Fallback #2 (Optional backup) ---
        if openrouter_available and openrouter_service:
            try:
                logger.info(f"[OpenRouter] Determining next step (Groq failed)...")
                decision = await openrouter_service.generate_question_decision(prompt)
                logger.info(f"[OpenRouter] Decision: {decision}")
                remaining_seconds = max(0, time_limit_seconds - elapsed_seconds)
                return self._process_llm_decision(decision, interview_config, current_question_index, remaining_seconds)
            except Exception as e:
                logger.error(f"[OpenRouter] Failed: {e}")
        
        # --- Final fallback: simple next question logic ---
        logger.warning("All LLMs failed. Using simple next question logic.")
        next_preset_idx = current_question_index + 1
        remaining_seconds = max(0, time_limit_seconds - elapsed_seconds)
        suggested_time = min(120, remaining_seconds) if remaining_seconds > 0 else 120
        
        if next_preset_idx < len(interview_config.questions):
             return {
                 "action": "preset",
                 "question_text": interview_config.questions[next_preset_idx].text,
                 "next_index": next_preset_idx + 1,
                 "suggested_time_seconds": suggested_time
             }
        else:
             return {"action": "complete"}
    
    def _process_llm_decision(self, decision: Dict, interview_config: InterviewConfig, current_question_index: int, remaining_seconds: int = 600) -> Dict[str, Any]:
        """Process and validate LLM decision, ensuring all required fields are present."""
        action = decision.get("action", "preset")
        question_text = decision.get("question_text", "")
        suggested_time = decision.get("suggested_time_seconds", 120)
        
        # Clamp suggested time between 30s and 180s, but also cap to remaining time
        suggested_time = max(30, min(180, suggested_time))
        
        # CRITICAL: Don't assign more time than what's left in the interview!
        if remaining_seconds > 0:
            suggested_time = min(suggested_time, remaining_seconds)
        
        if action == "complete":
            return {"action": "complete"}
        
        elif action in ("follow_up", "resume"):
            if question_text:
                return {
                    "action": action,
                    "question_text": question_text,
                    "suggested_time_seconds": suggested_time
                }
            else:
                # No question text, fall back to preset
                action = "preset"
        
        # Default to preset
        if action == "preset":
            next_preset_idx = current_question_index + 1
            if next_preset_idx < len(interview_config.questions):
                return {
                    "action": "preset",
                    "question_text": question_text or interview_config.questions[next_preset_idx].text,
                    "next_index": next_preset_idx + 1,
                    "suggested_time_seconds": suggested_time
                }
            else:
                # All presets done - check if we should ask resume questions
                # The LLM should have already decided this, but if not, we complete
                if question_text and action in ("follow_up", "resume"):
                    return {
                        "action": "resume",
                        "question_text": question_text,
                        "suggested_time_seconds": suggested_time
                    }
                return {"action": "complete"}
        
        return {"action": "complete"}
    
    async def _determine_next_step_with_gemini(
        self,
        interview_config: InterviewConfig,
        session_history: List[Dict[str, str]],
        current_question_index: int,
        candidate_transcript: str,
        resume_text: str,
        prompt: str,
        elapsed_seconds: int = 0,
        time_limit_seconds: int = 600
    ) -> Dict[str, Any]:
        """Use Gemini for question decision (fallback from OpenRouter)."""
        global gemini_model

        try:
            prompt = self._build_llm_prompt(
                interview_config, session_history, current_question_index, candidate_transcript, resume_text,
                elapsed_seconds, time_limit_seconds
            )

            logger.info(f"Sending prompt to Google AI for session (after Q index {current_question_index})...")

            generation_config = genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=250, # Increased for safety
                response_mime_type="application/json" # Request JSON
            )

            response = await gemini_model.generate_content_async(
                prompt,
                generation_config=generation_config
            )

            llm_response_content = ""
            try:
                if response.parts:
                    llm_response_content = "".join(part.text for part in response.parts if hasattr(part, 'text'))
                elif hasattr(response, 'text'):
                     llm_response_content = response.text
                
                llm_response_content = llm_response_content.strip().lstrip('```json').rstrip('```').strip()
                logger.info(f"Received raw response text from Google AI: {llm_response_content}")
                decision = json.loads(llm_response_content) 

            except (AttributeError, IndexError, ValueError, json.JSONDecodeError) as parse_err:
                 logger.error(f"Failed to parse JSON response from Google AI: {parse_err}. Raw response: '{llm_response_content}'")
                 # Fallback to next preset question if parsing fails
                 next_preset_idx = current_question_index + 1
                 if next_preset_idx < len(interview_config.questions):
                      return {
                          "action": "preset",
                          "question_text": interview_config.questions[next_preset_idx].text,
                          "next_index": next_preset_idx + 1
                      }
                 else:
                      return self._get_next_preset_or_complete(interview_config, current_question_index)
            except Exception as resp_err:
                 logger.error(f"Error processing Google AI response: {resp_err}. Full response: {response}")
                 return self._get_next_preset_or_complete(interview_config, current_question_index)

            action = decision.get("action")
            next_step_data = {"action": action}
            logger.info(f"Parsed AI Action: {action}")

            # Calculate remaining preset questions
            next_preset_idx = current_question_index + 1  # 0-based index of NEXT preset Q
            has_remaining_presets = next_preset_idx < len(interview_config.questions)

            if action == "preset":
                if has_remaining_presets:
                    next_question = interview_config.questions[next_preset_idx]
                    next_step_data["question_text"] = next_question.text
                    next_step_data["next_index"] = next_preset_idx + 1  # 1-based index for DB
                    # Get suggested time from the preset question, default to 120s
                    next_step_data["suggested_time_seconds"] = getattr(next_question, 'suggested_time_seconds', 120) or 120
                else:
                    logger.warning("AI chose 'preset' but no pre-set questions remain. Completing.")
                    next_step_data["action"] = "complete"

            elif action == "follow_up" or action == "resume":
                generated_text = decision.get("question_text")
                if generated_text:
                    next_step_data["question_text"] = generated_text
                    # Keep the same preset index (don't advance yet)
                    next_step_data["next_index"] = current_question_index + 1  # 1-based index of CURRENT preset Q
                    # Get AI-suggested time for this follow-up, default to 90s, clamp between 30-180
                    suggested_time = decision.get("suggested_time_seconds", 90)
                    suggested_time = max(30, min(180, suggested_time))
                    # Cap to remaining interview time
                    remaining_secs = max(0, time_limit_seconds - elapsed_seconds)
                    if remaining_secs > 0:
                        suggested_time = min(suggested_time, remaining_secs)
                    next_step_data["suggested_time_seconds"] = suggested_time
                else:
                    # No question text provided, go to next preset
                    logger.warning(f"AI chose '{action}' but didn't provide question_text. Moving to next preset.")
                    return self._get_next_preset_or_complete(interview_config, current_question_index)

            elif action == "complete":
                # SMART CHECK: Only allow complete if ALL preset questions have been asked
                if has_remaining_presets:
                    logger.warning(f"AI chose 'complete' but {len(interview_config.questions) - next_preset_idx} preset questions remain. Forcing next preset.")
                    return self._get_next_preset_or_complete(interview_config, current_question_index)
                # Otherwise allow complete
                pass
            else:
                logger.error(f"Invalid action '{action}' received from AI. Moving to next preset.")
                return self._get_next_preset_or_complete(interview_config, current_question_index)

            logger.info(f"Final decision data: {next_step_data}")
            return next_step_data

        except Exception as e:
            logger.error(f"Error determining next step with Google AI: {e}")
            # Check for quota errors specifically
            if "quota" in str(e).lower():
                 logger.error("Google AI Quota Exceeded! Check your billing.")
            
            # Try Groq as fallback for follow-up questions
            if GROQ_API_KEY:
                try:
                    logger.info("Attempting Groq fallback for determine_next_step...")
                    return await self._determine_next_step_with_groq(
                        interview_config, session_history, current_question_index,
                        candidate_transcript, resume_text
                    )
                except Exception as groq_err:
                    logger.error(f"Groq fallback also failed: {groq_err}")
            
            # SMART FALLBACK: Go to next preset question instead of completing
            return self._get_next_preset_or_complete(interview_config, current_question_index)

    async def _determine_next_step_with_groq(
        self,
        interview_config,
        session_history: List[Dict[str, str]],
        current_question_index: int,
        candidate_transcript: str,
        resume_text: str,
        elapsed_seconds: int = 0,
        time_limit_seconds: int = 600
    ) -> Dict[str, Any]:
        """Use Groq API as fallback for determining next step with follow-up questions."""
        
        prompt = self._build_llm_prompt(
            interview_config, session_history, current_question_index, 
            candidate_transcript, resume_text,
            elapsed_seconds, time_limit_seconds
        )
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are an expert AI interviewer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 300,
                "response_format": {"type": "json_object"}
            }
            
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Groq API error: {response.status} - {error_text}")
                
                result = await response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Clean up the response
                content = content.strip().lstrip('```json').rstrip('```').strip()
                logger.info(f"Groq response for next step: {content}")
                
                decision = json.loads(content)
                action = decision.get("action")
                
                next_preset_idx = current_question_index + 1
                has_remaining_presets = next_preset_idx < len(interview_config.questions)
                
                if action == "follow_up" or action == "resume":
                    generated_text = decision.get("question_text")
                    if generated_text:
                        # Get AI-suggested time, default to 90s, clamp between 30-180
                        suggested_time = decision.get("suggested_time_seconds", 90)
                        suggested_time = max(30, min(180, suggested_time))
                        # Cap to remaining interview time
                        remaining_secs = max(0, time_limit_seconds - elapsed_seconds)
                        if remaining_secs > 0:
                            suggested_time = min(suggested_time, remaining_secs)
                        logger.info(f"Groq generated {action} question: {generated_text[:50]}... (time: {suggested_time}s)")
                        return {
                            "action": action,
                            "question_text": generated_text,
                            "next_index": current_question_index + 1,
                            "suggested_time_seconds": suggested_time
                        }
                
                if action == "preset" and has_remaining_presets:
                    next_question = interview_config.questions[next_preset_idx]
                    return {
                        "action": "preset",
                        "question_text": next_question.text,
                        "next_index": next_preset_idx + 1,
                        "suggested_time_seconds": getattr(next_question, 'suggested_time_seconds', 120) or 120
                    }
                
                if action == "complete" and not has_remaining_presets:
                    return {"action": "complete"}
                
                # Default: go to next preset
                return self._get_next_preset_or_complete(interview_config, current_question_index)

    def _get_next_preset_or_complete(self, interview_config, current_question_index: int) -> Dict[str, Any]:
        """Helper: Returns next preset question action or complete if all done"""
        next_preset_idx = current_question_index + 1
        if next_preset_idx < len(interview_config.questions):
            next_question = interview_config.questions[next_preset_idx]
            return {
                "action": "preset",
                "question_text": next_question.text,
                "next_index": next_preset_idx + 1,
                "suggested_time_seconds": getattr(next_question, 'suggested_time_seconds', 120) or 120
            }
        else:
            return {"action": "complete"}

    def _build_llm_prompt( 
        self,
        interview_config: InterviewConfig,
        session_history: List[Dict[str, str]],
        current_question_index: int, # 0-based index of question JUST answered
        candidate_transcript: str,
        resume_text: str,
        elapsed_seconds: int = 0,  # NEW: How much time has passed
        time_limit_seconds: int = 600  # NEW: Total interview time in seconds
    ) -> str:
        """Helper to construct the detailed prompt for the LLM."""

        job_role = interview_config.job_role
        job_desc = interview_config.job_description[:500] 
        
        focus_areas_str = "N/A"
        try:
            focus_list = interview_config.focus
            if isinstance(focus_list, str):
                 focus_list = json.loads(focus_list)
            if isinstance(focus_list, list):
                 focus_areas_str = ', '.join(focus_list)
        except: pass 

        history_str = "\n".join([f"Q{i+1}: {item['question']}\nA{i+1}: {item['answer'][:200]}..."
                                 for i, item in enumerate(session_history)])

        # Get the question that was just answered (it's the last one in the history)
        last_question_text = session_history[-1]["question"] if session_history else "N/A"

        # Remaining PRESET questions
        next_preset_index = current_question_index + 1 # 0-based index of NEXT preset
        remaining_questions = [q.text for i, q in enumerate(interview_config.questions) if i >= next_preset_index]
        remaining_questions_str = "\n".join(f"- {q}" for q in remaining_questions) if remaining_questions else "None"
        
        # Count follow-up questions since last preset question
        # This helps limit follow-ups per main question
        total_questions_asked = len(session_history)
        preset_count = current_question_index + 1  # How many preset questions answered
        follow_up_count = total_questions_asked - preset_count  # Approximate follow-ups asked
        
        # Calculate interview time context using ACTUAL elapsed time
        total_preset_questions = len(interview_config.questions)
        
        # Use passed-in time info (in seconds)
        remaining_seconds = max(0, time_limit_seconds - elapsed_seconds)
        remaining_minutes = remaining_seconds / 60
        elapsed_minutes = elapsed_seconds / 60
        total_minutes = time_limit_seconds / 60
        
        # Time budget allocation:
        # - 70% for preset questions (must complete all)
        # - 20% for follow-ups 
        # - 10% for resume questions at the end
        preset_time_budget = int(time_limit_seconds * 0.70)
        followup_time_budget = int(time_limit_seconds * 0.20)
        resume_time_budget = int(time_limit_seconds * 0.10)
        
        # Calculate remaining presets and time per preset
        remaining_presets = total_preset_questions - preset_count
        time_for_remaining_presets = remaining_seconds * 0.7 if remaining_presets > 0 else 0
        time_per_preset = int(time_for_remaining_presets / remaining_presets) if remaining_presets > 0 else 0
        
        # Determine if we have time for follow-ups
        has_time_for_followup = remaining_seconds > (remaining_presets * 60 + 30)  # Need at least 30s buffer
        
        # Max follow-ups based on remaining time - STRICT LIMIT: Max 1 per preset
        if remaining_seconds < 60:
            max_follow_ups_per_preset = 0  # No time for follow-ups!
        elif remaining_seconds < 120:
            max_follow_ups_per_preset = 0  # Very limited time, skip follow-ups
        elif remaining_presets > 0:
            max_follow_ups_per_preset = 1  # LIMIT: Only 1 follow-up per preset question
        else:
            max_follow_ups_per_preset = 1  # Even with no presets left, max 1 follow-up
        
        resume_summary = resume_text[:1000] 

        # Time urgency level
        if remaining_seconds < 60:
            time_urgency = "CRITICAL - Less than 1 minute left! Complete immediately or ask one final question."
        elif remaining_seconds < 120:
            time_urgency = "URGENT - Less than 2 minutes left. Wrap up quickly."
        elif remaining_seconds < 180:
            time_urgency = "LIMITED - About 3 minutes left. Be efficient."
        else:
            time_urgency = "NORMAL - Good amount of time remaining."

        prompt = f"""You are an expert AI interviewer conducting a DYNAMIC interview for a '{job_role}' role.
Your goal is to conduct an efficient interview that balances depth with time management.

**Context:**
- Job Description: {job_desc}
- Focus Areas: {focus_areas_str}
- Total Interview Time: {total_minutes:.1f} minutes ({time_limit_seconds} seconds)
- Preset Questions: {total_preset_questions}

**TIME STATUS (CRITICAL - Use this for decisions!):**
- Elapsed: {elapsed_minutes:.1f} min ({elapsed_seconds}s)
- Remaining: {remaining_minutes:.1f} min ({remaining_seconds}s)
- Time Urgency: {time_urgency}
- Has time for follow-ups: {"YES" if has_time_for_followup else "NO - Skip follow-ups, move to next preset!"}

**Interview Progress:**
- Questions asked so far: {total_questions_asked}
- Preset questions answered: {preset_count} of {total_preset_questions}
- Remaining presets: {remaining_presets}
- Follow-up questions asked: {follow_up_count}
- Max follow-ups allowed now: {max_follow_ups_per_preset}

**Candidate Resume Summary:**
{resume_summary}

**Interview History So Far:**
{history_str}

**Current Situation:**
The candidate just answered Question {total_questions_asked}:
Q: {last_question_text}
Answer: "{candidate_transcript}"

**Remaining Pre-set Questions:**
{remaining_questions_str}

**Decision Rules (IMPORTANT - Follow these strictly):**

1. **'preset'** (Move to next main question when appropriate):
   - USE THIS if you've already asked {max_follow_ups_per_preset}+ follow-ups for this preset question
   - USE THIS if the candidate's answer was complete and detailed
   - Move forward to cover all main topics efficiently

2. **'follow_up'** (Max {max_follow_ups_per_preset} per preset):
   - Ask if the answer is vague, incomplete, or mentions something interesting to probe
   - Generate ONE SHORT probing question based on their answer
   - Good for clarification: "Can you elaborate on..." or "What was the outcome of..."

3. **'resume'** (IMPORTANT - Based on candidate's resume):
   - Ask a question connecting their resume experience to the job role
   - MUST USE if all preset questions are done but interview time remains!
   - Example: "I see on your resume you worked at X. Can you tell me about..."
   - Can ask 1-2 resume questions during the interview

4. **'complete'**: 
   - ONLY use if ALL preset questions are done AND you've asked at least 1 resume question
   - Do NOT complete early if you haven't explored the candidate's resume!

**Current follow-ups for this preset: {follow_up_count}**
**Should you ask another follow-up? {"NO - Move to preset" if follow_up_count >= max_follow_ups_per_preset else "Maybe - if answer needs probing"}**

**Respond ONLY with valid JSON:**
{{
  "action": "follow_up" | "resume" | "preset" | "complete",
  "question_text": "Your question here (required for follow_up and resume)",
  "suggested_time_seconds": 90
}}

**Your JSON Response:**
"""
        return prompt

# Create service instance (if used globally)
ai_question_service = AIQuestionService()
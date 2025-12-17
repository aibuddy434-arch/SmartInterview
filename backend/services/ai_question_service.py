import logging
import random
import asyncio
from typing import List, Dict, Any, Optional
from models.interview import Question, FocusArea, DifficultyLevel, InterviewConfig
from app.config import settings # Import settings to get API key
import json
from enum import Enum # Import Enum for instance checks

logger = logging.getLogger(__name__)

# --- Google AI (Gemini) Client Initialization ---
google_ai_available = False
gemini_model = None
try:
    import google.generativeai as genai
    if settings.google_api_key:
        try:
            genai.configure(api_key=settings.google_api_key)
            # Select the Gemini model specified in settings
            gemini_model = genai.GenerativeModel(model_name=settings.google_model_name)
            google_ai_available = True
            logger.info(f"Google AI (Gemini) client configured successfully with model: {settings.google_model_name}.")
        except Exception as e:
            logger.error(f"Failed to configure Google AI client: {e}")
            google_ai_available = False
    else:
        logger.warning("GOOGLE_API_KEY not set. LLM features disabled.")
        google_ai_available = False
except ImportError:
    logger.warning("Google AI library not installed (`pip install google-generativeai`). LLM features disabled.")
    google_ai_available = False
# --- End Google AI Initialization ---

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
        Tries to use Google AI (Gemini) first, then falls back to templates.
        """
        global google_ai_available, gemini_model
        
        focus_area_strings = [area.value if isinstance(area, Enum) else area for area in focus_areas]
        difficulty_string = difficulty.value if isinstance(difficulty, Enum) else difficulty

        if google_ai_available and gemini_model:
            try:
                logger.info(f"Attempting to generate questions using Google AI for job: {job_role}")
                
                prompt = self._build_initial_questions_prompt(
                    job_role, job_description, focus_area_strings, difficulty_string, number_of_questions
                )

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
                        questions.append(Question(
                            text=q_data["text"],
                            tags=q_data["tags"],
                            generated_by="ai"
                        ))
                
                if questions:
                     logger.info(f"Successfully generated {len(questions)} questions using Google AI.")
                     return questions[:number_of_questions] # Return exact number
                else:
                    logger.warning("AI generation succeeded but returned no questions.")

            except Exception as e:
                logger.error(f"Google AI question generation failed: {e}. Falling back to templates.")
                # Fallthrough to template logic
        else:
            logger.warning("Google AI not available. Falling back to templates.")

        # --- Fallback Logic ---
        return self._generate_template_questions(
            focus_areas, difficulty, number_of_questions
        )

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
        You are an AI assistant tasked with creating interview questions.
        
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
        
        **Respond ONLY with a valid JSON object with a single key "questions".**
        The value of "questions" must be a JSON list, where each item is an object with "text" and "tags" keys.

        **Example JSON Response:**
        {{
          "questions": [
            {{
              "text": "Can you describe a challenging {difficulty} project you completed using Python, as mentioned in the job description?",
              "tags": ["technical"]
            }},
            {{
              "text": "How would you explain a complex technical concept to a non-technical stakeholder?",
              "tags": ["communication"]
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
        resume_text: str
    ) -> Dict[str, Any]:
        """
        Analyzes the latest response and determines the next action using Google AI (Gemini).
        Returns: Dict like {"action": "preset/follow_up/resume/complete", "question_text": "...", "next_index": #}
        """
        global google_ai_available, gemini_model 
        
        # --- Fallback Logic ---
        if not google_ai_available or gemini_model is None:
            logger.warning("Google AI not available, falling back to simple next question logic.")
            next_preset_idx = current_question_index + 1 # 0-based index of NEXT preset Q
            if next_preset_idx < len(interview_config.questions):
                 return {
                     "action": "preset",
                     "question_text": interview_config.questions[next_preset_idx].text,
                     "next_index": next_preset_idx + 1 # Return 1-based index for DB update
                 }
            else:
                 return {"action": "complete"}
        # --- End Fallback ---

        try:
            prompt = self._build_llm_prompt(
                interview_config, session_history, current_question_index, candidate_transcript, resume_text
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
                    next_step_data["question_text"] = interview_config.questions[next_preset_idx].text
                    next_step_data["next_index"] = next_preset_idx + 1  # 1-based index for DB
                else:
                    logger.warning("AI chose 'preset' but no pre-set questions remain. Completing.")
                    next_step_data["action"] = "complete"

            elif action == "follow_up" or action == "resume":
                generated_text = decision.get("question_text")
                if generated_text:
                    next_step_data["question_text"] = generated_text
                    # Keep the same preset index (don't advance yet)
                    next_step_data["next_index"] = current_question_index + 1  # 1-based index of CURRENT preset Q
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
            # SMART FALLBACK: Go to next preset question instead of completing
            return self._get_next_preset_or_complete(interview_config, current_question_index)

    def _get_next_preset_or_complete(self, interview_config, current_question_index: int) -> Dict[str, Any]:
        """Helper: Returns next preset question action or complete if all done"""
        next_preset_idx = current_question_index + 1
        if next_preset_idx < len(interview_config.questions):
            return {
                "action": "preset",
                "question_text": interview_config.questions[next_preset_idx].text,
                "next_index": next_preset_idx + 1
            }
        else:
            return {"action": "complete"}

    def _build_llm_prompt( 
        self,
        interview_config: InterviewConfig,
        session_history: List[Dict[str, str]],
        current_question_index: int, # 0-based index of question JUST answered
        candidate_transcript: str,
        resume_text: str
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
        
        resume_summary = resume_text[:1000] 

        prompt = f"""You are an expert AI interviewer conducting a DYNAMIC interview for a '{job_role}' role.
Your goal is to conduct a thorough, adaptive interview that feels natural and explores the candidate deeply.

**Context:**
- Job Description: {job_desc}
- Focus Areas: {focus_areas_str}

**Candidate Resume Summary:**
{resume_summary}

**Interview History So Far:**
{history_str}

**Current Situation:**
The candidate just answered Question {current_question_index + 1}:
Q{current_question_index + 1}: {last_question_text}
Candidate's Answer: "{candidate_transcript}"

**Remaining Pre-set Questions (as backup):**
{remaining_questions_str}

**Your Task:** 
Analyze the candidate's LAST answer carefully. As a skilled interviewer, you should:
1. PROBE DEEPER when answers are vague, incomplete, or mention interesting topics
2. CONNECT to their resume when you spot relevant experience
3. Only move to preset questions when the current topic is fully explored

**Decision Rules (in order of priority):**

1. **'follow_up'** (PREFERRED - use 60% of the time): 
   - If the answer mentions ANY technology, project, challenge, or experience that could be explored further
   - If the answer is less than 3 sentences or lacks specific details
   - If there's an interesting claim that needs evidence ("I improved performance" → "Can you quantify that improvement?")
   - Generate ONE probing question based DIRECTLY on their LAST answer.

2. **'resume'** (USE OFTEN - use 25% of the time):
   - If this is a good opportunity to connect to their resume (skills, past roles, projects mentioned)
   - If you haven't asked about their resume in the last 2 questions
   - Generate ONE question connecting their experience to the job requirements.

3. **'preset'** (FALLBACK - use 15% of the time):
   - ONLY if the current answer is complete, detailed, and well-explained
   - AND there's nothing more to explore on this topic
   - AND you've already asked follow-up or resume questions recently

4. **'complete'**: 
   - ONLY if ALL preset questions have been asked AND you've done at least 2 follow-ups
   - OR if the total interview time should end

**Respond ONLY with a valid JSON object:**
{{
  "action": "follow_up" | "resume" | "preset" | "complete",
  "question_text": "Your question here (required for follow_up and resume)"
}}

**Examples of GOOD follow-up questions:**
- "You mentioned optimizing database queries. What specific techniques did you use and what improvements did you measure?"
- "That's an interesting approach. Can you walk me through a specific example where you applied this?"
- "You said you led a team. How did you handle disagreements within the team?"

**Your JSON Response:**
"""
        return prompt

# Create service instance (if used globally)
ai_question_service = AIQuestionService()
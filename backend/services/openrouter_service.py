"""
OpenRouter API Service
Provides unified access to 500+ AI models with automatic failover.
"""
import os
import logging
import json
import aiohttp
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# OpenRouter Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Model Configuration
MODEL_PRIMARY = os.getenv("OPENROUTER_MODEL_PRIMARY", "meta-llama/llama-3.3-70b-instruct")
MODEL_FALLBACK = os.getenv("OPENROUTER_MODEL_FALLBACK", "meta-llama/llama-4-maverick:free")
MODEL_REPORT = os.getenv("OPENROUTER_MODEL_REPORT", "anthropic/claude-3.5-sonnet")

# Model pricing per 1M tokens (for cost estimation)
MODEL_PRICING = {
    "meta-llama/llama-3.3-70b-instruct": {"input": 0.10, "output": 0.39},
    "meta-llama/llama-4-maverick:free": {"input": 0.0, "output": 0.0},
    "anthropic/claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "google/gemini-2.0-flash-001": {"input": 0.10, "output": 0.40},
}

if OPENROUTER_API_KEY:
    logger.info(f"✅ OpenRouter API configured with key: {OPENROUTER_API_KEY[:20]}...")
    logger.info(f"   Primary model: {MODEL_PRIMARY}")
    logger.info(f"   Fallback model: {MODEL_FALLBACK}")
    logger.info(f"   Report model: {MODEL_REPORT}")
else:
    logger.warning("⚠️ OPENROUTER_API_KEY not found in .env file")


class OpenRouterService:
    """OpenRouter API service with automatic failover support."""
    
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",  # For OpenRouter analytics
            "X-Title": "AI Interview System"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        json_mode: bool = False,
        fallback_models: List[str] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenRouter with automatic fallover.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to MODEL_PRIMARY)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            json_mode: If True, request JSON output
            fallback_models: List of models to try if primary fails
        
        Returns:
            Dict with 'content' (response text), 'model' (used), 'usage' (token counts)
        """
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
        
        # Build model list (primary + fallbacks)
        models_to_try = [model or MODEL_PRIMARY]
        if fallback_models:
            models_to_try.extend(fallback_models)
        else:
            models_to_try.append(MODEL_FALLBACK)
        
        last_error = None
        
        for current_model in models_to_try:
            try:
                logger.info(f"[OpenRouter] Trying model: {current_model}")
                
                payload = {
                    "model": current_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                
                if json_mode:
                    payload["response_format"] = {"type": "json_object"}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as response:
                        response_text = await response.text()
                        
                        if response.status == 200:
                            result = json.loads(response_text)
                            content = result["choices"][0]["message"]["content"]
                            usage = result.get("usage", {})
                            
                            logger.info(f"[OpenRouter] Success with {current_model}")
                            logger.info(f"   Tokens: {usage.get('prompt_tokens', 0)} in, {usage.get('completion_tokens', 0)} out")
                            
                            return {
                                "content": content,
                                "model": current_model,
                                "usage": usage
                            }
                        
                        elif response.status == 429:
                            logger.warning(f"[OpenRouter] Rate limited on {current_model}, trying fallback...")
                            last_error = f"Rate limited: {response_text}"
                            continue
                        
                        elif response.status >= 500:
                            logger.warning(f"[OpenRouter] Server error on {current_model}, trying fallback...")
                            last_error = f"Server error {response.status}: {response_text}"
                            continue
                        
                        else:
                            logger.error(f"[OpenRouter] Error {response.status}: {response_text}")
                            last_error = f"Error {response.status}: {response_text}"
                            continue
                            
            except aiohttp.ClientError as e:
                logger.warning(f"[OpenRouter] Network error with {current_model}: {e}")
                last_error = str(e)
                continue
            except Exception as e:
                logger.error(f"[OpenRouter] Unexpected error with {current_model}: {e}")
                last_error = str(e)
                continue
        
        # All models failed
        raise RuntimeError(f"All OpenRouter models failed. Last error: {last_error}")
    
    async def generate_question_decision(
        self,
        prompt: str,
        system_message: str = "You are an expert AI interviewer. Output ONLY valid JSON."
    ) -> Dict[str, Any]:
        """Generate next question decision using the primary model."""
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(
            messages=messages,
            model=MODEL_PRIMARY,
            temperature=0.3,
            max_tokens=500,
            json_mode=True
        )
        
        return json.loads(result["content"])
    
    async def generate_report_analysis(
        self,
        prompt: str,
        system_message: str = "You are an expert interview analyst. Output ONLY valid JSON."
    ) -> Dict[str, Any]:
        """Generate comprehensive report analysis using the report model (Claude)."""
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        # Use Claude for reports, fall back to Llama if Claude fails
        result = await self.chat_completion(
            messages=messages,
            model=MODEL_REPORT,
            temperature=0.2,
            max_tokens=2500,
            json_mode=True,
            fallback_models=[MODEL_PRIMARY, MODEL_FALLBACK]
        )
        
        return json.loads(result["content"])
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str = None) -> float:
        """Estimate cost for a request in USD."""
        model = model or MODEL_PRIMARY
        pricing = MODEL_PRICING.get(model, {"input": 0.10, "output": 0.40})
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost


# Singleton instance
openrouter_service = OpenRouterService()

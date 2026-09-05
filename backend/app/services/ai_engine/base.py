import json
import logging
import asyncio
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger("pulse.ai_engine")
T = TypeVar("T", bound=BaseModel)

class LLMProvider:
    """
    Extensible LLM Provider layer supporting structured JSON validation via Pydantic schemas.
    Falls back gracefully to intelligent rule heuristics if API key is missing or calls fail.
    """
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower() if settings.AI_PROVIDER else "openai"
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL or "gpt-4o-mini"

    def get_status(self) -> Dict[str, Any]:
        has_key = bool(settings.AI_API_KEY and settings.AI_API_KEY.strip())
        provider_name = settings.AI_PROVIDER.upper() if settings.AI_PROVIDER else "OPENAI"
        
        if has_key and settings.AI_PROVIDER != "mock":
            status_text = f"CONNECTED (LIVE {provider_name} API)"
        else:
            status_text = "FALLBACK (HEURISTIC ENGINE)"

        return {
            "provider": settings.AI_PROVIDER or "openai",
            "model": settings.AI_MODEL or "gpt-4o-mini",
            "has_api_key": has_key,
            "status": status_text
        }

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: Type[T],
        fallback_factory: Optional[Any] = None
    ) -> T:
        """
        Executes an LLM call expecting JSON adhering strictly to response_schema.
        Includes retries and timeout protection.
        """
        if not self.api_key or not self.api_key.strip():
            logger.info("No AI_API_KEY set. Utilizing intelligent rule-heuristic engine.")
            if fallback_factory:
                return fallback_factory()
            raise ValueError("No AI API key set and no fallback factory provided.")

        max_retries = 3
        backoff_sec = 1.0

        for attempt in range(1, max_retries + 1):
            try:
                if self.provider == "openai":
                    return await self._call_openai(system_prompt, user_prompt, response_schema)
                elif self.provider == "gemini":
                    return await self._call_gemini(system_prompt, user_prompt, response_schema)
                else:
                    logger.warning(f"Unsupported AI provider '{self.provider}'. Falling back.")
                    if fallback_factory:
                        return fallback_factory()
                    raise ValueError(f"Unsupported AI provider: {self.provider}")
            except Exception as e:
                logger.warning(f"Attempt {attempt}/{max_retries} failed for AI provider {self.provider}: {type(e).__name__}")
                if attempt < max_retries:
                    await asyncio.sleep(backoff_sec * attempt)
                else:
                    logger.error(f"All {max_retries} LLM attempts failed. Engaging fallback heuristic.")
                    if fallback_factory:
                        return fallback_factory()
                    raise e

    async def _call_openai(self, system_prompt: str, user_prompt: str, response_schema: Type[T]) -> T:
        import httpx
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt + "\nReturn ONLY valid JSON matching the requested schema."},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            parsed_json = json.loads(raw_content)
            return response_schema.model_validate(parsed_json)

    async def _call_gemini(self, system_prompt: str, user_prompt: str, response_schema: Type[T]) -> T:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_prompt}\n\nContext:\n{user_prompt}\n\nReturn strict JSON."}]}
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed_json = json.loads(raw_content)
            return response_schema.model_validate(parsed_json)

llm_provider = LLMProvider()


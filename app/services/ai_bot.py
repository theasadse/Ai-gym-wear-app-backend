import asyncio
from functools import lru_cache
from typing import Optional, List, Dict

import google.generativeai as genai

from app.core.config import settings
from app.core.logger import logger


class AIBotService:
    """
    Thin wrapper around a text-generation provider so it can be swapped easily.
    """

    async def generate_reply(
        self, message: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class HFAIBotService(AIBotService):
    def __init__(self, model_pipeline):
        self._pipeline = model_pipeline

    async def generate_reply(
        self, message: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        prompt = self._build_prompt(message, history)
        loop = asyncio.get_event_loop()
        logger.info("Generating reply", extra={"model": settings.model_name})
        outputs = await loop.run_in_executor(
            None, lambda: self._pipeline(prompt, max_new_tokens=settings.max_tokens)
        )
        generated = outputs[0]["generated_text"]
        if generated.startswith(prompt):
            generated = generated[len(prompt) :].strip()
        return generated.strip()

    @staticmethod
    def _build_prompt(message: str, history: Optional[List[Dict[str, str]]]) -> str:
        conversation = ""
        if history:
            for turn in history[-6:]:
                role = "User" if turn.get("role") == "user" else "Assistant"
                conversation += f"{role}: {turn.get('content','').strip()}\n"
        conversation += f"User: {message}\nAssistant:"
        return (
            "You are a helpful gym wear shopping assistant that knows about products, sizes, and fit advice.\n"
            + conversation
        )


class GeminiAIBotService(AIBotService):
    def __init__(self, api_key: str, model_name: str, fallback: Optional["HFAIBotService"] = None):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        self.fallback = fallback

    async def generate_reply(
        self, message: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        def _sync_call():
            chat = self.model.start_chat(
                history=[
                    {"role": "user" if h.get("role") == "user" else "model", "parts": h.get("content", "")}
                    for h in (history or [])[-6:]
                ]
            )
            resp = chat.send_message(message)
            return resp.text or ""

        loop = asyncio.get_event_loop()
        logger.info("Generating reply via Gemini", extra={"model": settings.gemini_model})
        try:
            return (await loop.run_in_executor(None, _sync_call)).strip()
        except Exception as exc:
            logger.error("Gemini generation failed", exc_info=exc)
            if self.fallback:
                return await self.fallback.generate_reply(message, history)
            raise


@lru_cache
def _load_pipeline():
    # Lazy import to avoid torch import unless needed.
    from transformers import pipeline  # type: ignore

    logger.info("Loading model pipeline", extra={"model": settings.model_name})
    return pipeline(
        "text-generation",
        model=settings.model_name,
        device_map="auto" if settings.device_map_auto else None,
    )


def get_ai_bot() -> AIBotService:
    if settings.gemini_api_key:
        # No HF fallback by default to avoid torch import issues in restricted envs.
        return GeminiAIBotService(settings.gemini_api_key, settings.gemini_model, fallback=None)
    return HFAIBotService(_load_pipeline())

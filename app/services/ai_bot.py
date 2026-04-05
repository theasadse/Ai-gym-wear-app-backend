import asyncio
from functools import lru_cache
from typing import Optional, List, Dict

from transformers import pipeline, Pipeline

from app.core.config import settings
from app.core.logger import logger


class AIBotService:
    """
    Thin wrapper around a text-generation pipeline so it can be swapped easily.
    """

    def __init__(self, model_pipeline: Pipeline):
        self._pipeline = model_pipeline

    async def generate_reply(
        self, message: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        prompt = self._build_prompt(message, history)
        loop = asyncio.get_event_loop()
        logger.info("Generating reply", extra={"model": settings.model_name})
        # Run the blocking HF pipeline in a thread to avoid blocking the event loop.
        outputs = await loop.run_in_executor(
            None, lambda: self._pipeline(prompt, max_new_tokens=settings.max_tokens)
        )
        # HF pipeline returns list of dicts with 'generated_text'
        generated = outputs[0]["generated_text"]
        # Strip the prompt prefix if returned.
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


@lru_cache
def _load_pipeline() -> Pipeline:
    logger.info("Loading model pipeline", extra={"model": settings.model_name})
    return pipeline(
        "text-generation",
        model=settings.model_name,
        device_map="auto" if settings.device_map_auto else None,
    )


def get_ai_bot() -> AIBotService:
    pipe = _load_pipeline()
    return AIBotService(pipe)

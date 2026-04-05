from fastapi import APIRouter, Depends

from app.api.schemas import ChatRequest, ChatResponse
from app.services.ai_bot import get_ai_bot, AIBotService
from app.api import products

router = APIRouter()
router.include_router(products.router)


@router.post("/chat", response_model=ChatResponse, tags=["ai"])
async def chat(
    payload: ChatRequest, bot: AIBotService = Depends(get_ai_bot)
) -> ChatResponse:
    """
    Accept a user message and return the AI bot reply.
    """
    reply = await bot.generate_reply(payload.message, context=payload.context)
    return ChatResponse(reply=reply)

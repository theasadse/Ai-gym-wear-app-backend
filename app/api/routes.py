from typing import List

from fastapi import APIRouter, Depends

from app.api.schemas import ChatRequest, ChatResponse, ProductOut
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
    hist = [h.model_dump() for h in payload.history] if payload.history else None
    reply = await bot.generate_reply(payload.message, history=hist)
    return ChatResponse(reply=reply)


# Public mirror without /api prefix for frontend defaults
public_router = APIRouter()
public_router.add_api_route(
    "/products",
    products.get_products,
    response_model=List[ProductOut],
    methods=["GET"],
    tags=["products"],
)
public_router.add_api_route(
    "/recommendations",
    products.get_recommendations,
    response_model=List[ProductOut],
    methods=["GET"],
    tags=["products"],
)
public_router.add_api_route(
    "/chat",
    chat,
    response_model=ChatResponse,
    methods=["POST"],
    tags=["ai"],
)

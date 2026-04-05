from typing import List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import ChatRequest, ChatResponse, ProductOut
from app.services.ai_bot import get_ai_bot, AIBotService
from app.services.product_service import list_products
from app.api import products
from app.core.config import settings

router = APIRouter()
router.include_router(products.router)


def _extract_max_price(message: str) -> Optional[float]:
    """
    Parse phrases like 'under 20', 'below $30', '<15' for a max price filter.
    """
    pattern = r"(?:under|below|less than|<)\s*\$?\s*(\d+(?:\.\d+)?)"
    match = re.search(pattern, message, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


@router.post("/chat", response_model=ChatResponse, tags=["ai"])
async def chat(
    payload: ChatRequest, bot: AIBotService = Depends(get_ai_bot)
) -> ChatResponse:
    """
    Accept a user message and return product-grounded suggestions.
    Gemini/HF is optional; if it fails we still return product picks.
    """
    hist = [h.model_dump() for h in payload.history] if payload.history else None

    # 1) Retrieve products
    max_price = _extract_max_price(payload.message)
    product_matches: List[ProductOut] = []
    try:
        product_matches = await list_products(
            search=payload.message, max_price=max_price
        )
    except Exception:
        product_matches = []

    # 2) Build deterministic product suggestions
    if product_matches:
        top = product_matches[:3]
        suggestions = "\n".join(
            [f"- {p.name} (${p.price:.2f}) → /products/{p.id}" for p in top]
        )
    else:
        suggestions = "No matching products found right now."

    # 3) Optional AI phrasing using product context
    ai_reply = ""
    if settings.gemini_api_key and bot:
        context = "\n".join(
            [
                f"{p.name} (${p.price:.2f}) | {p.category} | sizes {p.sizes} | tags {', '.join(p.tags)} | id {p.id}"
                for p in product_matches[:5]
            ]
        )
        prompt = (
            "You are a gym-wear assistant. Suggest products only from this list:\n"
            f"{context}\n\nUser request: {payload.message}\n"
            "Respond briefly with up to 2 items, referencing the name and price."
        )
        try:
            ai_reply = await bot.generate_reply(prompt, history=hist)
        except Exception:
            ai_reply = ""

    # 4) Combine
    combined = ai_reply.strip() if ai_reply else ""
    if suggestions:
        combined = f"{combined}\n\nSuggested products:\n{suggestions}".strip()

    # If everything failed, return a clear message
    if not combined:
        raise HTTPException(status_code=502, detail="AI suggestions service unavailable")

    return ChatResponse(reply=combined)


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

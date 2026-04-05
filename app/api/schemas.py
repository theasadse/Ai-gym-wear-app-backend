from decimal import Decimal
from typing import Optional, List, Literal

from pydantic import BaseModel, Field, ConfigDict


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to the AI bot")
    history: Optional[List[ChatHistoryItem]] = Field(
        None, description="Optional prior messages to keep context"
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Bot-generated reply")


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    price: float
    category: str
    image: str
    colors: List[str]
    tags: List[str]
    rating: float
    stock: int
    featured: bool
    newArrival: bool
    sizes: str

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message to the AI bot")
    context: Optional[str] = Field(
        None, description="Optional conversation or product context"
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Bot-generated reply")


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    price: float
    imageUrl: str
    category: str
    sizes: str
    inventory: int

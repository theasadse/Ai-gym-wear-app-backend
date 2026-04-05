from typing import List, Optional

from fastapi import APIRouter, Query

from app.api.schemas import ProductOut
from app.services.product_service import list_products

router = APIRouter()


@router.get("/products", response_model=List[ProductOut], tags=["products"])
async def get_products(category: Optional[str] = Query(None, description="Filter by category")):
    return await list_products(category)

from typing import List, Optional

from fastapi import APIRouter, Query

from app.api.schemas import ProductOut
from app.services.product_service import list_products, list_recommendations

router = APIRouter()


@router.get("/products", response_model=List[ProductOut], tags=["products"])
async def get_products(
    search: Optional[str] = Query(None, description="Search by name or tag"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    size: Optional[str] = Query(None, description="Filter by size"),
):
    return await list_products(search=search, category=category, tag=tag, size=size)


@router.get("/recommendations", response_model=List[ProductOut], tags=["products"])
async def get_recommendations(userId: Optional[str] = Query(None, description="User id for personalization")):
    return await list_recommendations(user_id=userId)

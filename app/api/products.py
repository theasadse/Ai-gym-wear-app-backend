from typing import List, Optional

from fastapi import APIRouter, Query

from app.api.schemas import ProductOut
from app.services.product_service import list_products, list_recommendations
from app.db import prisma

router = APIRouter()


@router.get("/products", response_model=List[ProductOut], tags=["products"])
async def get_products(
    search: Optional[str] = Query(None, description="Search by name or tag"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    size: Optional[str] = Query(None, description="Filter by size"),
    maxPrice: Optional[float] = Query(None, description="Filter by max price (USD)"),
):
    return await list_products(
        search=search, category=category, tag=tag, size=size, max_price=maxPrice
    )


@router.get("/recommendations", response_model=List[ProductOut], tags=["products"])
async def get_recommendations(userId: Optional[str] = Query(None, description="User id for personalization")):
    return await list_recommendations(user_id=userId)


@router.get("/products/{product_id}", response_model=ProductOut, tags=["products"])
async def get_product(product_id: str):
    product = await prisma.product.find_unique(where={"id": product_id})
    if not product:
        return {"detail": "Product not found"}
    return ProductOut.model_validate(product, from_attributes=True)

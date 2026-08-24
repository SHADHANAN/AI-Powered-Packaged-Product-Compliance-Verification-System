from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.controllers.product_controller import ProductController
from backend.schemas.product import ProductCreate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Registers a packaged product with its mandatory commodity declarations.",
)
async def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductResponse:
    return ProductController.create_product(db=db, product_in=product_in)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieves product details for a given product ID.",
)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductResponse:
    product = ProductController.get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return product


@router.get(
    "",
    response_model=List[ProductResponse],
    summary="List products",
    description="Returns a paginated list of registered packaged products.",
)
async def list_products(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination limit"),
    db: Session = Depends(get_db),
) -> List[ProductResponse]:
    return ProductController.list_products(db=db, skip=skip, limit=limit)

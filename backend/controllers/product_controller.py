from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.database.models import Product
from backend.schemas.product import ProductCreate, ProductUpdate


class ProductController:
    """
    Controller handling database CRUD operations for Product entity.
    """

    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        """
        Creates a new product record in the database.
        """
        db_product = Product(**product_in.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        Retrieves a product by primary key ID.
        """
        stmt = select(Product).where(Product.id == product_id)
        return db.scalars(stmt).first()

    @staticmethod
    def list_products(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """
        Returns a paginated list of products ordered by ID.
        """
        stmt = select(Product).offset(skip).limit(limit).order_by(Product.id.desc())
        return list(db.scalars(stmt).all())

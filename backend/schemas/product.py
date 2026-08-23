from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """
    Base attributes for a product.
    """
    product_name: str = Field(..., min_length=1, max_length=255, description="Name of the product")
    brand_name: Optional[str] = Field(None, max_length=255, description="Brand name")
    manufacturer_name: Optional[str] = Field(None, max_length=255, description="Manufacturer name and address")
    importer_name: Optional[str] = Field(None, max_length=255, description="Importer name and address (if applicable)")
    country_of_origin: Optional[str] = Field(None, max_length=100, description="Country of origin")
    net_quantity: Optional[str] = Field(None, max_length=100, description="Declared net quantity value")
    unit: Optional[str] = Field(None, max_length=50, description="Unit of measurement (e.g., g, kg, ml, l)")
    batch_number: Optional[str] = Field(None, max_length=100, description="Lot/Batch number")
    date_of_manufacture: Optional[str] = Field(None, max_length=100, description="Date of manufacture / packaging")
    date_of_import: Optional[str] = Field(None, max_length=100, description="Date of import (if applicable)")
    mrp: Optional[float] = Field(None, ge=0, description="Maximum Retail Price in INR")
    customer_care_details: Optional[str] = Field(None, description="Consumer grievance/customer care contact information")


class ProductCreate(ProductBase):
    """
    Schema for creating a new product.
    """
    pass


class ProductUpdate(BaseModel):
    """
    Schema for updating an existing product.
    """
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand_name: Optional[str] = Field(None, max_length=255)
    manufacturer_name: Optional[str] = Field(None, max_length=255)
    importer_name: Optional[str] = Field(None, max_length=255)
    country_of_origin: Optional[str] = Field(None, max_length=100)
    net_quantity: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=50)
    batch_number: Optional[str] = Field(None, max_length=100)
    date_of_manufacture: Optional[str] = Field(None, max_length=100)
    date_of_import: Optional[str] = Field(None, max_length=100)
    mrp: Optional[float] = Field(None, ge=0)
    customer_care_details: Optional[str] = None


class ProductResponse(ProductBase):
    """
    Schema for product responses returned from the API.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

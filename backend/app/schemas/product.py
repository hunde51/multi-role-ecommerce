from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ProductStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

class ProductBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, max_length=100)
    status: ProductStatus = ProductStatus.ACTIVE
    is_active: bool = True
    is_featured: bool = False
    stock_quantity: int = Field(default=-1, ge=-1)  # -1 = unlimited
    download_limit: int = Field(default=0, ge=0)  # 0 = unlimited

class ProductCreate(ProductBase):
    # File info will be handled separately in the upload endpoint
    pass

class ProductUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    short_description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    compare_at_price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)
    sku: Optional[str] = Field(None, max_length=100)
    status: Optional[ProductStatus] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    stock_quantity: Optional[int] = Field(None, ge=-1)
    download_limit: Optional[int] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: int
    seller_id: int
    file_url: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    file_type: Optional[str]
    thumbnail_url: Optional[str]
    preview_url: Optional[str]
    sample_file_url: Optional[str]
    sold_count: int
    average_rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]

class ProductList(BaseModel):
    """Schema for product listings (public view)"""
    id: int
    title: str
    short_description: Optional[str]
    price: float
    compare_at_price: Optional[float]
    thumbnail_url: Optional[str]
    seller_name: Optional[str]
    seller_rating: float
    sold_count: int
    average_rating: float
    review_count: int
    is_featured: bool
    created_at: datetime

class ProductFileUpload(BaseModel):
    """Schema for file upload response"""
    file_url: str
    file_name: str
    file_size: int
    file_type: str
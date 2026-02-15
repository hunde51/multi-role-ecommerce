from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class SellerApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class SellerApplication(BaseModel):
    store_name: str = Field(..., min_length=2, max_length=255)
    seller_bio: str = Field(..., min_length=10, max_length=1024)
    seller_address: str = Field(..., min_length=5, max_length=500)
    seller_tax_id: Optional[str] = Field(None, max_length=50)
    terms_accepted: bool = Field(..., description="Must accept terms and conditions")

class SellerApplicationResponse(BaseModel):
    id: int
    email: str
    store_name: str
    seller_bio: str
    seller_address: str
    seller_tax_id: Optional[str]
    status: SellerApplicationStatus
    created_at: datetime
    updated_at: Optional[datetime]

class SellerApprovalRequest(BaseModel):
    status: SellerApplicationStatus
    rejection_reason: Optional[str] = Field(None, max_length=500)

class SellerProfile(BaseModel):
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    store_name: Optional[str]
    seller_bio: Optional[str]
    seller_address: Optional[str]
    seller_tax_id: Optional[str]
    is_seller_approved: bool
    seller_verified: bool
    total_sales: float
    total_products: int
    seller_rating: float
    created_at: datetime

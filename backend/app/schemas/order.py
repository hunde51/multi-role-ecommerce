from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    product_name: str
    price: float

class OrderBase(BaseModel):
    total_amount: float = Field(..., gt=0)
    status: OrderStatus = OrderStatus.PENDING
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]
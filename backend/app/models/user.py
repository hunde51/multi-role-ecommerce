from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.core.database import Base

class UserRole(PyEnum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    # === Primary Key ===
    id = Column(Integer, primary_key=True, index=True)
    
    # === Authentication & Identity ===
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    
    # === Personal Information ===
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)  # Profile picture
    bio = Column(Text, nullable=True)  # For seller profiles
    
    # === Role & Permissions ===
    role = Column(Enum(UserRole), nullable=False, default=UserRole.BUYER)
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    is_seller_approved = Column(Boolean, default=False, nullable=False)  # Admin approved seller
    is_verified = Column(Boolean, default=False)  # Email verified (legacy, keep for compatibility)
    
    # === Security & Tracking ===
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)  # Keep for compatibility
    login_attempts = Column(Integer, default=0)  # Track failed logins
    locked_until = Column(DateTime(timezone=True), nullable=True)  # Account lock
    
    # === Seller Specific (if role is seller) ===
    store_name = Column(String(255), nullable=True)
    seller_bio = Column(String(1024), nullable=True)
    seller_name = Column(String, nullable=True)  # Business/store name
    seller_description = Column(Text, nullable=True)
    seller_address = Column(String, nullable=True)
    seller_tax_id = Column(String, nullable=True)  # VAT/EIN number
    stripe_account_id = Column(String, nullable=True)  # For payments
    total_sales = Column(Float, default=0.0)  # Total revenue
    total_products = Column(Integer, default=0)  # Products count
    seller_rating = Column(Float, default=0.0)  # Average rating
    seller_verified = Column(Boolean, default=False)  # Identity verified
    
    # === Customer Specific ===
    default_shipping_address = Column(String, nullable=True)
    default_payment_method = Column(String, nullable=True)  # Last 4 digits
    total_spent = Column(Float, default=0.0)
    loyalty_points = Column(Integer, default=0)
    
    # === Address Information ===
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # === Preferences ===
    newsletter_subscribed = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    language = Column(String, default="en")
    currency = Column(String, default="USD")
    
    # === Timestamps ===
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # === Relationships ===
    # Products they sell (if seller)
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan")
    
    # Orders they made (if customer)
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    
    # Reviews they wrote
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    
    # Wishlist
    wishlist_items = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"
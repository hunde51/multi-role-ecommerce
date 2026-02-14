# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Text, DateTime, Integer as CountColumn
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ProductStatus(str, enum.Enum):
    DRAFT = "draft"           # Seller still editing
    PENDING = "pending"       # Awaiting admin approval
    ACTIVE = "active"         # Published and for sale
    SUSPENDED = "suspended"   # Taken down by admin
    ARCHIVED = "archived"     # No longer for sale

class Product(Base):
    __tablename__ = "products"
    
    # === Primary Key ===
    id = Column(Integer, primary_key=True, index=True)
    
    # === Basic Information ===
    title = Column(String(200), index=True, nullable=False)
    description = Column(Text, nullable=False)
    short_description = Column(String(500), nullable=True)  # For listings
    price = Column(Float, nullable=False)
    compare_at_price = Column(Float, nullable=True)  # Original price for "sale" tag
    
    # === Digital Product Specific ===
    file_url = Column(String, nullable=True)  # Path to main product file
    file_size = Column(Integer, nullable=True)  # In bytes
    file_type = Column(String, nullable=True)  # PDF, MP4, ZIP, etc.
    preview_url = Column(String, nullable=True)  # Preview image/video
    download_limit = Column(Integer, default=0)  # 0 = unlimited
    sample_file_url = Column(String, nullable=True)  # Free sample
    
    # === Media ===
    thumbnail_url = Column(String, nullable=True)
    gallery_images = Column(Text, nullable=True)  # JSON array of image URLs
    video_url = Column(String, nullable=True)  # Product video
    
    # === Status & Visibility ===
    status = Column(Enum(ProductStatus), default=ProductStatus.DRAFT)
    is_active = Column(Boolean, default=True)  # Quick toggle
    is_featured = Column(Boolean, default=False)  # Show on homepage
    is_bestseller = Column(Boolean, default=False)
    
    # === Inventory (Even for digital, you might want limits) ===
    stock_quantity = Column(Integer, default=-1)  # -1 = unlimited
    sold_count = Column(Integer, default=0)  # Total sales
    
    # === Categorization ===
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    tags = Column(String, nullable=True)  # Comma-separated or JSON
    sku = Column(String, unique=True, nullable=True)  # Stock keeping unit
    
    # === Seller Information ===
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # === SEO & Metadata ===
    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)
    slug = Column(String, unique=True, index=True)  # URL-friendly name
    
    # === Timestamps ===
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # === Relationships ===
    seller = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    
    # === Derived Properties (calculated, not stored) ===
    @property
    def average_rating(self):
        if self.reviews:
            return sum(r.rating for r in self.reviews) / len(self.reviews)
        return 0.0
    
    @property
    def review_count(self):
        return len(self.reviews)
    
    def __repr__(self):
        return f"<Product {self.title} (${self.price})>"

# === Category Model (for organizing products) ===
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    
    # Relationships
    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref=backref("parent", remote_side=[id]))
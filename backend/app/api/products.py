from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path

from app.core.database import get_db
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.product import (
    ProductCreate, 
    ProductResponse, 
    ProductUpdate, 
    ProductList,
    ProductFileUpload
)
from app.api.auth import get_current_user
from app.core.permissions import get_approved_seller, check_product_ownership

router = APIRouter(prefix="/products", tags=["products"])

# File upload configuration
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_FILE_TYPES = {
    "application/pdf": "pdf",
    "application/zip": "zip", 
    "video/mp4": "mp4",
    "image/jpeg": "jpg",
    "image/png": "png"
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def validate_file(file: UploadFile) -> bool:
    """Validate file type and size"""
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 100MB limit"
        )
    
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Allowed types: {list(ALLOWED_FILE_TYPES.keys())}"
        )
    
    return True

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename using UUID"""
    file_extension = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4()}{file_extension}"

@router.post("/", response_model=ProductResponse)
async def create_product(
    title: str = Form(...),
    description: str = Form(...),
    short_description: Optional[str] = Form(None),
    price: float = Form(...),
    compare_at_price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    sku: Optional[str] = Form(None),
    status: str = Form("active"),
    is_active: bool = Form(True),
    is_featured: bool = Form(False),
    stock_quantity: int = Form(-1),
    download_limit: int = Form(0),
    file: UploadFile = File(...),
    thumbnail: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_approved_seller),
    db: Session = Depends(get_db)
):
    """Create a new product (approved sellers only)"""
    
    # Validate main file
    validate_file(file)
    
    # Generate unique filename
    file_extension = ALLOWED_FILE_TYPES.get(file.content_type, 'bin')
    unique_filename = generate_unique_filename(file.filename or "file")
    file_path = UPLOAD_DIR / unique_filename
    
    # Save main file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Handle thumbnail if provided
    thumbnail_path = None
    thumbnail_name = None
    if thumbnail:
        if thumbnail.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thumbnail must be JPG or PNG"
            )
        
        thumbnail_filename = generate_unique_filename(thumbnail.filename or "thumb")
        thumbnail_file_path = UPLOAD_DIR / thumbnail_filename
        thumbnail_content = await thumbnail.read()
        with open(thumbnail_file_path, "wb") as f:
            f.write(thumbnail_content)
        
        thumbnail_path = f"/static/uploads/products/{thumbnail_filename}"
        thumbnail_name = thumbnail.filename
    
    # Create product
    db_product = Product(
        title=title,
        description=description,
        short_description=short_description,
        price=price,
        compare_at_price=compare_at_price,
        category=category,
        tags=tags,
        sku=sku,
        status=status,
        is_active=is_active,
        is_featured=is_featured,
        stock_quantity=stock_quantity,
        download_limit=download_limit,
        file_url=f"/static/uploads/products/{unique_filename}",
        file_name=file.filename,
        file_size=len(content),
        file_type=file.content_type,
        thumbnail_url=thumbnail_path,
        thumbnail_name=thumbnail_name,
        seller_id=current_user.id
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product

@router.get("/me", response_model=List[ProductResponse])
def get_my_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_approved_seller),
    db: Session = Depends(get_db)
):
    """Get current seller's products"""
    products = db.query(Product).filter(
        Product.seller_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return products

@router.get("/", response_model=List[ProductList])
def get_public_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|price|sold_count|rating)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """Get public product listings"""
    query = db.query(Product).filter(
        Product.is_active == True,
        Product.status == "active"
    )
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(
            Product.title.ilike(f"%{search}%") | 
            Product.description.ilike(f"%{search}%")
        )
    
    # Apply sorting
    if sort_by == "created_at":
        order_column = Product.created_at
    elif sort_by == "price":
        order_column = Product.price
    elif sort_by == "sold_count":
        order_column = Product.sold_count
    elif sort_by == "rating":
        order_column = Product.average_rating
    else:
        order_column = Product.created_at
    
    if sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    products = query.offset(skip).limit(limit).all()
    
    # Convert to ProductList schema
    result = []
    for product in products:
        result.append(ProductList(
            id=product.id,
            title=product.title,
            short_description=product.short_description,
            price=product.price,
            compare_at_price=product.compare_at_price,
            thumbnail_url=product.thumbnail_url,
            seller_name=product.seller.store_name or product.seller.username,
            seller_rating=product.seller.seller_rating,
            sold_count=product.sold_count,
            average_rating=product.average_rating,
            review_count=product.review_count,
            is_featured=product.is_featured,
            created_at=product.created_at
        ))
    
    return result

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get single product details"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True,
        Product.status == "active"
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    compare_at_price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    sku: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    is_featured: Optional[bool] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    download_limit: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    thumbnail: Optional[UploadFile] = File(None),
    product: Product = Depends(check_product_ownership),
    db: Session = Depends(get_db)
):
    """Update product (owner only)"""
    
    # Update text fields
    if title is not None:
        product.title = title
    if description is not None:
        product.description = description
    if short_description is not None:
        product.short_description = short_description
    if price is not None:
        product.price = price
    if compare_at_price is not None:
        product.compare_at_price = compare_at_price
    if category is not None:
        product.category = category
    if tags is not None:
        product.tags = tags
    if sku is not None:
        product.sku = sku
    if status is not None:
        product.status = status
    if is_active is not None:
        product.is_active = is_active
    if is_featured is not None:
        product.is_featured = is_featured
    if stock_quantity is not None:
        product.stock_quantity = stock_quantity
    if download_limit is not None:
        product.download_limit = download_limit
    
    # Handle file update
    if file:
        validate_file(file)
        
        # Delete old file
        if product.file_url and product.file_name:
            old_file_path = Path("uploads") / product.file_url.replace("/static/uploads/", "")
            if old_file_path.exists():
                old_file_path.unlink()
        
        # Save new file
        file_extension = ALLOWED_FILE_TYPES.get(file.content_type, 'bin')
        unique_filename = generate_unique_filename(file.filename or "file")
        file_path = UPLOAD_DIR / unique_filename
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        product.file_url = f"/static/uploads/products/{unique_filename}"
        product.file_name = file.filename
        product.file_size = len(content)
        product.file_type = file.content_type
    
    # Handle thumbnail update
    if thumbnail:
        if thumbnail.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Thumbnail must be JPG or PNG"
            )
        
        # Delete old thumbnail
        if product.thumbnail_url and product.thumbnail_name:
            old_thumb_path = Path("uploads") / product.thumbnail_url.replace("/static/uploads/", "")
            if old_thumb_path.exists():
                old_thumb_path.unlink()
        
        # Save new thumbnail
        thumbnail_filename = generate_unique_filename(thumbnail.filename or "thumb")
        thumbnail_file_path = UPLOAD_DIR / thumbnail_filename
        thumbnail_content = await thumbnail.read()
        with open(thumbnail_file_path, "wb") as f:
            f.write(thumbnail_content)
        
        product.thumbnail_url = f"/static/uploads/products/{thumbnail_filename}"
        product.thumbnail_name = thumbnail.filename
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    product: Product = Depends(check_product_ownership),
    db: Session = Depends(get_db)
):
    """Delete product (owner only)"""
    
    # Soft delete
    product.is_active = False
    product.status = "archived"
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.post("/upload", response_model=ProductFileUpload)
async def upload_product_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_approved_seller)
):
    """Upload product file separately (for drag-and-drop)"""
    
    validate_file(file)
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename or "file")
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    return ProductFileUpload(
        file_url=f"/static/uploads/products/{unique_filename}",
        file_name=file.filename,
        file_size=len(content),
        file_type=file.content_type
    )
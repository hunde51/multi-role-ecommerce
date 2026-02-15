from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, UserRole
from app.api.auth import get_current_user

def get_approved_seller(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dependency to ensure user is an approved seller"""
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller access required"
        )
    
    if not current_user.is_seller_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller account not approved. Please wait for admin approval."
        )
    
    return current_user

def get_admin_user(
    current_user: User = Depends(get_current_user)
):
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def get_customer_or_seller(
    current_user: User = Depends(get_current_user)
):
    """Dependency to ensure user is customer or seller"""
    if current_user.role not in [UserRole.BUYER, UserRole.SELLER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Customer or seller access required"
        )
    return current_user

def check_product_ownership(
    product_id: int,
    current_user: User = Depends(get_approved_seller),
    db: Session = Depends(get_db)
):
    """Dependency to check if user owns the product"""
    from app.models.product import Product
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only manage your own products."
        )
    
    return product

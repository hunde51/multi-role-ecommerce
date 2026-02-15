from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.seller import (
    SellerApplicationResponse, 
    SellerApprovalRequest,
    SellerProfile
)
from app.api.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def get_admin_user(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/sellers", response_model=List[SellerApplicationResponse])
def list_seller_applications(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all seller applications (admin only)"""
    
    query = db.query(User).filter(User.role == UserRole.SELLER)
    
    if status:
        if status == "pending":
            query = query.filter(User.store_name.isnot(None), User.is_seller_approved == False)
        elif status == "approved":
            query = query.filter(User.is_seller_approved == True)
        elif status == "rejected":
            query = query.filter(User.store_name.is_(None))
    
    sellers = query.offset(skip).limit(limit).all()
    
    result = []
    for seller in sellers:
        app_status = "pending"
        if seller.is_seller_approved:
            app_status = "approved"
        elif seller.store_name is None:
            app_status = "rejected"
        
        result.append(SellerApplicationResponse(
            id=seller.id,
            email=seller.email,
            store_name=seller.store_name or "",
            seller_bio=seller.seller_bio or "",
            seller_address=seller.seller_address or "",
            seller_tax_id=seller.seller_tax_id,
            status=app_status,
            created_at=seller.created_at,
            updated_at=seller.updated_at
        ))
    
    return result

@router.patch("/sellers/{user_id}/approve", response_model=SellerApplicationResponse)
def approve_reject_seller(
    user_id: int,
    approval: SellerApprovalRequest,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Approve or reject a seller application (admin only)"""
    
    seller = db.query(User).filter(User.id == user_id).first()
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found"
        )
    
    if seller.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a seller applicant"
        )
    
    if approval.status == "approved":
        seller.is_seller_approved = True
        seller.seller_verified = True  # Auto-verify for now
    elif approval.status == "rejected":
        # Clear seller application data
        seller.store_name = None
        seller.seller_bio = None
        seller.seller_address = None
        seller.seller_tax_id = None
        seller.is_seller_approved = False
        seller.role = UserRole.BUYER  # Revert to buyer
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'approved' or 'rejected'"
        )
    
    db.commit()
    db.refresh(seller)
    
    # Determine final status
    final_status = approval.status
    if approval.status == "rejected":
        final_status = "rejected"
    
    return SellerApplicationResponse(
        id=seller.id,
        email=seller.email,
        store_name=seller.store_name or "",
        seller_bio=seller.seller_bio or "",
        seller_address=seller.seller_address or "",
        seller_tax_id=seller.seller_tax_id,
        status=final_status,
        created_at=seller.created_at,
        updated_at=seller.updated_at
    )

@router.get("/sellers/{user_id}", response_model=SellerProfile)
def get_seller_details(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed seller information (admin only)"""
    
    seller = db.query(User).filter(
        User.id == user_id,
        User.role == UserRole.SELLER
    ).first()
    
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found"
        )
    
    return SellerProfile(
        id=seller.id,
        email=seller.email,
        username=seller.username,
        full_name=seller.full_name,
        store_name=seller.store_name,
        seller_bio=seller.seller_bio,
        seller_address=seller.seller_address,
        seller_tax_id=seller.seller_tax_id,
        is_seller_approved=seller.is_seller_approved,
        seller_verified=seller.seller_verified,
        total_sales=seller.total_sales,
        total_products=seller.total_products,
        seller_rating=seller.seller_rating,
        created_at=seller.created_at
    )

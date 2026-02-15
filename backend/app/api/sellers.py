from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.seller import (
    SellerApplication, 
    SellerApplicationResponse, 
    SellerApprovalRequest,
    SellerProfile
)
from app.api.auth import get_current_user

router = APIRouter(prefix="/sellers", tags=["sellers"])

@router.post("/apply", response_model=SellerApplicationResponse)
def apply_as_seller(
    application: SellerApplication,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply to become a seller"""
    
    # Check if user is already a seller or has pending application
    if current_user.role == UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already registered as a seller"
        )
    
    if current_user.is_seller_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your seller application has already been approved"
        )
    
    # Check if user already has a pending application
    if current_user.store_name:  # Simple check - if store_name exists, application exists
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending seller application"
        )
    
    # Validate terms acceptance
    if not application.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must accept the terms and conditions to apply as a seller"
        )
    
    # Update user with seller application details
    current_user.role = UserRole.SELLER
    current_user.store_name = application.store_name
    current_user.seller_bio = application.seller_bio
    current_user.seller_address = application.seller_address
    current_user.seller_tax_id = application.seller_tax_id
    current_user.is_seller_approved = False  # Explicitly set to False
    
    db.commit()
    db.refresh(current_user)
    
    return SellerApplicationResponse(
        id=current_user.id,
        email=current_user.email,
        store_name=current_user.store_name,
        seller_bio=current_user.seller_bio,
        seller_address=current_user.seller_address,
        seller_tax_id=current_user.seller_tax_id,
        status="pending",
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.get("/application-status", response_model=SellerApplicationResponse)
def get_application_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's seller application status"""
    
    if current_user.role != UserRole.SELLER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No seller application found"
        )
    
    status = "pending"
    if current_user.is_seller_approved:
        status = "approved"
    elif current_user.store_name is None:
        status = "rejected"
    
    return SellerApplicationResponse(
        id=current_user.id,
        email=current_user.email,
        store_name=current_user.store_name or "",
        seller_bio=current_user.seller_bio or "",
        seller_address=current_user.seller_address or "",
        seller_tax_id=current_user.seller_tax_id,
        status=status,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.get("/profile", response_model=SellerProfile)
def get_seller_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get seller profile (approved sellers only)"""
    
    if current_user.role != UserRole.SELLER or not current_user.is_seller_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only approved sellers can access their profile"
        )
    
    return SellerProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        store_name=current_user.store_name,
        seller_bio=current_user.seller_bio,
        seller_address=current_user.seller_address,
        seller_tax_id=current_user.seller_tax_id,
        is_seller_approved=current_user.is_seller_approved,
        seller_verified=current_user.seller_verified,
        total_sales=current_user.total_sales,
        total_products=current_user.total_products,
        seller_rating=current_user.seller_rating,
        created_at=current_user.created_at
    )

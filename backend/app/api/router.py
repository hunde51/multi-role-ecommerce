from fastapi import APIRouter

from app.api import auth, users, products, orders, sellers, admin

api_router = APIRouter(prefix="/api/v1")

# Authentication endpoints
api_router.include_router(auth.router, tags=["Authentication"])

# User endpoints
api_router.include_router(users.router, tags=["Users"])

# Product endpoints
api_router.include_router(products.router, tags=["Products"])

# Order endpoints
api_router.include_router(orders.router, tags=["Orders"])

# Seller endpoints
api_router.include_router(sellers.router, tags=["Sellers"])

# Admin endpoints
api_router.include_router(admin.router, tags=["Admin"])

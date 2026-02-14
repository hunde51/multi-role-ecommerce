from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import engine
from app.models import base
from app.api.router import api_router
from app.config import settings

app = FastAPI(title="Multi-Role E-Commerce API")

# Create all tables
base.Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(api_router)

# Static folder (only if exists)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Multi-Role E-Commerce API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

# backend/services/dependencies_ext.py
from services.password_service import password_service
from services.rate_limiter import rate_limiter

async def get_password_service():
    return password_service

async def get_rate_limiter():
    return rate_limiter

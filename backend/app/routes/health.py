from fastapi import APIRouter
from app.database import init_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Kairos Assistant API"}

# net/api/routers/health.py

from fastapi import APIRouter
router = APIRouter()
@router.get("/health")
def health():
    return {"ok": True}

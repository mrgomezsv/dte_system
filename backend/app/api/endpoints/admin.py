"""Endpoints de administración"""
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
async def get_admin():
    return {"message": "Admin endpoint - En desarrollo"} 
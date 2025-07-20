"""Endpoints de impresión"""
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
async def get_printing():
    return {"message": "Printing endpoint - En desarrollo"} 
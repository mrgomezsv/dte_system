"""Endpoints de POS"""
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
async def get_pos():
    return {"message": "POS endpoint - En desarrollo"} 
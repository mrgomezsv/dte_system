"""Endpoints de clientes"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_customers():
    return {"message": "Customers endpoint - En desarrollo"} 
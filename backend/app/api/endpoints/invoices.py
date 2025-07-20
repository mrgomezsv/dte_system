"""Endpoints de facturas"""
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
async def get_invoices():
    return {"message": "Invoices endpoint - En desarrollo"} 
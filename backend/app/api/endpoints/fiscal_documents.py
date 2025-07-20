"""Endpoints de documentos fiscales"""
from fastapi import APIRouter
router = APIRouter()
@router.get("/")
async def get_fiscal_documents():
    return {"message": "Fiscal documents endpoint - En desarrollo"} 
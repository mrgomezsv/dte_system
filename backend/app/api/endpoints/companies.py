"""
Endpoints de empresas
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_companies():
    """Obtener empresas"""
    return {"message": "Companies endpoint - En desarrollo"}

@router.post("/")
async def create_company():
    """Crear empresa"""
    return {"message": "Create company endpoint - En desarrollo"} 
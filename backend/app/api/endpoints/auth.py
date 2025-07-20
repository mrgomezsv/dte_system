"""
Endpoints de autenticación
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def auth_status():
    """Estado de autenticación"""
    return {"status": "Authentication module loaded"}

@router.post("/login")
async def login():
    """Login básico"""
    return {"message": "Login endpoint - En desarrollo"}

@router.post("/logout")
async def logout():
    """Logout básico"""
    return {"message": "Logout endpoint - En desarrollo"} 
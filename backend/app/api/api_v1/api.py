"""
Router principal de la API v1
"""
from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    companies,
    customers,
    products,
    invoices,
    pos,
    printing,
    reports,
    admin,
    fiscal_documents
)

api_router = APIRouter()

# Incluir todos los routers de endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["🔐 Autenticación"])
api_router.include_router(companies.router, prefix="/companies", tags=["🏢 Empresas"])
api_router.include_router(customers.router, prefix="/customers", tags=["👥 Clientes"])
api_router.include_router(products.router, prefix="/products", tags=["📦 Productos"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["🧾 Facturas"])
api_router.include_router(fiscal_documents.router, prefix="/fiscal-documents", tags=["📄 Documentos Fiscales"])
api_router.include_router(pos.router, prefix="/pos", tags=["🏪 Punto de Venta"])
api_router.include_router(printing.router, prefix="/printing", tags=["🖨️ Impresión"])
api_router.include_router(reports.router, prefix="/reports", tags=["📊 Reportes"])
api_router.include_router(admin.router, prefix="/admin", tags=["⚙️ Administración"]) 
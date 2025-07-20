"""
Sistema de Endpoints Dinámicos Personalizados por Cliente
"""
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.models.client_endpoint import ClientEndpoint

logger = logging.getLogger(__name__)

# Router para endpoints dinámicos
dynamic_router = APIRouter()

async def setup_dynamic_routes(app: FastAPI):
    """
    Configurar rutas dinámicas al inicio de la aplicación
    """
    logger.info("🔧 Configurando endpoints dinámicos...")
    
    # En una implementación real, cargaríamos esto desde la base de datos
    # Por ahora, creamos algunos endpoints de ejemplo
    
    @app.get("/api/v1/client/{client_code}/invoices")
    async def client_invoices(
        client_code: str,
        request: Request,
        db: Session = Depends(get_db)
    ):
        """Endpoint dinámico para obtener facturas del cliente"""
        return await handle_dynamic_request(
            client_code=client_code,
            path="/invoices",
            method="GET",
            request=request,
            db=db
        )
    
    @app.post("/api/v1/client/{client_code}/invoices")
    async def create_client_invoice(
        client_code: str,
        request: Request,
        db: Session = Depends(get_db)
    ):
        """Endpoint dinámico para crear facturas del cliente"""
        return await handle_dynamic_request(
            client_code=client_code,
            path="/invoices",
            method="POST",
            request=request,
            db=db
        )
    
    @app.get("/api/v1/client/{client_code}/products")
    async def client_products(
        client_code: str,
        request: Request,
        db: Session = Depends(get_db)
    ):
        """Endpoint dinámico para obtener productos del cliente"""
        return await handle_dynamic_request(
            client_code=client_code,
            path="/products",
            method="GET",
            request=request,
            db=db
        )
    
    logger.info("✅ Endpoints dinámicos configurados")


async def handle_dynamic_request(
    client_code: str,
    path: str,
    method: str,
    request: Request,
    db: Session
) -> Dict[str, Any]:
    """
    Manejar requests a endpoints dinámicos
    """
    try:
        # Buscar configuración del endpoint
        endpoint_config = db.query(ClientEndpoint).filter(
            ClientEndpoint.client_code == client_code,
            ClientEndpoint.path == path,
            ClientEndpoint.http_method == method,
            ClientEndpoint.status == "active"
        ).first()
        
        if not endpoint_config:
            raise HTTPException(
                status_code=404,
                detail=f"Endpoint no encontrado: {method} /client/{client_code}{path}"
            )
        
        # Verificar autenticación
        if not await verify_client_auth(request, endpoint_config):
            raise HTTPException(
                status_code=401,
                detail="Autenticación fallida"
            )
        
        # Obtener datos del request
        request_data = {}
        if method in ["POST", "PUT", "PATCH"]:
            request_data = await request.json()
        
        # Validar esquema del request
        is_valid, errors = endpoint_config.validate_request_schema(request_data)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"error": "Esquema inválido", "details": errors}
            )
        
        # Ejecutar lógica de negocio
        response_data = await execute_business_logic(
            endpoint_config=endpoint_config,
            request_data=request_data,
            db=db
        )
        
        # Registrar estadísticas
        endpoint_config.record_request(success=True)
        db.commit()
        
        return {
            "success": True,
            "data": response_data,
            "client": client_code,
            "endpoint": path
        }
        
    except HTTPException:
        # Registrar fallo
        if 'endpoint_config' in locals():
            endpoint_config.record_request(success=False)
            db.commit()
        raise
    
    except Exception as e:
        logger.error(f"Error en endpoint dinámico: {e}")
        
        # Registrar fallo
        if 'endpoint_config' in locals():
            endpoint_config.record_request(success=False)
            db.commit()
        
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


async def verify_client_auth(request: Request, endpoint_config: ClientEndpoint) -> bool:
    """
    Verificar autenticación del cliente
    """
    if endpoint_config.is_public:
        return True
    
    # Verificar API Key
    if endpoint_config.auth_type == "api_key":
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
        if api_key and api_key.replace("Bearer ", "") == endpoint_config.api_key:
            return True
    
    # Verificar Bearer Token
    elif endpoint_config.auth_type == "bearer_token":
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Aquí iría la validación del token JWT
            return True
    
    return False


async def execute_business_logic(
    endpoint_config: ClientEndpoint,
    request_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Ejecutar lógica de negocio del endpoint
    """
    business_type = endpoint_config.business_logic_type
    
    if business_type == "invoice":
        return await handle_invoice_logic(endpoint_config, request_data, db)
    elif business_type == "product":
        return await handle_product_logic(endpoint_config, request_data, db)
    elif business_type == "customer":
        return await handle_customer_logic(endpoint_config, request_data, db)
    else:
        # Lógica personalizada
        return await handle_custom_logic(endpoint_config, request_data, db)


async def handle_invoice_logic(
    endpoint_config: ClientEndpoint,
    request_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Manejar lógica de facturas
    """
    from app.models.invoice import Invoice
    
    if endpoint_config.http_method == "GET":
        # Obtener facturas
        invoices = db.query(Invoice).filter(
            Invoice.company_id == endpoint_config.company_id
        ).limit(10).all()
        
        return {
            "invoices": [
                {
                    "id": inv.id,
                    "number": inv.invoice_number,
                    "total": float(inv.total_amount),
                    "status": inv.status.value,
                    "date": inv.issue_date.isoformat()
                }
                for inv in invoices
            ]
        }
    
    elif endpoint_config.http_method == "POST":
        # Crear factura (lógica simplificada)
        return {
            "message": "Factura creada exitosamente",
            "invoice_id": "INV-001",
            "status": "created"
        }
    
    return {"message": "Operación completada"}


async def handle_product_logic(
    endpoint_config: ClientEndpoint,
    request_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Manejar lógica de productos
    """
    from app.models.product import Product
    
    if endpoint_config.http_method == "GET":
        # Obtener productos
        products = db.query(Product).filter(
            Product.company_id == endpoint_config.company_id,
            Product.is_active == True
        ).limit(10).all()
        
        return {
            "products": [
                {
                    "id": prod.id,
                    "code": prod.code,
                    "name": prod.name,
                    "price": float(prod.sale_price),
                    "stock": float(prod.current_stock)
                }
                for prod in products
            ]
        }
    
    return {"message": "Operación completada"}


async def handle_customer_logic(
    endpoint_config: ClientEndpoint,
    request_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Manejar lógica de clientes
    """
    from app.models.customer import Customer
    
    if endpoint_config.http_method == "GET":
        # Obtener clientes
        customers = db.query(Customer).filter(
            Customer.company_id == endpoint_config.company_id,
            Customer.is_active == True
        ).limit(10).all()
        
        return {
            "customers": [
                {
                    "id": cust.id,
                    "name": cust.name,
                    "document": cust.document_number,
                    "email": cust.email
                }
                for cust in customers
            ]
        }
    
    return {"message": "Operación completada"}


async def handle_custom_logic(
    endpoint_config: ClientEndpoint,
    request_data: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Manejar lógica personalizada
    """
    # Aquí se ejecutaría código Python personalizado del cliente
    # Por seguridad, esto debe estar muy controlado en producción
    
    if endpoint_config.custom_logic:
        # Ejecutar lógica personalizada de forma segura
        # (esto requiere un sandbox en producción)
        return {"message": "Lógica personalizada ejecutada", "result": "custom_result"}
    
    return {"message": "Endpoint personalizado activo", "data": request_data} 
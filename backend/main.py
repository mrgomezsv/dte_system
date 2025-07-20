"""
Sistema de Facturación Electrónica El Salvador
Microservicio principal FastAPI
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.core.config import settings
from app.core.database import engine, create_db_and_tables
from app.api.api_v1.api import api_router
from app.api.endpoints.dynamic_endpoints import setup_dynamic_routes

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando Sistema de Facturación Electrónica...")
    await create_db_and_tables()
    await setup_dynamic_routes(app)
    logger.info("✅ Sistema iniciado correctamente")
    
    yield
    
    # Shutdown
    logger.info("🔄 Cerrando conexiones...")
    await engine.dispose()
    logger.info("👋 Sistema cerrado correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema Facturación Electrónica El Salvador",
    description="""
    ## 🧾 API para Facturación Electrónica
    
    Sistema completo que incluye:
    
    * **Comprobantes fiscales** oficiales (CCF, Facturas, etc.)
    * **Punto de Venta (POS)** integrado
    * **Sistema de impresión** de tickets
    * **Endpoints personalizados** por cliente
    * **Integración Ministerio Hacienda** El Salvador
    
    ### Documentos soportados:
    - ✅ Crédito Fiscal (CCF)
    - ✅ Factura de Exportación  
    - ✅ Nota de Crédito/Débito
    - ✅ Comprobante de Retención
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Middleware de seguridad
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Información del request
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"📥 {request.method} {request.url.path} - Cliente: {client_host}")
    
    # Procesar request
    response = await call_next(request)
    
    # Calcular tiempo de procesamiento
    process_time = time.time() - start_time
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Tiempo: {process_time:.3f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado",
            "path": str(request.url.path)
        }
    )


# Incluir routers de API
app.include_router(api_router, prefix="/api/v1")


# Endpoint de health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Verificar estado del sistema"""
    return {
        "status": "healthy",
        "service": "Facturación Electrónica El Salvador",
        "version": "1.0.0",
        "timestamp": time.time()
    }


# Endpoint raíz
@app.get("/", tags=["Root"])
async def root():
    """Información principal del servicio"""
    return {
        "message": "🧾 Sistema de Facturación Electrónica El Salvador",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Comprobantes fiscales oficiales",
            "Punto de Venta integrado", 
            "Sistema de impresión",
            "Endpoints personalizados",
            "Integración Ministerio Hacienda"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    ) 
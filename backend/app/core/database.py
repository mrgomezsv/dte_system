"""
Configuración de base de datos PostgreSQL con SQLAlchemy
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from typing import AsyncGenerator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Motor de base de datos asíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries en desarrollo
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Motor síncrono para migraciones con Alembic
sync_engine = create_engine(
    settings.DATABASE_URL_SYNC,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False,
)

# Base para modelos
Base = declarative_base()


# Dependency para obtener sesión de DB
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que proporciona una sesión de base de datos asíncrona
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Error en transacción de DB: {e}")
            raise
        finally:
            await session.close()


# Función para crear tablas
async def create_db_and_tables():
    """
    Crear todas las tablas en la base de datos
    """
    try:
        async with engine.begin() as conn:
            # Importar todos los modelos aquí para asegurar que estén registrados
            from app.models.user import User
            from app.models.company import Company
            from app.models.customer import Customer
            from app.models.product import Product
            from app.models.invoice import Invoice, InvoiceItem
            from app.models.fiscal_document import FiscalDocument
            from app.models.printer_config import PrinterConfig
            from app.models.client_endpoint import ClientEndpoint
            
            logger.info("🗃️  Creando tablas de base de datos...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Tablas creadas exitosamente")
            
    except Exception as e:
        logger.error(f"❌ Error creando tablas: {e}")
        raise


# Función para obtener sesión síncrona (para migraciones)
def get_sync_db():
    """
    Obtener sesión síncrona para operaciones de migración
    """
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


# Función para verificar conexión
async def check_db_connection():
    """
    Verificar que la conexión a la base de datos funciona
    """
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        return False


# Context manager para transacciones manuales
class DatabaseTransaction:
    """
    Context manager para manejar transacciones de base de datos manualmente
    """
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
            logger.error(f"Error en transacción: {exc_val}")
        else:
            await self.session.commit()
        
        await self.session.close()
        

# Función utilitaria para ejecutar queries raw
async def execute_raw_query(query: str, params: dict = None):
    """
    Ejecutar query SQL raw de manera segura
    """
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(query, params or {})
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            logger.error(f"Error ejecutando query: {e}")
            raise


# Configuración de índices y optimizaciones
async def setup_database_optimizations():
    """
    Configurar índices y optimizaciones específicas para facturación
    """
    optimizations = [
        # Índices para búsquedas de facturas
        "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_invoice_customer ON invoices(customer_id);",
        "CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoices(status);",
        "CREATE INDEX IF NOT EXISTS idx_invoice_fiscal_number ON invoices(fiscal_number);",
        
        # Índices para documentos fiscales
        "CREATE INDEX IF NOT EXISTS idx_fiscal_doc_type ON fiscal_documents(document_type);",
        "CREATE INDEX IF NOT EXISTS idx_fiscal_doc_date ON fiscal_documents(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_fiscal_doc_status ON fiscal_documents(status);",
        
        # Índices para productos
        "CREATE INDEX IF NOT EXISTS idx_product_code ON products(code);",
        "CREATE INDEX IF NOT EXISTS idx_product_active ON products(is_active);",
        
        # Índices para clientes
        "CREATE INDEX IF NOT EXISTS idx_customer_nit ON customers(nit);",
        "CREATE INDEX IF NOT EXISTS idx_customer_email ON customers(email);",
        
        # Índices compuestos para reportes
        "CREATE INDEX IF NOT EXISTS idx_invoice_company_date ON invoices(company_id, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_fiscal_company_type ON fiscal_documents(company_id, document_type);",
    ]
    
    try:
        async with engine.begin() as conn:
            for optimization in optimizations:
                await conn.execute(optimization)
        logger.info("✅ Optimizaciones de base de datos aplicadas")
    except Exception as e:
        logger.error(f"❌ Error aplicando optimizaciones: {e}")


# Función para backup de base de datos
async def backup_database(backup_path: str = None):
    """
    Crear backup de la base de datos (requiere pg_dump)
    """
    import subprocess
    import datetime
    
    if not backup_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{settings.BACKUP_DIR}/backup_{timestamp}.sql"
    
    try:
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_SERVER,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", backup_path,
            "--no-password"
        ]
        
        env = {"PGPASSWORD": settings.POSTGRES_PASSWORD}
        
        process = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if process.returncode == 0:
            logger.info(f"✅ Backup creado: {backup_path}")
            return backup_path
        else:
            logger.error(f"❌ Error creando backup: {process.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error en backup: {e}")
        return None 
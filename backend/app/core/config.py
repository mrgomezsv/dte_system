"""
Configuración central del sistema de facturación electrónica
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Configuración principal del sistema"""
    
    # Información del proyecto
    PROJECT_NAME: str = "Sistema Facturación Electrónica El Salvador"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Microservicio para facturación electrónica en El Salvador"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días
    
    # Security
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Frontend React
        "http://localhost:8080",  # Admin Panel
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    
    # Base de datos PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "facturacion_db"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property 
    def DATABASE_URL_SYNC(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Celery Configuration (para tareas asíncronas)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @property
    def CELERY_BROKER(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    @property
    def CELERY_BACKEND(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL
    
    # Configuración de facturación electrónica El Salvador
    HACIENDA_BASE_URL: str = "https://apitest.dtes.mh.gob.sv/fesv/recepciondte"
    HACIENDA_PRODUCTION_URL: str = "https://api.dtes.mh.gob.sv/fesv/recepciondte"
    HACIENDA_ENVIRONMENT: str = "test"  # test | production
    
    # Certificados digitales para firmado
    CERTIFICATE_PATH: str = "./certificates/"
    PRIVATE_KEY_PATH: str = "./certificates/private.key"
    PUBLIC_CERT_PATH: str = "./certificates/public.crt"
    CERTIFICATE_PASSWORD: Optional[str] = None
    
    # Configuración de impresión
    PRINTER_ENABLED: bool = True
    DEFAULT_PRINTER_NAME: Optional[str] = None
    THERMAL_PRINTER_PORT: str = "/dev/ttyUSB0"  # Puerto impresora térmica
    TICKET_WIDTH: int = 80  # Ancho en mm (58 o 80)
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Archivos y storage
    UPLOAD_DIR: str = "./uploads"
    INVOICE_TEMPLATES_DIR: str = "./templates/invoices"
    BACKUP_DIR: str = "./backups"
    
    # Límites y configuración
    MAX_INVOICE_ITEMS: int = 100
    MAX_FILE_SIZE_MB: int = 10
    INVOICE_EXPIRY_DAYS: int = 30
    
    # Configuración de logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/facturacion.log"
    
    # Configuración de empresa por defecto
    DEFAULT_COMPANY_NAME: str = "Mi Empresa SV"
    DEFAULT_COMPANY_NIT: str = "0000000000000"
    DEFAULT_COMPANY_ADDRESS: str = "San Salvador, El Salvador"
    DEFAULT_COMPANY_PHONE: str = "+503 2222-2222"
    DEFAULT_COMPANY_EMAIL: str = "empresa@ejemplo.com"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Configuración de desarrollo
    DEBUG: bool = False
    TESTING: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()


# Función para validar configuración
def validate_settings():
    """Valida que las configuraciones críticas estén presentes"""
    errors = []
    
    if not settings.SECRET_KEY or settings.SECRET_KEY == "super-secret-key-change-in-production":
        errors.append("SECRET_KEY debe ser configurada en producción")
    
    if settings.HACIENDA_ENVIRONMENT == "production" and "test" in settings.HACIENDA_BASE_URL:
        errors.append("URL de Hacienda debe ser de producción cuando HACIENDA_ENVIRONMENT=production")
    
    # Verificar que existan los directorios necesarios
    for directory in [settings.UPLOAD_DIR, settings.INVOICE_TEMPLATES_DIR, settings.BACKUP_DIR]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    if errors:
        raise ValueError(f"Errores de configuración: {'; '.join(errors)}")
    
    return True


# Configuraciones específicas por ambiente
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    HACIENDA_ENVIRONMENT: str = "test"


class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    HACIENDA_ENVIRONMENT: str = "production"
    ALLOWED_HOSTS: List[str] = ["api.miempresa.com", "localhost"]


class TestSettings(Settings):
    TESTING: bool = True
    POSTGRES_DB: str = "facturacion_test_db"


# Factory para obtener configuración según ambiente
def get_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestSettings()
    else:
        return DevelopmentSettings() 
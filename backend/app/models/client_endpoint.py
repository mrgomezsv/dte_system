"""
Modelo de Endpoints Personalizados por Cliente
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class HttpMethod(str, enum.Enum):
    """Métodos HTTP soportados"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class EndpointStatus(str, enum.Enum):
    """Estados del endpoint"""
    ACTIVE = "active"  # Activo
    INACTIVE = "inactive"  # Inactivo
    TESTING = "testing"  # En pruebas
    DEPRECATED = "deprecated"  # Deprecado


class AuthType(str, enum.Enum):
    """Tipos de autenticación"""
    NONE = "none"  # Sin autenticación
    API_KEY = "api_key"  # API Key
    BEARER_TOKEN = "bearer_token"  # Bearer Token
    BASIC_AUTH = "basic_auth"  # Autenticación básica
    CUSTOM = "custom"  # Personalizada


class ClientEndpoint(Base):
    """Modelo de Endpoint Personalizado por Cliente"""
    __tablename__ = "client_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Información básica del endpoint
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    path = Column(String(200), nullable=False, index=True)  # /api/client/{client_code}/custom-endpoint
    full_url = Column(String(500), nullable=True)  # URL completa generada
    
    # Configuración HTTP
    http_method = Column(Enum(HttpMethod), default=HttpMethod.GET)
    content_type = Column(String(100), default="application/json")
    
    # Cliente/organización
    client_code = Column(String(50), nullable=False, index=True)  # Código único del cliente
    client_name = Column(String(200), nullable=False)
    contact_email = Column(String(100), nullable=True)
    
    # Configuración de autenticación
    auth_type = Column(Enum(AuthType), default=AuthType.API_KEY)
    api_key = Column(String(255), nullable=True)  # API Key del cliente
    auth_config = Column(JSON, nullable=True)  # Configuración adicional de auth
    
    # Configuración del endpoint
    request_schema = Column(JSON, nullable=True)  # Esquema del request esperado
    response_schema = Column(JSON, nullable=True)  # Esquema de la respuesta
    default_parameters = Column(JSON, nullable=True)  # Parámetros por defecto
    
    # Lógica de negocio
    business_logic_type = Column(String(50), nullable=False)  # Tipo de lógica (invoice, product, etc.)
    custom_logic = Column(Text, nullable=True)  # Lógica personalizada en Python
    mapping_config = Column(JSON, nullable=True)  # Mapeo de campos
    
    # Límites y configuración
    rate_limit_per_minute = Column(Integer, default=60)  # Límite de requests por minuto
    rate_limit_per_hour = Column(Integer, default=1000)  # Límite de requests por hora
    max_request_size_mb = Column(Integer, default=10)  # Tamaño máximo del request
    
    # Estado y monitoreo
    status = Column(Enum(EndpointStatus), default=EndpointStatus.TESTING, index=True)
    is_public = Column(Boolean, default=False)  # Endpoint público (sin auth)
    requires_company_context = Column(Boolean, default=True)  # Requiere contexto de empresa
    
    # Estadísticas de uso
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_request_date = Column(DateTime(timezone=True), nullable=True)
    avg_response_time_ms = Column(Integer, default=0)
    
    # Configuración de logging
    log_requests = Column(Boolean, default=True)  # Loggear requests
    log_responses = Column(Boolean, default=False)  # Loggear respuestas
    retention_days = Column(Integer, default=30)  # Días de retención de logs
    
    # Webhooks y notificaciones
    webhook_url = Column(String(500), nullable=True)  # URL de webhook para notificaciones
    webhook_events = Column(JSON, nullable=True)  # Eventos que disparan webhook
    notification_emails = Column(JSON, nullable=True)  # Emails para notificaciones
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_tested_date = Column(DateTime(timezone=True), nullable=True)
    
    # Versioning
    version = Column(String(10), default="1.0")
    is_deprecated = Column(Boolean, default=False)
    deprecation_date = Column(DateTime(timezone=True), nullable=True)
    replacement_endpoint_id = Column(Integer, ForeignKey("client_endpoints.id"), nullable=True)
    
    # Relaciones
    company = relationship("Company", back_populates="client_endpoints")
    created_by = relationship("User", foreign_keys=[created_by_id])
    replacement_endpoint = relationship("ClientEndpoint", remote_side=[id])
    
    def __repr__(self):
        return f"<ClientEndpoint(client='{self.client_code}', path='{self.path}')>"
    
    @property
    def endpoint_url(self) -> str:
        """URL completa del endpoint"""
        if self.full_url:
            return self.full_url
        return f"/api/v1/client/{self.client_code}{self.path}"
    
    @property
    def success_rate(self) -> float:
        """Tasa de éxito del endpoint"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> float:
        """Tasa de fallo del endpoint"""
        return 100.0 - self.success_rate
    
    @property
    def is_healthy(self) -> bool:
        """Verificar si el endpoint está saludable"""
        return (
            self.status == EndpointStatus.ACTIVE and
            self.success_rate >= 95.0 and
            not self.is_deprecated
        )
    
    @property
    def auth_header_name(self) -> str:
        """Nombre del header de autenticación"""
        auth_headers = {
            AuthType.API_KEY: "X-API-Key",
            AuthType.BEARER_TOKEN: "Authorization",
            AuthType.BASIC_AUTH: "Authorization"
        }
        return auth_headers.get(self.auth_type, "X-Auth")
    
    def generate_api_key(self) -> str:
        """Generar nueva API key"""
        import secrets
        import string
        
        # Generar API key de 32 caracteres
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Prefijo identificativo
        self.api_key = f"{self.client_code.upper()}_{api_key}"
        return self.api_key
    
    def validate_request_schema(self, data: dict) -> tuple[bool, list]:
        """Validar esquema del request"""
        errors = []
        
        if not self.request_schema:
            return True, errors
        
        # Aquí iría la validación real del esquema JSON
        # Por simplicidad, asumimos que es válido
        return True, errors
    
    def apply_rate_limit(self, current_requests_minute: int, current_requests_hour: int) -> bool:
        """Verificar límites de rate limiting"""
        if current_requests_minute > self.rate_limit_per_minute:
            return False
        if current_requests_hour > self.rate_limit_per_hour:
            return False
        return True
    
    def record_request(self, success: bool, response_time_ms: int = 0):
        """Registrar estadísticas de request"""
        self.total_requests += 1
        self.last_request_date = func.now()
        
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Actualizar tiempo promedio de respuesta
        if response_time_ms > 0:
            total_time = self.avg_response_time_ms * (self.total_requests - 1) + response_time_ms
            self.avg_response_time_ms = int(total_time / self.total_requests)
    
    def get_auth_config(self) -> dict:
        """Obtener configuración de autenticación"""
        base_config = {
            "type": self.auth_type.value,
            "header_name": self.auth_header_name,
            "api_key": self.api_key if self.auth_type == AuthType.API_KEY else None
        }
        
        if self.auth_config:
            base_config.update(self.auth_config)
        
        return base_config
    
    def deprecate(self, replacement_endpoint_id: int = None, deprecation_date: DateTime = None):
        """Deprecar endpoint"""
        self.is_deprecated = True
        self.status = EndpointStatus.DEPRECATED
        self.deprecation_date = deprecation_date or func.now()
        if replacement_endpoint_id:
            self.replacement_endpoint_id = replacement_endpoint_id
    
    def get_openapi_spec(self) -> dict:
        """Generar especificación OpenAPI para el endpoint"""
        spec = {
            "summary": self.name,
            "description": self.description or f"Endpoint personalizado para {self.client_name}",
            "tags": [f"Client: {self.client_name}"],
            "parameters": [],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        self.content_type: {
                            "schema": self.response_schema or {"type": "object"}
                        }
                    }
                }
            }
        }
        
        # Agregar esquema de request para POST/PUT/PATCH
        if self.http_method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH]:
            spec["requestBody"] = {
                "required": True,
                "content": {
                    self.content_type: {
                        "schema": self.request_schema or {"type": "object"}
                    }
                }
            }
        
        # Agregar configuración de autenticación
        if self.auth_type != AuthType.NONE:
            spec["security"] = [{self.auth_type.value: []}]
        
        return spec 
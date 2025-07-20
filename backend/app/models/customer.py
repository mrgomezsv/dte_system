"""
Modelo de Cliente para facturación electrónica
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class CustomerType(str, enum.Enum):
    """Tipos de cliente"""
    INDIVIDUAL = "individual"  # Persona natural
    COMPANY = "company"  # Empresa
    GOVERNMENT = "government"  # Institución gubernamental
    NONPROFIT = "nonprofit"  # ONG


class DocumentType(str, enum.Enum):
    """Tipos de documento de identificación"""
    DUI = "dui"  # Documento Único de Identidad
    NIT = "nit"  # Número de Identificación Tributaria
    PASSPORT = "passport"  # Pasaporte
    OTHER = "other"  # Otro


class Customer(Base):
    """Modelo de Cliente"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Información básica
    name = Column(String(200), nullable=False, index=True)
    commercial_name = Column(String(200), nullable=True)
    customer_type = Column(Enum(CustomerType), default=CustomerType.INDIVIDUAL)
    
    # Documentos de identificación
    document_type = Column(Enum(DocumentType), default=DocumentType.DUI)
    document_number = Column(String(20), nullable=False, index=True)
    nit = Column(String(17), nullable=True, index=True)  # NIT si es contribuyente
    nrc = Column(String(8), nullable=True)  # NRC si es contribuyente IVA
    
    # Información fiscal
    is_tax_exempt = Column(Boolean, default=False)  # Exento de impuestos
    tax_exemption_reason = Column(String(200), nullable=True)
    is_iva_contributor = Column(Boolean, default=False)  # Contribuyente IVA
    tax_rate = Column(String(10), default="13%")  # Tasa de impuesto aplicable
    
    # Información de contacto
    email = Column(String(100), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Dirección
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True, default="San Salvador")
    country = Column(String(50), nullable=False, default="El Salvador")
    postal_code = Column(String(10), nullable=True)
    
    # Información comercial
    customer_code = Column(String(20), nullable=True, unique=True, index=True)
    credit_limit = Column(String(10), default="0.00")  # Límite de crédito
    payment_terms = Column(String(50), default="Contado")  # Términos de pago
    discount_percentage = Column(String(5), default="0.00")  # Descuento por defecto
    
    # Configuración
    is_active = Column(Boolean, default=True, nullable=False)
    requires_purchase_order = Column(Boolean, default=False)  # Requiere orden de compra
    send_invoice_by_email = Column(Boolean, default=False)  # Enviar factura por email
    
    # Información adicional
    business_activity = Column(String(200), nullable=True)  # Actividad económica
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Tags separados por comas
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_purchase_date = Column(DateTime(timezone=True), nullable=True)
    total_purchases = Column(String(10), default="0.00")
    
    # Relaciones
    company = relationship("Company", back_populates="customers")
    invoices = relationship("Invoice", back_populates="customer")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<Customer(name='{self.name}', document='{self.document_number}')>"
    
    @property
    def formatted_document(self) -> str:
        """Formatear documento según el tipo"""
        if self.document_type == DocumentType.DUI and len(self.document_number) == 9:
            # Formato DUI: 00000000-0
            return f"{self.document_number[:8]}-{self.document_number[8]}"
        elif self.document_type == DocumentType.NIT and len(self.document_number) == 14:
            # Formato NIT: 0000-000000-000-0
            return f"{self.document_number[:4]}-{self.document_number[4:10]}-{self.document_number[10:13]}-{self.document_number[13]}"
        return self.document_number
    
    @property
    def formatted_nit(self) -> str:
        """Formatear NIT con guiones"""
        if self.nit and len(self.nit) == 14:
            return f"{self.nit[:4]}-{self.nit[4:10]}-{self.nit[10:13]}-{self.nit[13]}"
        return self.nit or ""
    
    @property
    def formatted_nrc(self) -> str:
        """Formatear NRC con guión"""
        if self.nrc and len(self.nrc) == 8:
            return f"{self.nrc[:6]}-{self.nrc[6]}"
        return self.nrc or ""
    
    @property
    def full_address(self) -> str:
        """Dirección completa formateada"""
        if not self.address:
            return ""
        return f"{self.address}, {self.city}, {self.department}, {self.country}"
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar (comercial si existe, sino nombre)"""
        return self.commercial_name or self.name
    
    @property
    def contact_info(self) -> dict:
        """Información de contacto consolidada"""
        return {
            "email": self.email,
            "phone": self.phone,
            "mobile": self.mobile,
            "address": self.full_address
        }
    
    def get_applicable_tax_rate(self) -> float:
        """Obtener tasa de impuesto aplicable"""
        if self.is_tax_exempt:
            return 0.0
        
        # Convertir string a float
        try:
            if self.tax_rate.endswith('%'):
                return float(self.tax_rate[:-1]) / 100
            return float(self.tax_rate) / 100
        except (ValueError, AttributeError):
            return 0.13  # 13% por defecto
    
    def can_purchase_on_credit(self, amount: float) -> bool:
        """Verificar si puede comprar a crédito"""
        try:
            credit_limit = float(self.credit_limit)
            total_purchases = float(self.total_purchases)
            return (total_purchases + amount) <= credit_limit
        except (ValueError, TypeError):
            return False 
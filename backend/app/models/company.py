"""
Modelo de Empresa/Compañía con información fiscal para El Salvador
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Decimal, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# Tabla de asociación para usuarios y compañías
company_users = Table(
    'company_users',
    Base.metadata,
    Column('company_id', Integer, ForeignKey('companies.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)


class Company(Base):
    """Modelo de Empresa/Compañía"""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Información básica
    name = Column(String(200), nullable=False, index=True)
    commercial_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Información fiscal El Salvador
    nit = Column(String(17), unique=True, nullable=False, index=True)  # NIT: 0000-000000-000-0
    nrc = Column(String(8), nullable=True, index=True)  # NRC: 000000-0
    giro = Column(String(200), nullable=False)  # Actividad económica
    codigo_actividad = Column(String(10), nullable=True)  # Código de actividad económica
    
    # Información de contacto
    email = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    website = Column(String(100), nullable=True)
    
    # Dirección
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, default="San Salvador")
    department = Column(String(100), nullable=False, default="San Salvador")
    country = Column(String(50), nullable=False, default="El Salvador")
    postal_code = Column(String(10), nullable=True)
    
    # Información del representante legal
    legal_representative = Column(String(100), nullable=True)
    legal_representative_dui = Column(String(10), nullable=True)  # DUI: 00000000-0
    legal_representative_nit = Column(String(17), nullable=True)
    
    # Configuración fiscal
    is_iva_contributor = Column(Boolean, default=True, nullable=False)  # Contribuyente IVA
    is_tax_withholding_agent = Column(Boolean, default=False)  # Agente de retención
    tax_regime = Column(String(50), default="General")  # Régimen tributario
    
    # Configuración de facturación electrónica
    hacienda_user = Column(String(50), nullable=True)  # Usuario del MH
    hacienda_password = Column(String(255), nullable=True)  # Password encriptada
    certificate_path = Column(String(255), nullable=True)  # Ruta del certificado
    certificate_password = Column(String(255), nullable=True)  # Password del certificado
    
    # Configuración de serie de documentos
    ccf_series = Column(String(10), default="CCF", nullable=False)  # Serie para Crédito Fiscal
    invoice_series = Column(String(10), default="FAC", nullable=False)  # Serie para facturas
    current_ccf_number = Column(Integer, default=1)  # Correlativo actual CCF
    current_invoice_number = Column(Integer, default=1)  # Correlativo actual facturas
    
    # Configuración del negocio
    currency = Column(String(3), default="USD", nullable=False)  # Moneda principal
    tax_rate = Column(Decimal(5, 4), default=0.13, nullable=False)  # Tasa de IVA (13%)
    
    # Configuración de impresión
    print_logo = Column(Boolean, default=True)
    logo_path = Column(String(255), nullable=True)
    print_footer_message = Column(Text, nullable=True)
    ticket_header_message = Column(Text, nullable=True)
    
    # Estado y configuración
    is_active = Column(Boolean, default=True, nullable=False)
    is_main_company = Column(Boolean, default=False)  # Empresa principal del sistema
    timezone = Column(String(50), default="America/El_Salvador")
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relaciones
    users = relationship("User", back_populates="companies", secondary=company_users)
    customers = relationship("Customer", back_populates="company")
    products = relationship("Product", back_populates="company") 
    invoices = relationship("Invoice", back_populates="company")
    fiscal_documents = relationship("FiscalDocument", back_populates="company")
    printer_configs = relationship("PrinterConfig", back_populates="company")
    client_endpoints = relationship("ClientEndpoint", back_populates="company")
    
    def __repr__(self):
        return f"<Company(name='{self.name}', nit='{self.nit}')>"
    
    @property
    def formatted_nit(self) -> str:
        """Formatear NIT con guiones"""
        if len(self.nit) == 14:
            return f"{self.nit[:4]}-{self.nit[4:10]}-{self.nit[10:13]}-{self.nit[13]}"
        return self.nit
    
    @property
    def formatted_nrc(self) -> str:
        """Formatear NRC con guión"""
        if self.nrc and len(self.nrc) == 8:
            return f"{self.nrc[:6]}-{self.nrc[6]}"
        return self.nrc or ""
    
    @property
    def next_ccf_number(self) -> str:
        """Obtener siguiente número de CCF"""
        return f"{self.ccf_series}-{self.current_ccf_number:08d}"
    
    @property
    def next_invoice_number(self) -> str:
        """Obtener siguiente número de factura"""
        return f"{self.invoice_series}-{self.current_invoice_number:08d}"
    
    def increment_ccf_number(self):
        """Incrementar correlativo de CCF"""
        self.current_ccf_number += 1
    
    def increment_invoice_number(self):
        """Incrementar correlativo de factura"""
        self.current_invoice_number += 1
    
    @property
    def full_address(self) -> str:
        """Dirección completa formateada"""
        return f"{self.address}, {self.city}, {self.department}, {self.country}" 
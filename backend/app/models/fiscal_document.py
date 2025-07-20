"""
Modelo de Documento Fiscal para El Salvador
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DocumentStatus(str, enum.Enum):
    """Estados del documento fiscal"""
    DRAFT = "draft"  # Borrador
    GENERATED = "generated"  # Generado
    SIGNED = "signed"  # Firmado
    SENT = "sent"  # Enviado al MH
    APPROVED = "approved"  # Aprobado por MH
    REJECTED = "rejected"  # Rechazado por MH
    CANCELLED = "cancelled"  # Anulado


class DocumentType(str, enum.Enum):
    """Tipos de documento fiscal según El Salvador"""
    CCF = "01"  # Crédito Fiscal
    EXPORT_INVOICE = "11"  # Factura de Exportación
    EXCLUDED_SUBJECT_INVOICE = "14"  # Factura de Sujeto Excluido
    RETENTION_VOUCHER = "05"  # Comprobante de Retención
    CREDIT_NOTE = "04"  # Nota de Crédito
    DEBIT_NOTE = "06"  # Nota de Débito
    ACCOUNTING_DOCUMENT = "03"  # Documento Contable de Liquidación


class TransmissionType(str, enum.Enum):
    """Tipos de transmisión"""
    NORMAL = "1"  # Transmisión normal
    CONTINGENCY = "2"  # Contingencia


class FiscalDocument(Base):
    """Modelo de Documento Fiscal"""
    __tablename__ = "fiscal_documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    
    # Información del documento
    document_type = Column(Enum(DocumentType), nullable=False, index=True)
    document_number = Column(String(50), nullable=False, unique=True, index=True)
    control_number = Column(String(8), nullable=False, unique=True, index=True)  # Número de control
    generation_code = Column(String(8), nullable=False)  # Código de generación
    
    # Información del DTE (Documento Tributario Electrónico)
    uuid_dte = Column(String(36), nullable=True, unique=True, index=True)  # UUID del DTE
    environment = Column(String(2), default="00")  # Ambiente (00=pruebas, 01=producción)
    version = Column(String(3), default="1")  # Versión del formato
    transmission_type = Column(Enum(TransmissionType), default=TransmissionType.NORMAL)
    
    # Fechas importantes
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    generation_date = Column(DateTime(timezone=True), server_default=func.now())
    signed_date = Column(DateTime(timezone=True), nullable=True)
    sent_date = Column(DateTime(timezone=True), nullable=True)
    approved_date = Column(DateTime(timezone=True), nullable=True)
    
    # Estado y validación
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, index=True)
    validation_code = Column(String(50), nullable=True)  # Código de validación del MH
    
    # Contenido del documento
    xml_content = Column(Text, nullable=True)  # XML firmado
    json_content = Column(Text, nullable=True)  # JSON original
    pdf_path = Column(String(500), nullable=True)  # Ruta del PDF generado
    
    # Información de firmado digital
    signature = Column(Text, nullable=True)  # Firma digital
    certificate_serial = Column(String(100), nullable=True)  # Serial del certificado
    signed_by = Column(String(200), nullable=True)  # Firmado por
    
    # Respuestas del Ministerio de Hacienda
    mh_response_json = Column(Text, nullable=True)  # Respuesta completa del MH
    mh_status_code = Column(String(10), nullable=True)  # Código de estado del MH
    mh_status_description = Column(Text, nullable=True)  # Descripción del estado
    mh_error_code = Column(String(10), nullable=True)  # Código de error
    mh_error_message = Column(Text, nullable=True)  # Mensaje de error
    
    # Información de contingencia
    is_contingency = Column(Boolean, default=False)  # Es contingencia
    contingency_reason = Column(String(500), nullable=True)  # Razón de contingencia
    original_issue_date = Column(DateTime(timezone=True), nullable=True)  # Fecha original de emisión
    
    # Información de anulación
    is_cancelled = Column(Boolean, default=False)
    cancellation_date = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancellation_request_uuid = Column(String(36), nullable=True)
    
    # Hash y verificación
    document_hash = Column(String(128), nullable=True)  # Hash del documento
    qr_code_data = Column(Text, nullable=True)  # Datos para código QR
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relaciones
    company = relationship("Company", back_populates="fiscal_documents")
    invoice = relationship("Invoice")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<FiscalDocument(type='{self.document_type}', number='{self.document_number}')>"
    
    @property
    def is_approved(self) -> bool:
        """Verificar si está aprobado por el MH"""
        return self.status == DocumentStatus.APPROVED
    
    @property
    def is_rejected(self) -> bool:
        """Verificar si fue rechazado por el MH"""
        return self.status == DocumentStatus.REJECTED
    
    @property
    def can_be_cancelled(self) -> bool:
        """Verificar si puede ser anulado"""
        return (
            not self.is_cancelled and 
            self.status in [DocumentStatus.APPROVED, DocumentStatus.SENT] and
            not self.is_contingency
        )
    
    @property
    def document_type_name(self) -> str:
        """Nombre del tipo de documento"""
        type_names = {
            DocumentType.CCF: "Crédito Fiscal",
            DocumentType.EXPORT_INVOICE: "Factura de Exportación",
            DocumentType.EXCLUDED_SUBJECT_INVOICE: "Factura de Sujeto Excluido",
            DocumentType.RETENTION_VOUCHER: "Comprobante de Retención",
            DocumentType.CREDIT_NOTE: "Nota de Crédito",
            DocumentType.DEBIT_NOTE: "Nota de Débito",
            DocumentType.ACCOUNTING_DOCUMENT: "Documento Contable de Liquidación"
        }
        return type_names.get(self.document_type, "Documento Fiscal")
    
    @property
    def full_document_number(self) -> str:
        """Número completo del documento"""
        return f"DTE-{self.document_type}-{self.document_number}"
    
    @property
    def qr_url(self) -> str:
        """URL para código QR de verificación"""
        if self.uuid_dte:
            return f"https://admin.factura.gob.sv/consultaPublica?ambiente={self.environment}&codGen={self.generation_code}&fechaEmi={self.issue_date.strftime('%d-%m-%Y')}"
        return ""
    
    def generate_control_number(self) -> str:
        """Generar número de control"""
        # Algoritmo simplificado - en producción usar el algoritmo oficial del MH
        import hashlib
        import random
        
        data = f"{self.document_type}{self.document_number}{self.issue_date.strftime('%Y%m%d')}"
        hash_obj = hashlib.md5(data.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Tomar los primeros 8 caracteres y asegurar que sean números
        control = ''.join([str(ord(c) % 10) for c in hash_hex[:8]])
        return control
    
    def generate_generation_code(self) -> str:
        """Generar código de generación"""
        # Código alfanumérico de 8 caracteres
        import random
        import string
        
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(8))
    
    def update_status(self, new_status: DocumentStatus, mh_response: dict = None):
        """Actualizar estado del documento"""
        self.status = new_status
        
        if mh_response:
            self.mh_response_json = str(mh_response)
            self.mh_status_code = mh_response.get('codigoEstado')
            self.mh_status_description = mh_response.get('descripcionEstado')
            
            if 'errors' in mh_response:
                errors = mh_response['errors']
                if errors:
                    self.mh_error_code = errors[0].get('codigo')
                    self.mh_error_message = errors[0].get('mensaje')
        
        # Actualizar fechas según el estado
        if new_status == DocumentStatus.SIGNED:
            self.signed_date = func.now()
        elif new_status == DocumentStatus.SENT:
            self.sent_date = func.now()
        elif new_status == DocumentStatus.APPROVED:
            self.approved_date = func.now()
    
    def cancel_document(self, reason: str, requester_id: int):
        """Anular documento"""
        if not self.can_be_cancelled:
            raise ValueError("Este documento no puede ser anulado")
        
        self.is_cancelled = True
        self.cancellation_date = func.now()
        self.cancellation_reason = reason
        self.status = DocumentStatus.CANCELLED 
"""
Modelos de Factura e Items para facturación electrónica
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Decimal, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    """Estados de la factura"""
    DRAFT = "draft"  # Borrador
    PENDING = "pending"  # Pendiente
    SENT = "sent"  # Enviada al MH
    APPROVED = "approved"  # Aprobada por MH
    REJECTED = "rejected"  # Rechazada por MH
    CANCELLED = "cancelled"  # Anulada


class InvoiceType(str, enum.Enum):
    """Tipos de factura"""
    CCF = "ccf"  # Crédito Fiscal
    EXPORT = "export"  # Factura de Exportación
    EXCLUDED = "excluded"  # Factura de Sujeto Excluido
    RETENTION = "retention"  # Comprobante de Retención


class PaymentMethod(str, enum.Enum):
    """Métodos de pago"""
    CASH = "cash"  # Efectivo
    CARD = "card"  # Tarjeta
    TRANSFER = "transfer"  # Transferencia
    CHECK = "check"  # Cheque
    CREDIT = "credit"  # Crédito


class Invoice(Base):
    """Modelo de Factura"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Información de la factura
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    fiscal_number = Column(String(50), nullable=True, unique=True, index=True)  # Número fiscal del MH
    invoice_type = Column(Enum(InvoiceType), default=InvoiceType.CCF)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # Fechas importantes
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
    sent_to_mh_date = Column(DateTime(timezone=True), nullable=True)
    approved_date = Column(DateTime(timezone=True), nullable=True)
    
    # Información fiscal
    control_code = Column(String(50), nullable=True)  # Código de control del MH
    uuid_dte = Column(String(50), nullable=True)  # UUID del DTE
    generation_code = Column(String(10), nullable=True)  # Código de generación
    
    # Totales monetarios
    subtotal = Column(Decimal(15, 4), default=0.0000, nullable=False)  # Subtotal
    tax_amount = Column(Decimal(15, 4), default=0.0000, nullable=False)  # Monto de IVA
    discount_amount = Column(Decimal(15, 4), default=0.0000)  # Descuento
    total_amount = Column(Decimal(15, 4), default=0.0000, nullable=False)  # Total
    
    # Información de pago
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)
    payment_terms = Column(String(100), default="Contado")
    paid_amount = Column(Decimal(15, 4), default=0.0000)  # Monto pagado
    change_amount = Column(Decimal(15, 4), default=0.0000)  # Vuelto
    
    # Referencias
    purchase_order = Column(String(50), nullable=True)  # Orden de compra
    reference_number = Column(String(50), nullable=True)  # Número de referencia
    notes = Column(Text, nullable=True)  # Observaciones
    
    # Configuración
    print_ticket = Column(Boolean, default=True)  # Imprimir ticket
    send_by_email = Column(Boolean, default=False)  # Enviar por email
    is_cash_sale = Column(Boolean, default=True)  # Venta de contado
    
    # Información del Ministerio de Hacienda
    mh_response = Column(Text, nullable=True)  # Respuesta del MH
    mh_error_message = Column(Text, nullable=True)  # Mensaje de error del MH
    xml_generated = Column(Text, nullable=True)  # XML generado
    pdf_path = Column(String(500), nullable=True)  # Ruta del PDF
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_reason = Column(Text, nullable=True)
    
    # Relaciones
    company = relationship("Company", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    created_by = relationship("User", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice(number='{self.invoice_number}', total={self.total_amount})>"
    
    @property
    def is_paid(self) -> bool:
        """Verificar si está pagada completamente"""
        return self.paid_amount >= self.total_amount
    
    @property
    def balance_due(self) -> Decimal:
        """Saldo pendiente"""
        return self.total_amount - self.paid_amount
    
    @property
    def can_be_cancelled(self) -> bool:
        """Verificar si puede ser anulada"""
        return self.status in [InvoiceStatus.DRAFT, InvoiceStatus.PENDING, InvoiceStatus.SENT]
    
    @property
    def items_count(self) -> int:
        """Cantidad de items en la factura"""
        return len(self.items)
    
    def calculate_totals(self):
        """Calcular totales de la factura"""
        subtotal = Decimal('0.0000')
        tax_amount = Decimal('0.0000')
        
        for item in self.items:
            item.calculate_totals()
            subtotal += item.subtotal
            tax_amount += item.tax_amount
        
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.total_amount = subtotal + tax_amount - self.discount_amount


class InvoiceItem(Base):
    """Modelo de Item de Factura"""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    # Información del producto
    product_code = Column(String(50), nullable=False)
    product_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    unit_measure = Column(String(20), default="unidad")
    
    # Cantidades y precios
    quantity = Column(Decimal(10, 3), nullable=False)
    unit_price = Column(Decimal(10, 4), nullable=False)
    discount_percentage = Column(Decimal(5, 2), default=0.00)
    discount_amount = Column(Decimal(10, 4), default=0.0000)
    
    # Información fiscal
    tax_rate = Column(Decimal(5, 4), default=0.1300)  # 13% IVA
    is_tax_exempt = Column(Boolean, default=False)
    
    # Totales calculados
    subtotal = Column(Decimal(15, 4), default=0.0000)  # Cantidad × Precio - Descuento
    tax_amount = Column(Decimal(15, 4), default=0.0000)  # IVA
    total_amount = Column(Decimal(15, 4), default=0.0000)  # Subtotal + IVA
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    line_number = Column(Integer, nullable=False)  # Número de línea
    
    # Relaciones
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product", back_populates="invoice_items")
    
    def __repr__(self):
        return f"<InvoiceItem(product='{self.product_name}', qty={self.quantity})>"
    
    def calculate_totals(self):
        """Calcular totales del item"""
        # Subtotal = (cantidad × precio) - descuento
        line_total = self.quantity * self.unit_price
        
        if self.discount_percentage > 0:
            self.discount_amount = line_total * (self.discount_percentage / 100)
        
        self.subtotal = line_total - self.discount_amount
        
        # Calcular IVA si no está exento
        if not self.is_tax_exempt:
            self.tax_amount = self.subtotal * self.tax_rate
        else:
            self.tax_amount = Decimal('0.0000')
        
        self.total_amount = self.subtotal + self.tax_amount
    
    @property
    def effective_unit_price(self) -> Decimal:
        """Precio unitario efectivo después de descuentos"""
        if self.quantity > 0:
            return self.subtotal / self.quantity
        return self.unit_price 
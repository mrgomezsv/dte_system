"""
Modelo de Producto para inventario y facturación
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Decimal, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ProductType(str, enum.Enum):
    """Tipos de producto"""
    PRODUCT = "product"  # Producto físico
    SERVICE = "service"  # Servicio
    COMBO = "combo"  # Combo/paquete


class UnitMeasure(str, enum.Enum):
    """Unidades de medida"""
    UNIT = "unidad"  # Unidad
    KILOGRAM = "kilogramo"  # Kilogramo
    LITER = "litro"  # Litro
    METER = "metro"  # Metro
    HOUR = "hora"  # Hora
    BOX = "caja"  # Caja
    PACKAGE = "paquete"  # Paquete


class TaxCategory(str, enum.Enum):
    """Categorías de impuestos"""
    TAXED = "gravado"  # Gravado con IVA
    EXEMPT = "exento"  # Exento de IVA
    NO_SUBJECT = "no_sujeto"  # No sujeto


class Product(Base):
    """Modelo de Producto"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Información básica
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    product_type = Column(Enum(ProductType), default=ProductType.PRODUCT)
    
    # Códigos de identificación
    code = Column(String(50), nullable=False, index=True)  # SKU interno
    barcode = Column(String(50), nullable=True, unique=True, index=True)  # Código de barras
    internal_code = Column(String(50), nullable=True)  # Código interno adicional
    
    # Categorización
    category = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    
    # Unidades y medidas
    unit_measure = Column(Enum(UnitMeasure), default=UnitMeasure.UNIT)
    weight = Column(Decimal(10, 3), nullable=True)  # Peso en kg
    dimensions = Column(String(100), nullable=True)  # Dimensiones (LxAxA)
    
    # Precios
    cost_price = Column(Decimal(10, 4), default=0.0000, nullable=False)  # Precio de costo
    sale_price = Column(Decimal(10, 4), default=0.0000, nullable=False)  # Precio de venta
    wholesale_price = Column(Decimal(10, 4), nullable=True)  # Precio mayorista
    discount_price = Column(Decimal(10, 4), nullable=True)  # Precio con descuento
    
    # Información fiscal
    tax_category = Column(Enum(TaxCategory), default=TaxCategory.TAXED)
    tax_rate = Column(Decimal(5, 4), default=0.1300, nullable=False)  # Tasa de IVA (13%)
    
    # Control de inventario
    track_inventory = Column(Boolean, default=True)  # Controlar inventario
    current_stock = Column(Decimal(10, 3), default=0.000)  # Stock actual
    min_stock = Column(Decimal(10, 3), default=0.000)  # Stock mínimo
    max_stock = Column(Decimal(10, 3), nullable=True)  # Stock máximo
    reorder_point = Column(Decimal(10, 3), default=5.000)  # Punto de reorden
    
    # Configuración
    is_active = Column(Boolean, default=True, nullable=False)
    is_for_sale = Column(Boolean, default=True)  # Disponible para venta
    is_combo = Column(Boolean, default=False)  # Es un combo
    allow_decimal_qty = Column(Boolean, default=False)  # Permite cantidades decimales
    
    # Información del proveedor
    supplier_name = Column(String(200), nullable=True)
    supplier_code = Column(String(50), nullable=True)  # Código del proveedor
    lead_time_days = Column(Integer, default=0)  # Tiempo de entrega en días
    
    # Imágenes y archivos
    image_url = Column(String(500), nullable=True)  # URL de imagen principal
    image_thumbnail = Column(String(500), nullable=True)  # Miniatura
    attachment_url = Column(String(500), nullable=True)  # Archivo adjunto
    
    # Información adicional
    notes = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Tags separados por comas
    warranty_months = Column(Integer, default=0)  # Garantía en meses
    
    # Estadísticas de ventas
    total_sold = Column(Decimal(10, 3), default=0.000)  # Total vendido
    last_sale_date = Column(DateTime(timezone=True), nullable=True)
    total_revenue = Column(Decimal(15, 4), default=0.0000)  # Ingresos totales
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relaciones
    company = relationship("Company", back_populates="products")
    invoice_items = relationship("InvoiceItem", back_populates="product")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<Product(code='{self.code}', name='{self.name}')>"
    
    @property
    def full_code(self) -> str:
        """Código completo del producto"""
        return f"{self.code}-{self.barcode}" if self.barcode else self.code
    
    @property
    def formatted_price(self) -> str:
        """Precio formateado con símbolo de moneda"""
        return f"${self.sale_price:.2f}"
    
    @property
    def profit_margin(self) -> float:
        """Margen de ganancia en porcentaje"""
        if self.cost_price > 0:
            return ((self.sale_price - self.cost_price) / self.cost_price) * 100
        return 0.0
    
    @property
    def profit_amount(self) -> Decimal:
        """Ganancia por unidad"""
        return self.sale_price - self.cost_price
    
    @property
    def is_low_stock(self) -> bool:
        """Verificar si está en stock bajo"""
        if not self.track_inventory:
            return False
        return self.current_stock <= self.min_stock
    
    @property
    def is_out_of_stock(self) -> bool:
        """Verificar si está agotado"""
        if not self.track_inventory:
            return False
        return self.current_stock <= 0
    
    @property
    def stock_status(self) -> str:
        """Estado del stock"""
        if not self.track_inventory:
            return "no_tracked"
        elif self.is_out_of_stock:
            return "out_of_stock"
        elif self.is_low_stock:
            return "low_stock"
        else:
            return "in_stock"
    
    @property
    def tax_amount(self) -> Decimal:
        """Monto de impuesto por unidad"""
        if self.tax_category == TaxCategory.TAXED:
            return self.sale_price * self.tax_rate
        return Decimal('0.0000')
    
    @property
    def total_price_with_tax(self) -> Decimal:
        """Precio total con impuestos"""
        return self.sale_price + self.tax_amount
    
    def can_sell_quantity(self, quantity: Decimal) -> bool:
        """Verificar si se puede vender la cantidad solicitada"""
        if not self.track_inventory:
            return True
        return self.current_stock >= quantity
    
    def get_price_for_customer(self, customer_type: str = "regular", quantity: Decimal = 1) -> Decimal:
        """Obtener precio según tipo de cliente"""
        if customer_type == "wholesale" and self.wholesale_price:
            return self.wholesale_price
        elif customer_type == "discount" and self.discount_price:
            return self.discount_price
        else:
            return self.sale_price
    
    def update_stock(self, quantity_change: Decimal, operation: str = "sale"):
        """Actualizar stock del producto"""
        if not self.track_inventory:
            return
        
        if operation == "sale":
            self.current_stock -= quantity_change
            self.total_sold += quantity_change
            self.last_sale_date = func.now()
        elif operation == "purchase":
            self.current_stock += quantity_change
        elif operation == "adjustment":
            self.current_stock = quantity_change
    
    def calculate_total_value(self) -> Decimal:
        """Calcular valor total del inventario"""
        return self.current_stock * self.cost_price 
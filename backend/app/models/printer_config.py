"""
Modelo de Configuración de Impresora
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class PrinterType(str, enum.Enum):
    """Tipos de impresora"""
    THERMAL = "thermal"  # Térmica
    INKJET = "inkjet"  # Inyección de tinta
    LASER = "laser"  # Láser
    MATRIX = "matrix"  # Matriz de puntos


class PrinterConnection(str, enum.Enum):
    """Tipos de conexión"""
    USB = "usb"  # USB
    SERIAL = "serial"  # Puerto serie
    NETWORK = "network"  # Red/IP
    BLUETOOTH = "bluetooth"  # Bluetooth


class PaperSize(str, enum.Enum):
    """Tamaños de papel"""
    SIZE_58MM = "58mm"  # 58mm (térmico)
    SIZE_80MM = "80mm"  # 80mm (térmico)
    LETTER = "letter"  # Carta
    A4 = "a4"  # A4
    CUSTOM = "custom"  # Personalizado


class PrinterConfig(Base):
    """Modelo de Configuración de Impresora"""
    __tablename__ = "printer_configs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Información básica
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    printer_type = Column(Enum(PrinterType), default=PrinterType.THERMAL)
    
    # Conexión
    connection_type = Column(Enum(PrinterConnection), default=PrinterConnection.USB)
    connection_string = Column(String(200), nullable=False)  # Puerto, IP, etc.
    
    # Configuración de papel
    paper_size = Column(Enum(PaperSize), default=PaperSize.SIZE_80MM)
    paper_width_mm = Column(Integer, default=80)  # Ancho en mm
    characters_per_line = Column(Integer, default=42)  # Caracteres por línea
    
    # Configuración de impresión
    print_speed = Column(Integer, default=5)  # Velocidad (1-9)
    print_density = Column(Integer, default=5)  # Densidad (1-15)
    auto_cut = Column(Boolean, default=True)  # Corte automático
    cut_lines = Column(Integer, default=3)  # Líneas antes del corte
    
    # Configuración del ticket
    print_header = Column(Boolean, default=True)  # Imprimir encabezado
    print_logo = Column(Boolean, default=False)  # Imprimir logo
    logo_path = Column(String(500), nullable=True)  # Ruta del logo
    header_lines = Column(Integer, default=2)  # Líneas de encabezado
    footer_lines = Column(Integer, default=2)  # Líneas de pie
    
    # Mensajes personalizados
    header_message = Column(Text, nullable=True)  # Mensaje del encabezado
    footer_message = Column(Text, nullable=True)  # Mensaje del pie
    thank_you_message = Column(String(200), default="¡Gracias por su compra!")
    
    # Configuración de QR
    print_qr_code = Column(Boolean, default=True)  # Imprimir código QR
    qr_size = Column(Integer, default=4)  # Tamaño del QR (1-8)
    qr_position = Column(String(10), default="center")  # Posición (left, center, right)
    
    # Configuración avanzada
    encoding = Column(String(20), default="cp850")  # Codificación de caracteres
    cash_drawer_pin = Column(Integer, nullable=True)  # Pin para cajón
    open_cash_drawer = Column(Boolean, default=False)  # Abrir cajón automáticamente
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Impresora por defecto
    last_test_date = Column(DateTime(timezone=True), nullable=True)
    last_test_successful = Column(Boolean, default=False)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relaciones
    company = relationship("Company", back_populates="printer_configs")
    created_by = relationship("User", foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f"<PrinterConfig(name='{self.name}', type='{self.printer_type}')>"
    
    @property
    def connection_display(self) -> str:
        """Mostrar conexión de forma amigable"""
        if self.connection_type == PrinterConnection.USB:
            return f"USB: {self.connection_string}"
        elif self.connection_type == PrinterConnection.SERIAL:
            return f"Serie: {self.connection_string}"
        elif self.connection_type == PrinterConnection.NETWORK:
            return f"Red: {self.connection_string}"
        elif self.connection_type == PrinterConnection.BLUETOOTH:
            return f"Bluetooth: {self.connection_string}"
        return self.connection_string
    
    @property
    def paper_display(self) -> str:
        """Mostrar configuración de papel"""
        if self.paper_size == PaperSize.CUSTOM:
            return f"Personalizado: {self.paper_width_mm}mm"
        return f"{self.paper_size.value.upper()}"
    
    @property
    def is_thermal(self) -> bool:
        """Verificar si es impresora térmica"""
        return self.printer_type == PrinterType.THERMAL
    
    @property
    def status_display(self) -> str:
        """Estado de la impresora"""
        if not self.is_active:
            return "Inactiva"
        elif self.last_test_successful:
            return "Funcionando"
        elif self.last_test_date:
            return "Error en prueba"
        else:
            return "Sin probar"
    
    def get_esc_pos_config(self) -> dict:
        """Obtener configuración para ESC/POS"""
        return {
            "interface": self.connection_type.value,
            "port": self.connection_string,
            "profile": "TM-T88III" if self.is_thermal else "default",
            "encoding": self.encoding,
            "auto_cut": self.auto_cut,
            "cut_lines": self.cut_lines
        }
    
    def get_ticket_format(self) -> dict:
        """Obtener formato del ticket"""
        return {
            "width": self.paper_width_mm,
            "characters_per_line": self.characters_per_line,
            "print_header": self.print_header,
            "print_logo": self.print_logo,
            "logo_path": self.logo_path,
            "header_message": self.header_message,
            "footer_message": self.footer_message,
            "thank_you_message": self.thank_you_message,
            "print_qr": self.print_qr_code,
            "qr_size": self.qr_size,
            "qr_position": self.qr_position,
            "header_lines": self.header_lines,
            "footer_lines": self.footer_lines
        }
    
    def test_connection(self) -> bool:
        """Probar conexión con la impresora"""
        try:
            # Aquí iría la lógica para probar la conexión
            # Por ahora, simulamos una prueba exitosa
            self.last_test_date = func.now()
            self.last_test_successful = True
            return True
        except Exception:
            self.last_test_date = func.now()
            self.last_test_successful = False
            return False 
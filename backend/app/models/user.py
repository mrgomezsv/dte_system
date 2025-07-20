"""
Modelo de Usuario para autenticación y gestión de accesos
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    ACCOUNTANT = "accountant"
    CLIENT = "client"


class UserStatus(str, enum.Enum):
    """Estados del usuario"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """Modelo de Usuario"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Información adicional
    phone = Column(String(20), nullable=True)
    position = Column(String(50), nullable=True)
    employee_code = Column(String(20), nullable=True, unique=True)
    
    # Configuración de usuario
    role = Column(Enum(UserRole), default=UserRole.CASHIER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Configuración de acceso
    can_create_invoices = Column(Boolean, default=True)
    can_modify_invoices = Column(Boolean, default=False)
    can_delete_invoices = Column(Boolean, default=False)
    can_access_reports = Column(Boolean, default=True)
    can_manage_products = Column(Boolean, default=False)
    can_manage_customers = Column(Boolean, default=True)
    can_print_tickets = Column(Boolean, default=True)
    
    # Información de sesión
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadatos
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relaciones
    companies = relationship("Company", back_populates="users", secondary="company_users")
    invoices = relationship("Invoice", back_populates="created_by")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Verificar si el usuario es administrador"""
        return self.role == UserRole.ADMIN or self.is_superuser
    
    @property
    def can_access_admin_panel(self) -> bool:
        """Verificar si puede acceder al panel de administración"""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    @property
    def permissions(self) -> dict:
        """Obtener permisos del usuario en formato dict"""
        return {
            "create_invoices": self.can_create_invoices,
            "modify_invoices": self.can_modify_invoices,
            "delete_invoices": self.can_delete_invoices,
            "access_reports": self.can_access_reports,
            "manage_products": self.can_manage_products,
            "manage_customers": self.can_manage_customers,
            "print_tickets": self.can_print_tickets,
            "access_admin": self.can_access_admin_panel,
            "is_admin": self.is_admin
        } 
# 🧾 Sistema de Facturación Electrónica El Salvador

## 📋 Descripción

Microservicio completo para facturación electrónica en El Salvador que incluye:

- **🏢 Backend robusto** con FastAPI y PostgreSQL
- **📄 Templates fiscales** oficiales (CCF, Facturas de Exportación, etc.)
- **🏪 Punto de Venta (POS)** integrado con interfaz web
- **🖨️ Sistema de impresión** para tickets y comprobantes
- **🔌 Endpoints personalizados** por cliente
- **⚡ APIs dinámicas** para integración con sistemas externos

## 🚀 Características Principales

### Comprobantes Fiscales Soportados
- ✅ Crédito Fiscal (CCF)
- ✅ Factura de Exportación
- ✅ Nota de Crédito/Débito
- ✅ Comprobante de Retención
- ✅ Factura de Sujeto Excluido
- ✅ Documento Contable de Liquidación

### Punto de Venta
- 🛍️ Catálogo de productos con códigos de barras
- 💰 Múltiples formas de pago
- 📊 Gestión de inventario en tiempo real
- 👥 Control de usuarios y roles
- 🎯 Descuentos y promociones

### Sistema de Impresión
- 🖨️ Impresoras térmicas (58mm, 80mm)
- 📄 Impresoras láser/inkjet estándar
- 📧 Generación de PDFs para email
- 🔍 Códigos QR para verificación digital

## 🏗️ Arquitectura

```
facturacion-electronica/
├── backend/                 # Microservicio FastAPI
├── pos-frontend/           # Interfaz POS React
├── admin-panel/            # Panel de administración
├── printer-service/        # Servicio de impresión
├── docker-compose.yml      # Orquestación contenedores
└── docs/                   # Documentación técnica
```

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI + PostgreSQL + Redis
- **Frontend**: React.js + TypeScript
- **Base de Datos**: PostgreSQL con optimizaciones fiscales
- **Cache**: Redis para sesiones POS
- **Impresión**: ESC/POS + ReportLab
- **Contenedores**: Docker + Docker Compose

## 🚦 Estado del Proyecto

🔄 **En desarrollo inicial** - Configurando estructura base

## 👥 Contribuidores

- Desarrollador Principal: [Tu nombre]

## 📄 Licencia

Proyecto propietario - Todos los derechos reservados

---

*Desarrollado con ❤️ para la digitalización fiscal de El Salvador* 
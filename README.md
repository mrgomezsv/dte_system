# 🧾 Sistema de Facturación Electrónica El Salvador

## 📋 Descripción

Microservicio completo para facturación electrónica en El Salvador que incluye:

- **🏢 Backend robusto** con FastAPI y PostgreSQL
- **📄 Templates fiscales** oficiales (CCF, Facturas de Exportación, etc.)
- **🏪 Punto de Venta (POS)** integrado con interfaz web React
- **🖨️ Sistema de impresión** para tickets térmicos y comprobantes
- **🔌 Endpoints personalizados** por cliente con APIs dinámicas
- **⚡ Integración completa** con Ministerio de Hacienda El Salvador

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker y Docker Compose instalados
- Git instalado
- Puerto 3000, 5432, 6379, 8000 disponibles

### Instalación Automática

```bash
# Clonar el repositorio
git clone https://github.com/mrgomezsv/dte_system.git
cd dte_system

# Ejecutar script de instalación
chmod +x scripts/start.sh
./scripts/start.sh
```

### Instalación Manual

```bash
# 1. Crear archivo de configuración
cp .env.example .env

# 2. Levantar servicios
docker-compose up -d

# 3. Verificar instalación
curl http://localhost:8000/health
```

## 🌐 URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend POS** | http://localhost:3000 | Punto de venta principal |
| **Panel Admin** | http://localhost:3001 | Administración del sistema |
| **API Backend** | http://localhost:8000 | API REST principal |
| **Documentación** | http://localhost:8000/docs | Swagger/OpenAPI |
| **Monitor Celery** | http://localhost:5555 | Monitoreo de tareas |
| **Servicio Impresión** | http://localhost:8001 | API de impresión |

## 🏗️ Arquitectura del Sistema

```
Sistema de Facturación Electrónica/
├── backend/                    # FastAPI + PostgreSQL + Redis
│   ├── app/
│   │   ├── api/               # Endpoints REST
│   │   ├── core/              # Configuración central
│   │   ├── models/            # Modelos SQLAlchemy
│   │   └── services/          # Lógica de negocio
│   ├── templates/             # Templates fiscales XML/HTML
│   └── requirements.txt       # Dependencias Python
├── pos-frontend/              # React + TypeScript
├── admin-panel/               # Panel administración React
├── printer-service/           # Servicio impresión especializado
├── nginx/                     # Reverse proxy
├── docker-compose.yml         # Orquestación completa
└── scripts/                   # Scripts de utilidad
```

## 💡 Características Principales

### 📄 Comprobantes Fiscales Soportados

✅ **Crédito Fiscal (CCF)** - Para contribuyentes IVA  
✅ **Factura de Exportación** - Ventas al exterior  
✅ **Nota de Crédito/Débito** - Ajustes contables  
✅ **Comprobante de Retención** - Retenciones fiscales  
✅ **Factura de Sujeto Excluido** - No contribuyentes  
✅ **Documento Contable de Liquidación** - Liquidaciones  

### 🏪 Punto de Venta Completo

- 🛍️ **Catálogo de productos** con códigos de barras
- 💰 **Múltiples formas de pago** (efectivo, tarjetas, transferencias)
- 📊 **Gestión de inventario** en tiempo real
- 👥 **Control de usuarios** y roles
- 🎯 **Descuentos y promociones** configurables
- 📱 **Interfaz responsive** para tablets y móviles

### 🖨️ Sistema de Impresión Avanzado

- 🖨️ **Impresoras térmicas** (58mm, 80mm)
- 📄 **Impresoras láser/inkjet** estándar
- 📧 **Generación de PDFs** para email
- 🔍 **Códigos QR** para verificación digital
- ⚙️ **Configuración flexible** por empresa

### 🔌 Endpoints Personalizados

- 🎛️ **APIs dinámicas** por cliente
- 🔑 **Autenticación personalizada** (API Key, JWT, etc.)
- 📋 **Esquemas configurables** de request/response
- 📈 **Rate limiting** y monitoreo
- 🔄 **Versionado** de endpoints

## 🛠️ Stack Tecnológico Completo

### Backend
- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL** - Base de datos robusta con optimizaciones fiscales
- **Redis** - Cache y gestión de sesiones POS
- **SQLAlchemy** - ORM avanzado para Python
- **Celery** - Tareas asíncronas (envío a Hacienda)
- **Alembic** - Migraciones de base de datos

### Frontend
- **React.js** - Interfaz de usuario moderna
- **TypeScript** - Tipado estático
- **Material-UI** - Componentes UI profesionales
- **React Query** - Gestión de estado del servidor
- **Socket.IO** - Comunicación en tiempo real

### Infraestructura
- **Docker & Docker Compose** - Containerización
- **Nginx** - Reverse proxy y balanceador
- **Flower** - Monitoreo de Celery
- **PostgreSQL** - Optimizado para facturación

### Impresión & Documentos
- **ESC/POS** - Protocolo impresoras térmicas
- **ReportLab** - Generación de PDFs
- **lxml** - Procesamiento XML fiscal
- **QRCode** - Códigos QR de verificación

## 📊 Modelos de Base de Datos

### Entidades Principales

| Modelo | Descripción | Campos Clave |
|--------|-------------|-------------|
| **Company** | Empresas emisoras | NIT, NRC, certificados |
| **Customer** | Clientes/receptores | DUI, NIT, tipo contributivo |
| **Product** | Catálogo productos | SKU, precio, inventario |
| **Invoice** | Facturas emitidas | Número, totales, estado |
| **FiscalDocument** | Documentos MH | UUID, XML, validación |
| **PrinterConfig** | Configuración impresoras | Tipo, puerto, formato |
| **ClientEndpoint** | APIs personalizadas | Path, auth, lógica |

### Optimizaciones de Rendimiento

```sql
-- Índices optimizados para consultas fiscales
CREATE INDEX idx_invoice_date ON invoices(created_at);
CREATE INDEX idx_invoice_fiscal_number ON invoices(fiscal_number);
CREATE INDEX idx_fiscal_doc_type ON fiscal_documents(document_type);
CREATE INDEX idx_customer_nit ON customers(nit);
```

## 🔧 APIs Principales

### Autenticación
```http
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### Facturación
```http
GET  /api/v1/invoices
POST /api/v1/invoices
GET  /api/v1/invoices/{id}
PUT  /api/v1/invoices/{id}
```

### Punto de Venta
```http
GET  /api/v1/pos/products
POST /api/v1/pos/sale
GET  /api/v1/pos/session
```

### Impresión
```http
POST /api/v1/printing/ticket
POST /api/v1/printing/fiscal-document
GET  /api/v1/printing/printers
```

### Endpoints Dinámicos
```http
GET  /api/v1/client/{client_code}/invoices
POST /api/v1/client/{client_code}/invoices
GET  /api/v1/client/{client_code}/products
```

## 🔒 Seguridad y Compliance

### Seguridad Implementada
- 🔐 **Autenticación JWT** con refresh tokens
- 🛡️ **Autorización basada en roles** (RBAC)
- 🔑 **API Keys** para clientes externos
- 🚦 **Rate limiting** por endpoint
- 🔒 **Cifrado de datos** sensibles
- 📝 **Auditoría completa** de operaciones

### Compliance Fiscal El Salvador
- ✅ **Certificados digitales** para firmado
- ✅ **XML fiscal** según estándares MH
- ✅ **Numeración controlada** de documentos
- ✅ **Códigos de control** algorítmicos
- ✅ **Transmisión segura** al MH
- ✅ **Contingencia** ante fallas

## 📈 Monitoreo y Logs

### Métricas Disponibles
- 📊 **Rendimiento de APIs** (tiempo respuesta, errores)
- 💰 **Volumen de facturación** por período
- 🖨️ **Estado de impresoras** y fallos
- 🔌 **Uso de endpoints** personalizados
- 📈 **Tendencias de ventas** en tiempo real

### Logs Estructurados
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "service": "billing",
  "user_id": 123,
  "action": "create_invoice",
  "invoice_id": "CCF-00000001",
  "amount": 115.00,
  "duration_ms": 245
}
```

## 🚀 Despliegue en Producción

### Variables de Entorno Críticas
```bash
# Seguridad
SECRET_KEY=your-super-secure-production-key
ENVIRONMENT=production

# Base de datos
POSTGRES_PASSWORD=secure-db-password

# Certificados MH
CERTIFICATE_PATH=/secure/certificates/
CERTIFICATE_PASSWORD=cert-password

# Hacienda
HACIENDA_ENVIRONMENT=production
HACIENDA_BASE_URL=https://api.dtes.mh.gob.sv/fesv/recepciondte
```

### Checklist Pre-Producción
- [ ] Certificados digitales instalados
- [ ] Conexión a Hacienda funcionando
- [ ] Backup automático configurado
- [ ] Monitoring y alertas activos
- [ ] SSL/TLS configurado
- [ ] Firewall y seguridad de red
- [ ] Usuarios y roles configurados
- [ ] Impresoras probadas y funcionando

## 🆘 Comandos Útiles

### Docker
```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Reiniciar servicios
docker-compose restart

# Acceder al contenedor
docker-compose exec backend bash

# Limpiar todo y empezar fresh
docker-compose down -v --remove-orphans
```

### Base de Datos
```bash
# Backup manual
docker-compose exec postgres pg_dump -U postgres facturacion_db > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres facturacion_db < backup.sql

# Acceder a PostgreSQL
docker-compose exec postgres psql -U postgres -d facturacion_db
```

### Debugging
```bash
# Estado de servicios
docker-compose ps

# Uso de recursos
docker stats

# Logs específicos
docker-compose logs backend | grep ERROR
```

## 📚 Documentación Adicional

- 📖 **API Docs**: http://localhost:8000/docs
- 🔧 **Admin Guide**: `docs/admin-guide.md`
- 👨‍💻 **Developer Guide**: `docs/developer-guide.md`
- 🏪 **POS Manual**: `docs/pos-manual.md`
- 🖨️ **Printer Setup**: `docs/printer-setup.md`

## 🤝 Contribución

### Proceso de Desarrollo
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- **Python**: PEP 8, type hints obligatorios
- **TypeScript**: ESLint + Prettier
- **Commits**: Conventional Commits
- **Tests**: Cobertura mínima 80%

## 📄 Licencia

Este proyecto es software propietario. Todos los derechos reservados.

## 📞 Soporte

- 📧 **Email**: soporte@facturacion-sv.com
- 💬 **Chat**: https://t.me/facturacion_sv
- 🐛 **Issues**: GitHub Issues
- 📖 **Wiki**: https://wiki.facturacion-sv.com

---

<div align="center">

**🧾 Sistema de Facturación Electrónica El Salvador**

*Desarrollado con ❤️ para la digitalización fiscal de El Salvador*

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)](https://redis.io/)

</div> 
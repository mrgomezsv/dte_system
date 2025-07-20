#!/bin/bash

# Script de inicio para Sistema de Facturación Electrónica El Salvador
# Autor: Sistema de Facturación Electrónica
# Fecha: 2024

set -e

echo "🧾 Iniciando Sistema de Facturación Electrónica El Salvador..."
echo "=================================================="

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker y Docker Compose."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose."
    exit 1
fi

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p uploads templates certificates logs backups
mkdir -p nginx/ssl
mkdir -p init-scripts

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "⚙️ Creando archivo .env desde ejemplo..."
    cat > .env << 'EOF'
# Configuración de Base de Datos PostgreSQL
POSTGRES_SERVER=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password123
POSTGRES_DB=facturacion_db
POSTGRES_PORT=5432

# Configuración de Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Configuración de la Aplicación
SECRET_KEY=facturacion-super-secret-key-2024
ENVIRONMENT=development
DEBUG=true

# Configuración de Facturación Electrónica El Salvador
HACIENDA_ENVIRONMENT=test
HACIENDA_BASE_URL=https://apitest.dtes.mh.gob.sv/fesv/recepciondte

# Configuración de Impresión
PRINTER_ENABLED=true
TICKET_WIDTH=80

# Configuración de la Aplicación
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
EOF
    echo "✅ Archivo .env creado con configuración por defecto"
fi

# Verificar que los puertos estén disponibles
echo "🔍 Verificando puertos disponibles..."
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Puerto $port está ocupado ($service). Por favor cierra el servicio que lo está usando."
        return 1
    fi
}

check_port 5432 "PostgreSQL" || exit 1
check_port 6379 "Redis" || exit 1
check_port 8000 "Backend API" || exit 1
check_port 3000 "Frontend POS" || exit 1

# Construir y levantar contenedores
echo "🏗️ Construyendo contenedores..."
docker-compose build

echo "🚀 Iniciando servicios..."
docker-compose up -d postgres redis

echo "⏳ Esperando que la base de datos esté lista..."
sleep 10

# Verificar que PostgreSQL esté funcionando
echo "🔍 Verificando conexión a PostgreSQL..."
docker-compose exec postgres pg_isready -U postgres

echo "🚀 Iniciando servicios completos..."
docker-compose up -d

echo "⏳ Esperando que todos los servicios estén listos..."
sleep 15

# Verificar estado de los servicios
echo "📊 Estado de los servicios:"
echo "========================="
docker-compose ps

# Mostrar URLs de acceso
echo ""
echo "🎉 ¡Sistema iniciado correctamente!"
echo "=================================="
echo ""
echo "📱 Frontend POS:           http://localhost:3000"
echo "⚙️  Panel Administración:   http://localhost:3001"
echo "🔧 API Backend:            http://localhost:8000"
echo "📚 Documentación API:      http://localhost:8000/docs"
echo "🌺 Monitor Celery:         http://localhost:5555"
echo "🖨️ Servicio Impresión:     http://localhost:8001"
echo ""
echo "🗄️ Base de datos PostgreSQL: localhost:5432"
echo "🔴 Redis:                   localhost:6379"
echo ""
echo "📋 Comandos útiles:"
echo "==================="
echo "Ver logs:           docker-compose logs -f"
echo "Parar servicios:    docker-compose down"
echo "Reiniciar:          docker-compose restart"
echo "Limpiar todo:       docker-compose down -v --remove-orphans"
echo ""

# Crear usuario administrador por defecto
echo "👤 Configurando usuario administrador por defecto..."
echo "Usuario: admin@facturacion.sv"
echo "Contraseña: admin123"
echo ""

# Verificar que la API esté respondiendo
echo "🔍 Verificando API..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API funcionando correctamente"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "⚠️  La API tardó en responder. Verifica los logs: docker-compose logs backend"
    else
        echo "⏳ Esperando API... ($i/30)"
        sleep 2
    fi
done

echo ""
echo "🎯 ¡Todo listo! Puedes comenzar a usar el sistema."
echo "📖 Para más información, consulta el README.md" 
# ===================================
# CONFIGURANDO ENTORNO VIRTUAL PYTHON
# ===================================

Write-Host "Configurando entorno virtual para Facturación Electrónica El Salvador" -ForegroundColor Green

# Cambiar al directorio del proyecto
Set-Location "C:\Users\Admin\Desktop\DTE"

# 1. Terminar procesos Python existentes
Write-Host "1. Terminando procesos Python existentes..." -ForegroundColor Yellow
try {
    Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Procesos terminados" -ForegroundColor Green
} catch {
    Write-Host "   ✓ No hay procesos Python activos" -ForegroundColor Green
}

# 2. Eliminar entorno virtual anterior si existe
if (Test-Path "venv") {
    Write-Host "2. Eliminando entorno virtual anterior..." -ForegroundColor Yellow
    Remove-Item -Path "venv" -Recurse -Force
    Write-Host "   ✓ Entorno anterior eliminado" -ForegroundColor Green
}

# 3. Crear nuevo entorno virtual
Write-Host "3. Creando entorno virtual..." -ForegroundColor Yellow
py -m venv venv
Write-Host "   ✓ Entorno virtual creado" -ForegroundColor Green

# 4. Activar entorno virtual
Write-Host "4. Activando entorno virtual..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "   ✓ Entorno virtual activado" -ForegroundColor Green

# 5. Actualizar pip
Write-Host "5. Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "   ✓ Pip actualizado" -ForegroundColor Green

# 6. Instalar dependencias
Write-Host "6. Instalando dependencias del backend..." -ForegroundColor Yellow
Set-Location "backend"
pip install -r requirements.txt
Write-Host "   ✓ Dependencias instaladas" -ForegroundColor Green

# 7. Verificar instalación
Write-Host "7. Verificando instalación..." -ForegroundColor Yellow
python -c "import fastapi; print('FastAPI: ✓')"
python -c "import sqlalchemy; print('SQLAlchemy: ✓')"
python -c "import uvicorn; print('Uvicorn: ✓')"
Write-Host "   ✓ Verificación completada" -ForegroundColor Green

# Regresar al directorio raíz
Set-Location ".."

Write-Host ""
Write-Host "====================================" -ForegroundColor Green
Write-Host "ENTORNO VIRTUAL CONFIGURADO ✓" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Para usar el proyecto:" -ForegroundColor Cyan
Write-Host "1. Activar entorno: venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Ir al backend: cd backend" -ForegroundColor White
Write-Host "3. Ejecutar servidor: uvicorn main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "El entorno virtual está listo para usar! 🎉" -ForegroundColor Green 
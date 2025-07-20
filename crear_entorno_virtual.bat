@echo off
echo ===================================
echo CONFIGURANDO ENTORNO VIRTUAL PYTHON
echo ===================================

cd /d C:\Users\Admin\Desktop\DTE

echo 1. Terminando procesos Python existentes...
taskkill /f /im python.exe >nul 2>&1

echo 2. Creando entorno virtual...
py -m venv venv

echo 3. Activando entorno virtual...
call venv\Scripts\activate.bat

echo 4. Actualizando pip...
python -m pip install --upgrade pip

echo 5. Instalando dependencias...
cd backend
pip install -r requirements.txt

echo 6. Probando instalación...
python -c "import fastapi; print('FastAPI instalado correctamente')"

echo.
echo ===================================
echo ENTORNO VIRTUAL CONFIGURADO ✓
echo ===================================
echo.
echo Para activar el entorno virtual:
echo   venv\Scripts\activate
echo.
echo Para ejecutar el servidor:
echo   cd backend
echo   uvicorn main:app --reload
echo.
pause 
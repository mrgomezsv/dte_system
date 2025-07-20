# 🐍 CONFIGURACIÓN ENTORNO VIRTUAL PYTHON

## ✅ **SOLUCIÓN AL PROBLEMA**

Has identificado correctamente que el problema es que **no tenemos un entorno virtual**. Los errores de importación y ejecución se deben a conflictos entre paquetes globales de Python.

## 🚀 **CONFIGURACIÓN AUTOMÁTICA**

### **Opción 1: Script PowerShell (Recomendado)**
```powershell
# Abrir PowerShell como Administrador y ejecutar:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\configurar_entorno.ps1
```

### **Opción 2: Script Batch**
```cmd
# Hacer doble clic en:
crear_entorno_virtual.bat
```

## 🔧 **CONFIGURACIÓN MANUAL**

Si prefieres hacerlo paso a paso:

```powershell
# 1. Ir al directorio del proyecto
cd C:\Users\Admin\Desktop\DTE

# 2. Terminar procesos Python
taskkill /f /im python.exe

# 3. Crear entorno virtual
py -m venv venv

# 4. Activar entorno virtual
venv\Scripts\Activate.ps1

# 5. Actualizar pip
python -m pip install --upgrade pip

# 6. Instalar dependencias
cd backend
pip install -r requirements.txt

# 7. Probar servidor
uvicorn main:app --reload
```

## 📁 **ESTRUCTURA DESPUÉS DE LA CONFIGURACIÓN**

```
DTE/
├── venv/                    # ← Entorno virtual
│   ├── Scripts/
│   ├── Lib/
│   └── ...
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   └── ...
├── .env
├── configurar_entorno.ps1   # ← Script automático
└── crear_entorno_virtual.bat
```

## ✨ **COMANDOS ÚTILES**

### **Activar entorno virtual:**
```powershell
venv\Scripts\Activate.ps1
```

### **Desactivar entorno virtual:**
```powershell
deactivate
```

### **Ejecutar servidor:**
```powershell
# Con entorno activado:
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Verificar instalación:**
```powershell
python -c "import fastapi; print('FastAPI funciona!')"
```

## 🎯 **DESPUÉS DE LA CONFIGURACIÓN**

Una vez configurado el entorno virtual:

1. **Servidor FastAPI** funcionará en: `http://localhost:8000`
2. **Documentación API** en: `http://localhost:8000/docs`
3. **Health Check** en: `http://localhost:8000/health`

## ⚠️ **IMPORTANTE**

- **SIEMPRE** activar el entorno virtual antes de trabajar
- **NO** instalar paquetes en el Python global
- **Usar** `python` (no `py`) dentro del entorno virtual

¡Una vez configurado, el proyecto funcionará perfectamente! 🚀 
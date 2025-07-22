# 📄 Documentación de Faltantes para Pruebas DTE El Salvador

## 1. Faltantes del Usuario (Información y Archivos que debes proveer)

- **Certificado digital del emisor**
  - Archivos requeridos: `private.key` y `public.crt` (o `.pfx` si es un solo archivo)
  - Contraseña del certificado
  - Ubicación: carpeta `certificates/` en la raíz del proyecto

- **Credenciales de Hacienda (DTE)**
  - Usuario y contraseña del emisor para el ambiente de pruebas/homologación

- **Datos fiscales de la empresa emisora**
  - NIT, NRC, razón social, dirección, email, etc.
  - (Normalmente se configuran en la base de datos o en el panel admin)

- **Correo electrónico de contacto**
  - Para pruebas de envío de facturas por email (puede ser uno de prueba)

- **(Opcional) Ejemplo de XML de DTE**
  - Si tienes un XML de ejemplo de Hacienda, ayuda a validar la integración

- **Completar el archivo `.env`**
  - Agregar las rutas y contraseñas reales de los certificados y credenciales

---

## 2. Faltantes del Entorno/Configuración (lo que falta para estar 100% operativo)

- **Colocar los archivos de certificado en la carpeta `certificates/`**
- **Completar y verificar el archivo `.env` con los datos reales**
- **Reiniciar el backend después de agregar los archivos y datos**
  - Comando: `docker compose restart backend`
- **(Opcional) Crear la carpeta `printer-service/` si se requiere impresión física**
- **(Opcional) Configurar correctamente el correo SMTP si se va a probar envío de emails reales**

---

## 3. Estado Actual del Sistema

- Infraestructura principal (backend, base de datos, redis, POS, admin-panel) ya levantada con Docker Compose
- Carpetas necesarias y archivo `.env` de ejemplo creados
- Falta únicamente la información y archivos del usuario para pruebas DTE reales

---

## 4. Próximos Pasos

1. Proveer los archivos y datos listados en la sección 1
2. Colocarlos en las rutas indicadas y completar el `.env`
3. Reiniciar el backend
4. Probar los endpoints en `http://localhost:8000/docs`

---

**¿Dudas o necesitas ayuda con algún punto?**
- Puedes consultar la documentación oficial de DTE El Salvador o pedir soporte al equipo técnico. 
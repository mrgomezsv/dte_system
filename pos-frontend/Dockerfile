# Dockerfile para Frontend POS React
FROM node:18-alpine

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Establecer variables de entorno por defecto
ENV REACT_APP_API_URL=http://localhost:8000/api/v1
ENV REACT_APP_WS_URL=ws://localhost:8000/ws
ENV GENERATE_SOURCEMAP=false

# Exponer puerto
EXPOSE 3000

# Comando de inicio
CMD ["npm", "start"] 
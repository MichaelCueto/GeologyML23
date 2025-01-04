# Usar una imagen base de Python
FROM python:3.9-slim

# Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios al contenedor
COPY . .

# Instalar dependencias
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Crear carpeta para los uploads (volumen)
RUN mkdir -p /app/process/uploads

# Exponer el puerto para la aplicación
EXPOSE 8081

# Comando para ejecutar la aplicación
CMD ["python", "process/app.py"]
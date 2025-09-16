# Utiliza una imagen base oficial de Python con parches de seguridad actualizados
FROM python:3.11-slim

# Establece el directorio de trabajo en la imagen
WORKDIR /app

# Copia el archivo de requerimientos al contenedor
COPY requirements_ibm.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements_ibm.txt

# Copia el código completo de la aplicación al contenedor
COPY . .

# Expone el puerto 8080 para la aplicación
EXPOSE 8080

# Comando para iniciar la aplicación con Gunicorn
CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
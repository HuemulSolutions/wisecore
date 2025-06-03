# Utiliza una imagen base oficial de Python con parches de seguridad actualizados
FROM python:3.11-slim

# Establece el directorio de trabajo en la imagen
WORKDIR /app

# Copia el archivo de requerimientos al contenedor
COPY requirements.txt .

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código completo de la aplicación al contenedor
COPY . .

# Expone el puerto 80 para la aplicación
EXPOSE 8080

# Comando para iniciar la aplicación FastAPI con Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
# Use an official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend and data directories
COPY backend /app/backend
COPY data /app/data

# Expose the port on which ChromaDB will run
EXPOSE 8000

# Run the main application
CMD ["python", "-m", "backend.main"]

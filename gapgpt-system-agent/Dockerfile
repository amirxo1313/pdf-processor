FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
  curl \
  docker-compose \
  docker.io \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/

# Set working directory to backend for imports
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



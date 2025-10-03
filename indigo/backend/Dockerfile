# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    tesseract-ocr \
    libtesseract-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install poetry
RUN pip install poetry

# Configure poetry to not create virtual environment (since we're in a container)
RUN poetry config virtualenvs.create false

# Install only dependencies first (no project) for better caching
RUN poetry install --only=main --no-root

# Copy application code (after deps for better caching)
COPY app/ ./app

# Now install just the project so entry points are registered
RUN poetry install --only-root

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5174

# Run the application
CMD ["poetry", "run", "app"]

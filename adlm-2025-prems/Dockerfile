FROM python:3.12-slim

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18.x
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy React app files and install dependencies
COPY chat_web/package*.json ./chat_web/
WORKDIR /app/chat_web
RUN npm ci

# Switch back to Django app directory
WORKDIR /app/chat_api_dj

# Copy dependency files
COPY chat_api_dj/pyproject.toml chat_api_dj/uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY chat_api_dj .

# Copy React source code
COPY chat_web/src ./chat_web/src
COPY chat_web/public ./chat_web/public

RUN pwd
RUN ls -la

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -m appuser
RUN chown -R appuser:appuser /app
RUN mkdir -p /home/appuser
RUN chown -R appuser:appuser /home/appuser
USER appuser

# Copy startup script
COPY start.sh /app/start.sh

# Expose both ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Set production settings
ENV DJANGO_SETTINGS_MODULE=chat_web_dj.settings_production

# Start both Django and React services
CMD ["/app/start.sh"]
# syntax=docker/dockerfile:1

# Build Stage
FROM python:3.11-slim AS build

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install system dependencies including Rust for building fastbm25
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (needed for maturin/fastbm25)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies including build dependencies for fastbm25
# Use --all-packages to install dev dependencies including maturin needed to build fastbm25
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-packages --no-install-project

# Copy pyproject.toml only for installing the project (we'll copy app code in runtime stage)
COPY pyproject.toml ./

# Install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Runtime Stage
FROM python:3.11-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the build stage
COPY --from=build /app/.venv /app/.venv

# Copy the application code
COPY app/ ./app

# Expose port
EXPOSE 5174

# Run the application using the installed console script
CMD ["/app/.venv/bin/app"]

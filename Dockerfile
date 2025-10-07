# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the code
COPY . /app/

# Expose Streamlit port
EXPOSE 8501

# Set Streamlit to listen on all interfaces
ENV STREAMLIT_SERVER_HEADLESS true
ENV STREAMLIT_SERVER_PORT 8501
ENV STREAMLIT_SERVER_ADDRESS 0.0.0.0

# Run the Streamlit app
CMD ["streamlit", "run", "chat_app.py"]

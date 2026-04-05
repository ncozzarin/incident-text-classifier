# Docker build script for production deployment
# This builds the backend API with multi-stage optimization

# Use Python 3.12 slim for smaller image
FROM python:3.12-slim as builder

# Set build-time arguments
ARG INSTALL_DEV=false

# Set working directory
WORKDIR /app

# Install system dependencies for compiling Python packages
# and for spaCy/Presidio which have native extensions
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage - lightweight production image
FROM python:3.12-slim as production

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user for security
RUN groupadd -r security && useradd -r -g security security

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/security/.local

# Copy application code
COPY --chown=security:security . .

# Switch to non-root user
USER security

# Create upload directory for temporary files
RUN mkdir -p /app/uploads && chmod 755 /app/uploads

# Expose port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage for local development
FROM builder as development

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=builder /root/.local /root/.local

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
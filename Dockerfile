# Eleven-Layer AI System Dockerfile
# Security-hardened production image

FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r aiuce && useradd -r -g aiuce aiuce

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY --chown=aiuce:aiuce . /app/

# Install project
RUN pip install --no-cache-dir -e .

# Create data directories with proper permissions
RUN mkdir -p /app/data/memory /app/data/audit /app/data/evolution /app/logs \
    && chown -R aiuce:aiuce /app/data /app/logs

# Switch to non-root user
USER aiuce

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python3", "-c", "from eleven_layer_ai import create_system; s = create_system(); print(s.chat('系统启动完成'))"]

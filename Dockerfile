# Use official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Install Node.js 18 (via NodeSource)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Setup Python environment with uv
RUN uv sync

# Create directories for logs and state files
RUN mkdir -p /var/log /etc/proxmox-monitor

# Copy config
RUN cp config/config.empty.yaml /etc/proxmox-monitor/config.yaml

# Copy entrypoint and token update scripts
COPY scripts/entrypoint.sh /app/entrypoint.sh
COPY scripts/update_token.py /app/scripts/update_token.py

RUN chmod +x /app/entrypoint.sh && \
    chmod +x /app/scripts/update_token.py

# Health check - verify Python can import main modules
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from src import main; print('OK')" || exit 1

# Run the application with entrypoint
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

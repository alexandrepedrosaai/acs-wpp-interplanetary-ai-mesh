# Multi-stage Dockerfile for ACS-WPP Interplanetary AI Mesh
# Supports Python, Node.js, and .NET Core

# Stage 1: Base image with all runtimes
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS base

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies (if requirements.txt exists)
RUN if [ -f requirements.txt ]; then pip3 install --no-cache-dir -r requirements.txt; fi

# Install Node.js dependencies (if package.json exists)
RUN if [ -f package.json ]; then npm install; fi

# Build .NET application (if .csproj exists)
RUN if [ -f *.csproj ]; then dotnet build -c Release; fi

# Expose common ports
EXPOSE 80 443 8080 3000

# Default command - can be overridden
CMD ["python3", "Interplanetary.py"]

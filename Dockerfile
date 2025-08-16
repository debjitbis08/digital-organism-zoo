# Minimal base for widespread compatibility
FROM python:3.11-slim

# Install Ollama for local LLM
RUN apt-get update && apt-get install -y \
  curl \
  git \
  sqlite3 \
  && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Create non-root user for security
RUN useradd -m -s /bin/bash organism

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ecosystem
COPY . .

# Download small LLM model on build
RUN ollama pull llama3.2:1b  # Smallest model for efficiency

# Expose web interface
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

USER organism

# Start ecosystem
CMD ["python", "genesis/ecosystem.py"]

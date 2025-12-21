# Multi-stage Dockerfile for Offline AI Voice Assistant
FROM python:3.11-slim-bullseye

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    OLLAMA_HOST=0.0.0.0:11434 \
    HOME=/root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and install Piper TTS
RUN mkdir -p /app/piper && \
    cd /app/piper && \
    wget --tries=3 --timeout=30 https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz || \
    curl -L -o piper_linux_x86_64.tar.gz https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz && \
    tar -xzf piper_linux_x86_64.tar.gz && \
    rm piper_linux_x86_64.tar.gz && \
    chmod +x piper/piper

# Download default Piper voice model
RUN mkdir -p /app/piper/voices && \
    cd /app/piper/voices && \
    (wget --tries=3 --timeout=30 https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx || \
    curl -L -o en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx) && \
    (wget --tries=3 --timeout=30 https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json || \
    curl -L -o en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json)

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /root/.ollama

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Starting Ollama server..."\n\
ollama serve > /tmp/ollama.log 2>&1 &\n\
OLLAMA_PID=$!\n\
\n\
echo "Waiting for Ollama to start..."\n\
sleep 5\n\
\n\
# Pull the model if specified\n\
if [ ! -z "$OLLAMA_MODEL" ]; then\n\
    echo "Pulling model: $OLLAMA_MODEL"\n\
    ollama pull $OLLAMA_MODEL || true\n\
fi\n\
\n\
echo "Starting Voice Assistant..."\n\
python voice_assistant.py\n\
\n\
# Cleanup\n\
kill $OLLAMA_PID 2>/dev/null || true\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose Ollama port
EXPOSE 11434

# Set the entrypoint
ENTRYPOINT ["/app/start.sh"]

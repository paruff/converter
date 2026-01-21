# Media Converter Docker Image
FROM python:3.11-slim

# Install system dependencies (ffmpeg, ffprobe)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY converter/ /app/converter/
COPY pyproject.toml /app/
COPY README.md /app/
COPY LICENSE /app/

# Install Python package
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp_fix /app/originals /media

# Set media directory as volume mount point
VOLUME ["/media"]

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command - show help
ENTRYPOINT ["python", "-m", "converter"]
CMD ["--help"]

# Production-ready Dockerfile for Django File Converter
# Python 3.11 slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
# - build-essential/pkg-config/libcairo2-dev: для сборки pycairo/rlpycairo (зависиимость xhtml2pdf)
# - Pillow: libjpeg-dev, zlib1g-dev, libfreetype6-dev, liblcms2-dev, libtiff5-dev, libwebp-dev
# - PDF processing: poppler-utils (для pdf2docx)
# - FFmpeg: для аудио/видео конвертации
# - OpenCV: libgl1, libglib2.0-0 (для opencv-python-headless, если понадобится)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools for native extensions (pycairo, etc.)
    build-essential \
    pkg-config \
    libcairo2-dev \
    # Pillow dependencies
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libtiff5-dev \
    libwebp-dev \
    # PDF processing
    poppler-utils \
    # FFmpeg для аудио/видео
    ffmpeg \
    # OpenCV dependencies (на будущее)
    libgl1 \
    libglib2.0-0 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (для кеширования слоя)
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create directories for media and static files
RUN mkdir -p /app/media/convert_temp /app/staticfiles

# Set Django settings module for collectstatic
ENV DJANGO_SETTINGS_MODULE=config.settings

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Use entrypoint script (выполняет миграции и запускает gunicorn)
ENTRYPOINT ["/app/entrypoint.sh"]

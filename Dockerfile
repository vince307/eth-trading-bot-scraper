# Dockerfile for scheduled scraper service
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set Playwright browser path BEFORE installing
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright system dependencies manually (without --with-deps)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxshmfence1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright Chromium browser (will use PLAYWRIGHT_BROWSERS_PATH)
RUN playwright install chromium

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["python", "scraper_cron.py"]

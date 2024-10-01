FROM python:3.9-slim

# Set environment variables
ENV CHROMEDRIVER_PATH /usr/bin/chromedriver
ENV GOOGLE_CHROME_BIN /usr/bin/google-chrome

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    ca-certificates \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libappindicator1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libgbm-dev \
    google-chrome-stable=113.0.5672.63-1 \
    chromium-driver=113.0.5672.63-1

# Copy project files
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Gunicorn logging and timeout settings
CMD ["gunicorn", "--log-level=debug", "--timeout", "120", "app:app", "--bind", "0.0.0.0:5000"]

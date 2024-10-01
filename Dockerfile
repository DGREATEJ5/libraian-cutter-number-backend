# Use a base image
FROM python:3.9-slim

# Set environment variables for Chrome and Chromedriver
ENV CHROMEDRIVER_PATH /usr/bin/chromedriver
ENV GOOGLE_CHROME_BIN /usr/bin/google-chrome

# Install dependencies, including Google Chrome and Chromedriver
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
    google-chrome-stable \
    chromium-driver

# Add logging to verify Chrome and Chromedriver installation paths
RUN echo "Installed Google Chrome at: $(which google-chrome)"
RUN echo "Installed Chromedriver at: $(which chromedriver)"

# Copy project files
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 5000

# Run the Gunicorn server with debug-level logging and a longer timeout
CMD ["gunicorn", "--log-level=debug", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]

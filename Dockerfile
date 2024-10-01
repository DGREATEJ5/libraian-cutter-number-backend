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
    && rm -f /etc/apt/sources.list.d/google-chrome.list \
    && rm -f /etc/apt/sources.list.d/google.list \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get install -y chromium-driver

# Debugging: Check Google Chrome and Chromedriver installation
RUN echo "Installed Google Chrome at: $(which google-chrome)"
RUN echo "Installed Chromedriver at: $(which chromedriver)"

# Copy project files
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]

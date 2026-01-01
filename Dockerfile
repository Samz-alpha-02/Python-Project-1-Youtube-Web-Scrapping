FROM python:3.9

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y wget gnupg2 ca-certificates libnss3-dev curl
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver using webdriver-manager (more reliable)
RUN apt-get install -yqq unzip
# Note: ChromeDriver will be managed by webdriver-manager in the Python code

# Set the working directory
WORKDIR /app

# Copy only the requirements file first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the necessary port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Run the application with Flask's development server
CMD ["python", "app.py"]

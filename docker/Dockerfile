# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first (best practice for Docker caching)
COPY ../docker/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory into the container
COPY ../app /app

# Set environment variables
ENV OVERWRITE_MODE=True
ENV RESTART_MODE=True

# Run the script
CMD ["python", "/app/fetch_binance_data.py"]

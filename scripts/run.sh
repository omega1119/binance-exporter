#!/bin/bash

# Set variables
IMAGE_NAME="binance_fetcher"
CONTAINER_NAME="binance_data_fetcher"

echo "🚀 Starting Binance Data Fetcher setup..."

# Step 1: Build the Docker image from the project root
echo "🔧 Building Docker image..."
docker build -t $IMAGE_NAME -f docker/Dockerfile .

# Step 2: Stop and remove any existing container
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Stopping existing container..."
    docker stop $CONTAINER_NAME
    echo "🗑 Removing old container..."
    docker rm $CONTAINER_NAME
fi

# Step 3: Run the container with correct volume mappings
echo "🚀 Running new container..."
docker run --name $CONTAINER_NAME \
    -v $(pwd)/app/data:/app/data \
    -v $(pwd)/app/logs:/app/logs \
    -v $(pwd)/app/last_run.txt:/app/last_run.txt \
    -v $(pwd)/app/config/myconfig.py:/app/config/myconfig.py \
    $IMAGE_NAME

echo "✅ Binance Data Fetcher is running!"
echo "📊 Check logs using: docker logs -f $CONTAINER_NAME"

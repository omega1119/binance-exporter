#!/bin/bash

# Set variables
CONTAINER_NAME="binance_data_fetcher"

# Check for arguments
if [ "$1" == "stop" ]; then
    echo "🛑 Stopping container..."
    docker stop $CONTAINER_NAME
elif [ "$1" == "start" ]; then
    echo "🚀 Restarting container..."
    docker restart $CONTAINER_NAME
elif [ "$1" == "logs" ]; then
    echo "📊 Showing logs..."
    docker logs -f $CONTAINER_NAME
elif [ "$1" == "remove" ]; then
    echo "🗑 Removing container..."
    docker rm -f $CONTAINER_NAME
else
    echo "❌ Invalid command! Use one of the following:"
    echo "  ./manage.sh stop    → Stop container"
    echo "  ./manage.sh start   → Restart container"
    echo "  ./manage.sh logs    → View logs"
    echo "  ./manage.sh remove  → Remove container"
fi

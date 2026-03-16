#!/bin/bash

# Portfolio Optimization AI - Docker Deployment Script

set -e

echo "🚀 Starting Portfolio Optimization AI deployment..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t portfolio-ai .

# Run Docker container
echo "🏃 Running Docker container..."
docker run -d \
    --name portfolio-ai-container \
    -p 8000:8000 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/cache:/app/cache \
    -v $(pwd)/logs:/app/logs \
    --restart unless-stopped \
    portfolio-ai

echo "✅ Deployment completed!"
echo "🌐 API is available at: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "📋 Health Check: http://localhost:8000/health"

# Wait for container to start
echo "⏳ Waiting for service to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Service is healthy!"
else
    echo "❌ Service health check failed"
    echo "📋 Container logs:"
    docker logs portfolio-ai-container
    exit 1
fi

echo "🎉 Portfolio Optimization AI is ready to use!"
echo ""
echo "📖 Usage examples:"
echo "  curl -X POST http://localhost:8000/optimize/sync \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"tickers\": [\"AAPL\", \"MSFT\", \"GOOG\", \"AMZN\"]}'"
echo ""
echo "📊 To run the dashboard:"
echo "  streamlit run dashboard/app.py --server.port 8501"

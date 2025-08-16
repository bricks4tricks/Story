#!/bin/bash

# LogicAndStories Deployment Script
# This script handles the deployment of the LogicAndStories application

set -e  # Exit on any error

echo "🚀 Starting LogicAndStories Deployment"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create a .env file with required environment variables."
    echo "See .env.example for reference."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Validate environment variables
echo "🔍 Validating environment configuration..."
python env_validator.py
if [ $? -ne 0 ]; then
    echo "❌ Environment validation failed. Please check your .env file."
    exit 1
fi

echo "✅ Environment validation passed"

# Run security tests
echo "🔒 Running security tests..."
python test_admin_security.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Admin security tests failed."
    exit 1
fi

python test_admin_py_security.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Admin.py security tests failed."
    exit 1
fi

echo "✅ Security tests passed"

# Build CSS assets
echo "📦 Building CSS assets..."
if [ -f package.json ]; then
    npm install
    npm run build:css
    echo "✅ CSS assets built"
else
    echo "⚠️  No package.json found, skipping CSS build"
fi

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t logicandstories:latest .
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed."
    exit 1
fi

echo "✅ Docker image built successfully"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Start new deployment
echo "🚀 Starting new deployment..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health check
echo "🏥 Performing health check..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
if [ "$health_response" == "200" ]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed (HTTP $health_response)"
    echo "📋 Container logs:"
    docker-compose logs --tail=50 web
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "🌐 Application is running at: http://localhost:5000"
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop with: docker-compose down"
echo ""
echo "🔧 Post-deployment checklist:"
echo "  - [ ] Verify application is accessible"
echo "  - [ ] Check database connectivity"
echo "  - [ ] Test user authentication"
echo "  - [ ] Verify email functionality"
echo "  - [ ] Run full test suite in production environment"
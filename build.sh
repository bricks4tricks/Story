#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Install Node.js dependencies for CSS processing
echo "📦 Installing Node.js dependencies..."
npm install

# Build CSS with Tailwind
echo "🎨 Building CSS with Tailwind..."
npm run build:css

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build completed successfully!"
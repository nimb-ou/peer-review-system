#!/bin/bash
# PeerPulse Enterprise - Production Deployment Script

echo "🚀 PeerPulse Enterprise Deployment"
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "production_app/frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing frontend dependencies..."
cd production_app/frontend
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "🏗️  Building production frontend..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend built successfully"
else
    echo "❌ Frontend build failed"
    exit 1
fi

echo "🎉 Deployment Complete!"
echo ""
echo "🌐 Your application is ready for deployment:"
echo "   - Frontend build: production_app/frontend/build/"
echo "   - Backend API: production_app/backend/"
echo ""
echo "☁️  Cloud Deployment Options:"
echo "   1. Netlify: Drag & drop the 'build' folder"
echo "   2. Vercel: Connect your GitHub repository"
echo "   3. AWS S3: Upload build files to S3 bucket"
echo "   4. Railway: Deploy backend + frontend together"
echo ""
echo "🚀 To run locally:"
echo "   Frontend: cd production_app/frontend && npm start"
echo "   Backend:  cd production_app/backend && python main.py"

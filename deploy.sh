#!/bin/bash

# XTHLETE Tournament Management System - Deployment Script

echo "🚀 Deploying XTHLETE Tournament Management System..."

# Frontend Deployment (Vercel)
echo "📦 Deploying Frontend to Vercel..."
cd /home/z/my-project

# Install dependencies
npm install

# Build frontend
npm run build

# Deploy to Vercel (requires vercel CLI)
if command -v vercel &> /dev/null; then
    vercel --prod
    echo "✅ Frontend deployed to Vercel"
else
    echo "⚠️  Vercel CLI not found. Please install it: npm i -g vercel"
fi

# Python Backend Deployment (Render/Heroku)
echo "🐍 Deploying Python Backend..."

cd /home/z/my-project/python-backend

# Create requirements.txt for production
pip freeze > requirements-freeze.txt

# Docker deployment
echo "🐳 Building Docker image..."
docker build -t xthlete-tournament-api .

# Tag and push to registry (configure as needed)
# docker tag xthlete-tournament-api your-registry/xthlete-tournament-api:latest
# docker push your-registry/xthlete-tournament-api:latest

echo "📊 Deployment Summary:"
echo "Frontend: https://your-app.vercel.app"
echo "Backend: https://your-api.onrender.com"
echo "API Documentation: https://your-api.onrender.com/docs"

echo "🎯 Next Steps:"
echo "1. Configure environment variables on your hosting platform"
echo "2. Set up database (PostgreSQL recommended)"
echo "3. Configure CORS origins"
echo "4. Set up monitoring and logging"
echo "5. Test all API endpoints"

echo "✅ Deployment script completed!"
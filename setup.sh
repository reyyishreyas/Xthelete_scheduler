#!/bin/bash

# 🚀 XTHLETE Tournament System - One-Click Setup Script

echo "🏆 XTHLETE Tournament Management System Setup"
echo "============================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ npm found: $(npm --version)"

# Navigate to project directory
cd /home/z/my-project

echo ""
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

echo ""
echo "🗄️ Setting up database..."
npm run db:push

if [ $? -ne 0 ]; then
    echo "❌ Failed to setup database"
    exit 1
fi

echo "✅ Database setup completed"

echo ""
echo "🚀 Starting development server..."
echo "=================================="
echo "📱 The application will be available at: http://localhost:3000"
echo "🛑 Press Ctrl+C to stop the server"
echo "=================================="

# Start the development server
npm run dev
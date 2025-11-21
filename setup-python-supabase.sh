#!/bin/bash

# 🚀 Complete Python FastAPI + Supabase Setup Script

echo "🏆 XTHLETE Tournament System - Python FastAPI + Supabase Setup"
echo "=============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ from https://python.org"
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

print_status "Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm."
    exit 1
fi

print_status "npm found: $(npm --version)"

echo ""
echo "📋 Setup Instructions:"
echo "====================="
echo ""
echo "1️⃣  First, setup your Supabase project:"
echo "   • Go to https://supabase.com"
echo "   • Create a new project"
echo "   • Get your Project URL and API keys from Settings → API"
echo "   • Run the SQL from 'supabase_schema.sql' in the SQL Editor"
echo ""
echo "2️⃣  Then run this script again with your Supabase credentials"
echo ""

# Check if .env file exists
if [ ! -f "/home/z/my-project/python-backend/.env" ]; then
    print_warning ".env file not found in python-backend directory"
    echo ""
    echo "Please create the .env file with your Supabase credentials:"
    echo "cd /home/z/my-project/python-backend"
    echo "cp .env.example .env"
    echo "nano .env  # Add your SUPABASE_URL, SUPABASE_KEY, and SUPABASE_SERVICE_KEY"
    echo ""
    exit 1
fi

print_status ".env file found"

# Navigate to project root
cd /home/z/my-project

echo ""
echo "📦 Installing frontend dependencies..."
npm install

if [ $? -ne 0 ]; then
    print_error "Failed to install frontend dependencies"
    exit 1
fi

print_status "Frontend dependencies installed"

echo ""
echo "🐍 Setting up Python backend..."

cd python-backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Failed to install Python dependencies"
    exit 1
fi

print_status "Python dependencies installed"

# Go back to project root
cd ..

echo ""
echo "🔧 Setup Complete!"
echo "=================="
echo ""
echo "🚀 To start the system:"
echo ""
echo "Terminal 1 - Start Python Backend:"
echo "cd /home/z/my-project/python-backend"
echo "source venv/bin/activate"
echo "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Terminal 2 - Start Frontend:"
echo "cd /home/z/my-project"
echo "npm run dev"
echo ""
echo "📱 Access Points:"
echo "• Frontend: http://localhost:3000"
echo "• Backend API: http://localhost:8000"
echo "• API Docs: http://localhost:8000/docs"
echo "• Health Check: http://localhost:8000/health"
echo ""
echo "🎯 Next Steps:"
echo "1. Start both servers as shown above"
echo "2. Open http://localhost:3000 in your browser"
echo "3. Create clubs and register players"
echo "4. Create tournaments and generate fixtures"
echo ""
print_status "Setup completed successfully! 🎉"
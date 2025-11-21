#!/bin/bash

# 🚀 XTHLETE Python FastAPI + Supabase Setup Script

echo "🏆 XTHLETE Tournament System - Python FastAPI + Supabase Setup"
echo "============================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Navigate to Python backend directory
cd /home/z/my-project/python-backend

echo ""
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"

echo ""
echo "📦 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

echo ""
echo "⚙️  Environment Setup Required!"
echo "=================================="
echo "Before running the server, you need to:"
echo ""
echo "1. Create a Supabase project at https://supabase.com"
echo "2. Run the SQL script from PYTHON_SETUP.md"
echo "3. Create a .env file with your Supabase credentials:"
echo "   SUPABASE_URL='https://your-project.supabase.co'"
echo "   SUPABASE_KEY='your-anon-key'"
echo ""
echo "4. Then run: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cat > .env << EOL
# Supabase Configuration
# Replace these with your actual Supabase credentials
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_KEY="your-anon-key-here"
EOL
    echo "✅ .env template created. Please edit it with your Supabase credentials."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🚀 Ready to start the Python backend!"
echo "===================================="
echo "After configuring your .env file, run:"
echo ""
echo "source venv/bin/activate"
echo "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Then access:"
echo "- API Documentation: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/health"
echo "- ReDoc: http://localhost:8000/redoc"
#!/bin/bash

# 🚀 Quick Setup for XTHLETE Python FastAPI + Supabase

echo "🏆 XTHLETE Tournament System - Quick Setup"
echo "========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Navigate to backend
cd /home/z/my-project/python-backend

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "⚙️  Setup Complete!"
echo "===================="
echo ""
echo "Next steps:"
echo "1. Create Supabase project: https://supabase.com"
echo "2. Run SQL script from SIMPLE_SETUP.md"
echo "3. Edit .env file with your Supabase credentials"
echo "4. Start server: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Then start frontend: cd .. && npm run dev"
echo ""
echo "Access:"
echo "- Frontend: http://localhost:3000"
echo "- API Docs: http://localhost:8000/docs"

# Create .env template
if [ ! -f .env ]; then
    echo "📝 Creating .env template..."
    cat > .env << EOL
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key"
EOL
    echo "✅ .env template created. Edit it with your Supabase credentials."
fi

echo ""
echo "🎉 Ready to start your tournament management system!"
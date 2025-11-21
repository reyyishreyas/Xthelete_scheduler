# 🚀 Quick Start Guide - XTHLETE Tournament Management System

## 📋 Prerequisites

Before you start, make sure you have:

1. **Node.js** (v18 or higher) - [Download here](https://nodejs.org/)
2. **Git** - [Download here](https://git-scm.com/)
3. **Code Editor** (VS Code recommended)
4. **Terminal/Command Prompt**

---

## 🎯 Option 1: Run the Next.js System (Recommended)

This is the main system with both frontend and backend built together.

### Step 1: Navigate to Project Directory
```bash
cd /home/z/my-project
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Setup Database
```bash
# Push the database schema
npm run db:push

# (Optional) View the database in Prisma Studio
npx prisma studio
```

### Step 4: Start the Development Server
```bash
npm run dev
```

### Step 5: Access the Application
Open your browser and go to: **http://localhost:3000**

That's it! The system is now running with:
- ✅ Frontend dashboard
- ✅ Backend APIs
- ✅ Database connectivity
- ✅ All algorithms implemented

---

## 🐍 Option 2: Run the Python Backend (Alternative)

If you prefer Python backend instead of Next.js API routes:

### Step 1: Navigate to Python Backend
```bash
cd /home/z/my-project/python-backend
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Database
```bash
# Set database URL (SQLite for development)
export DATABASE_URL="sqlite:///./tournament.db"

# Create database tables
python -c "from app.models.database import create_tables; create_tables()"
```

### Step 5: Start Python Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Access Python API
Open your browser and go to: **http://localhost:8000/docs**

---

## 🔄 Option 3: Run Both Systems (Full Setup)

For the complete experience, you can run both the Next.js frontend and Python backend:

### Terminal 1 - Start Next.js Frontend
```bash
cd /home/z/my-project
npm run dev
```

### Terminal 2 - Start Python Backend
```bash
cd /home/z/my-project/python-backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Points:
- **Frontend**: http://localhost:3000
- **Python API**: http://localhost:8000/docs
- **Next.js API**: http://localhost:3000/api

---

## 🛠️ Troubleshooting Common Issues

### Issue 1: "Command not found: npm"
**Solution**: Install Node.js from [nodejs.org](https://nodejs.org/)

### Issue 2: Database connection error
**Solution**: 
```bash
# Reset database
npm run db:push
```

### Issue 3: Port already in use
**Solution**: Kill the process or use different port
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### Issue 4: Python virtual environment issues
**Solution**: 
```bash
# Delete and recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📱 What You Can Do After Running

### 1. Create Your First Tournament
- Navigate to the dashboard
- Click "Create Tournament"
- Fill in tournament details

### 2. Register Players
- Go to "Players" section
- Add players with their club information
- System prevents duplicates automatically

### 3. Generate Fixtures
- Select a tournament
- Click "Generate Fixtures"
- Choose tournament type (Knockout/Round Robin)

### 4. Schedule Matches
- Go to "Scheduling" section
- Select courts and time slots
- System optimizes automatically

### 5. Manage Matches
- Use match security codes for access
- Update scores in real-time
- View live standings

---

## 🔧 Development Commands

### Next.js Commands
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Check code quality
npm run db:push      # Update database schema
npm run db:studio    # Open Prisma Studio
```

### Python Commands
```bash
uvicorn app.main:app --reload    # Start development server
pytest                          # Run tests
pytest --cov=app                # Run tests with coverage
```

---

## 🌐 Access Points Summary

| Service | URL | Description |
|---------|-----|-------------|
| **Main Dashboard** | http://localhost:3000 | Next.js frontend |
| **Next.js API** | http://localhost:3000/api | Built-in backend |
| **Python API** | http://localhost:8000 | Alternative backend |
| **API Docs** | http://localhost:8000/docs | Python API documentation |
| **Database** | http://localhost:5555 | Prisma Studio (if running) |

---

## 🎯 Quick Test Checklist

After running, verify these work:

- [ ] Dashboard loads at http://localhost:3000
- [ ] Can create a new club
- [ ] Can register players (no duplicates)
- [ ] Can create a tournament
- [ ] Can generate fixtures
- [ ] Can schedule matches
- [ ] Match codes are generated
- [ ] API endpoints respond correctly

---

## 📞 Need Help?

If you encounter any issues:

1. **Check the logs** in your terminal
2. **Verify all dependencies** are installed
3. **Ensure ports are available**
4. **Check database connection**

The system is designed to be robust and user-friendly. Most issues are resolved by following the troubleshooting steps above.

---

## 🎉 You're Ready!

Once you see the dashboard at http://localhost:3000, you're all set to manage tournaments like a pro! The system includes all the advanced algorithms and features requested for the XTHLETE hackathon.

**Happy Tournament Managing! 🏆**
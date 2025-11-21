# 🚀 Python FastAPI + Supabase Setup Guide

## 📋 Prerequisites

1. **Supabase Account** - [Create free account](https://supabase.com)
2. **Python 3.8+** - [Download here](https://python.org)
3. **Node.js 18+** - [Download here](https://nodejs.org)

---

## 🗄️ Step 1: Setup Supabase Database

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up/login
4. Create new project
5. Choose database password
6. Select region closest to you

### 2. Get Your Credentials
From your Supabase dashboard:
1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (something like `https://xxxxxxxx.supabase.co`)
   - **anon key** (public key)
   - **service_role key** (secret key)

### 3. Create Database Schema
1. Go to **SQL Editor** in Supabase dashboard
2. Click "New query"
3. Copy and paste the contents of `supabase_schema.sql`
4. Click "Run"

---

## 🐍 Step 2: Setup Python Backend

### 1. Navigate to Python Backend
```bash
cd /home/z/my-project/python-backend
```

### 2. Create Environment File
```bash
cp .env.example .env
```

### 3. Edit Environment File
```bash
nano .env  # or use any text editor
```

Add your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

### 4. Create Virtual Environment
```bash
# On Mac/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Test the Backend
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Verify Backend Working
Open your browser and go to:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🎨 Step 3: Setup Frontend

### 1. Navigate to Frontend
```bash
cd /home/z/my-project
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Create Environment File for Frontend
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 4. Start Frontend
```bash
npm run dev
```

### 5. Access Frontend
Open your browser and go to: **http://localhost:3000**

---

## 🎯 Step 4: Test the Complete System

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Test API Endpoints
Go to http://localhost:8000/docs and try:
- Create a club
- Register players
- Create tournaments
- Generate fixtures

### 3. Test Frontend Integration
1. Open http://localhost:3000
2. Create a new club
3. Register players
4. Create tournament
5. Generate fixtures

---

## 🛠️ Troubleshooting

### Issue: "SUPABASE_URL not set"
**Solution**: Make sure you created `.env` file with correct credentials

### Issue: "Database connection failed"
**Solution**: 
1. Check Supabase project is active
2. Verify URL and keys are correct
3. Make sure database schema was created

### Issue: "Port already in use"
**Solution**: 
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: "CORS errors"
**Solution**: Make sure frontend URL is in CORS origins:
```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 Production Deployment

### Backend (Python FastAPI)
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Next.js)
```bash
# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables for Production
```env
# Backend (.env)
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_KEY=your-prod-anon-key
SUPABASE_SERVICE_KEY=your-prod-service-key
DEBUG=False

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

---

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Supabase      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Cloud DB      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow:
1. **Frontend** sends requests to **FastAPI backend**
2. **Backend** processes requests using algorithms
3. **Backend** stores/retrieves data from **Supabase**
4. **Backend** returns results to **frontend**

---

## 🎉 Success Checklist

When everything is working, you should have:

- [ ] **Backend running** at http://localhost:8000
- [ ] **API docs** accessible at http://localhost:8000/docs
- [ ] **Frontend running** at http://localhost:3000
- [ ] **Can create clubs** in the UI
- [ ] **Can register players** without duplicates
- [ ] **Can create tournaments**
- [ ] **Can generate fixtures** using algorithms
- [ ] **Can schedule matches** across courts
- [ ] **Match codes** are generated for security

---

## 📞 Need Help?

1. **Check logs** in both terminals
2. **Verify Supabase connection** in backend
3. **Test API endpoints** directly first
4. **Check CORS configuration**
5. **Verify environment variables**

---

**🎊 Congratulations! You now have a complete Python FastAPI + Supabase tournament management system running!**
# 🚀 XTHLETE Tournament System - Simplified Python FastAPI + Supabase

## 📋 What You Need

1. **Python 3.8+** - [Download here](https://python.org)
2. **Supabase Account** - [Create free account](https://supabase.com)

---

## 🗄️ Step 1: Setup Supabase Database

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create new project
4. Choose database password

### 1.2 Get Your Credentials
From Supabase dashboard → **Project Settings** → **API**:
- Copy **Project URL** (e.g., `https://xxxxxxxx.supabase.co`)
- Copy **anon public** key (starts with `eyJ...`)

### 1.3 Create Database Tables
Go to **SQL Editor** in Supabase and run this SQL:

```sql
-- Clubs table
CREATE TABLE clubs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Players table
CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 5 AND age <= 100),
    club_id UUID NOT NULL REFERENCES clubs(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('U15', 'U17', 'adults', 'open')),
    type VARCHAR(20) NOT NULL CHECK (type IN ('singles', 'doubles', 'mixed_doubles')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Registrations table
CREATE TABLE registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id),
    event_id UUID NOT NULL REFERENCES events(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(player_id, event_id)
);

-- Tournaments table
CREATE TABLE tournaments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    event_id UUID NOT NULL REFERENCES events(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('knockout', 'round_robin')),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Courts table
CREATE TABLE courts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    location TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Rounds table
CREATE TABLE rounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id),
    round_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Matches table
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id),
    round_id UUID NOT NULL REFERENCES rounds(id),
    match_number INTEGER NOT NULL,
    player1_id UUID REFERENCES players(id),
    player2_id UUID REFERENCES players(id),
    court_id UUID REFERENCES courts(id),
    scheduled_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'scheduled', 'in_progress', 'completed', 'cancelled')),
    player1_score INTEGER,
    player2_score INTEGER,
    winner_id UUID REFERENCES players(id),
    match_code VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Standings table
CREATE TABLE standings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tournament_id UUID NOT NULL REFERENCES tournaments(id),
    player_id UUID REFERENCES players(id),
    points INTEGER DEFAULT 0,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    position INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_players_club_id ON players(club_id);
CREATE INDEX idx_registrations_player_id ON registrations(player_id);
CREATE INDEX idx_registrations_event_id ON registrations(event_id);
CREATE INDEX idx_tournaments_event_id ON tournaments(event_id);
CREATE INDEX idx_matches_tournament_id ON matches(tournament_id);
CREATE INDEX idx_matches_round_id ON matches(round_id);
CREATE INDEX idx_standings_tournament_id ON standings(tournament_id);
```

---

## 🐍 Step 2: Setup Python Backend

```bash
cd /home/z/my-project/python-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo 'SUPABASE_URL="https://your-project.supabase.co"' > .env
echo 'SUPABASE_KEY="your-anon-key"' >> .env
```

**Important**: Replace the Supabase URL and key with your actual credentials.

---

## 🚀 Step 3: Start the System

### Start Python Backend
```bash
cd /home/z/my-project/python-backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Start Next.js Frontend
```bash
cd /home/z/my-project
npm run dev
```

---

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🧪 Test the API

### Create a Club
```bash
curl -X POST "http://localhost:8000/api/clubs" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tennis Club A", "code": "TCA"}'
```

### Create a Player
```bash
curl -X POST "http://localhost:8000/api/players" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "phone": "+1234567890", "age": 25, "club_id": "your-club-id"}'
```

### Generate Pairings
```bash
curl -X POST "http://localhost:8000/api/algorithms/pairing" \
  -H "Content-Type: application/json" \
  -d '{"player_ids": ["player1-id", "player2-id"]}'
```

---

## 🎯 Available Features

### **API Endpoints:**
- `/api/clubs` - Club management
- `/api/players` - Player registration
- `/api/events` - Event creation
- `/api/tournaments` - Tournament management
- `/api/matches` - Match scheduling
- `/api/courts` - Court management
- `/api/algorithms/*` - Advanced algorithms

### **Advanced Algorithms:**
- **Anti-Cluster Distribution** - Smart player grouping
- **Backtracking Pairing** - Same-club avoidance
- **Smart Scheduling** - Multi-court optimization
- **Match Security** - SHA-256 access codes
- **Round Robin** - Circle rotation method
- **Knockout** - Smart seeding system

---

## 🛠️ Troubleshooting

### Issue: "Supabase connection failed"
**Solution**: Check your `.env` file has correct URL and key

### Issue: "Table does not exist"
**Solution**: Run the SQL script in Supabase SQL Editor

### Issue: "Module not found"
**Solution**: Make sure you're in the virtual environment
```bash
source venv/bin/activate
```

---

## 🎉 Success Indicators

✅ Working when:
- Python backend starts without errors
- API docs load at http://localhost:8000/docs
- Health check returns success
- Frontend connects to backend
- Data appears in Supabase dashboard

---

**🏆 Your simplified XTHLETE Tournament System is ready!**

**Backend**: Python FastAPI + Supabase  
**Frontend**: Next.js + TypeScript  
**Database**: Supabase (PostgreSQL)  
**Algorithms**: All 6 advanced algorithms implemented
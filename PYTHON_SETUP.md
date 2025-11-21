# 🚀 XTHLETE Tournament System - Python FastAPI + Supabase Setup

## 📋 Prerequisites

1. **Python 3.8+** - [Download here](https://python.org)
2. **Supabase Account** - [Create free account](https://supabase.com)
3. **Git** - [Download here](https://git-scm.com/)

---

## 🗄️ Step 1: Setup Supabase Database

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up/login
4. Create new project
5. Choose database password
6. Select region closest to you

### 1.2 Get Your Credentials
From your Supabase dashboard:
1. Go to **Project Settings** → **API**
2. Copy these values:
   - **Project URL** (looks like: `https://xxxxxxxx.supabase.co`)
   - **anon public** key (starts with `eyJ...`)

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
    team1_id UUID,
    team2_id UUID,
    court_id UUID REFERENCES courts(id),
    scheduled_time TIMESTAMP WITH TIME ZONE,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
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
    team_id UUID,
    points INTEGER DEFAULT 0,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    position INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
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

### 2.1 Navigate to Python Backend
```bash
cd /home/z/my-project/python-backend
```

### 2.2 Create Virtual Environment
```bash
# On Mac/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Configure Environment
Create a `.env` file in the `python-backend` directory:

```bash
# Replace with your actual Supabase credentials
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_KEY="your-anon-key-here"
```

**Important**: Replace the values with your actual Supabase URL and key from Step 1.2.

---

## 🚀 Step 3: Start the Python Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 🌐 Step 4: Test the API

### 4.1 API Documentation
Open your browser and go to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4.2 Health Check
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "message": "XTHLETE Tournament API is running",
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

---

## 🎨 Step 5: Update Frontend Configuration

Now update the frontend to use the Python backend:

### 5.1 Create API Client
Create `/home/z/my-project/src/lib/api-client.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000';

export const apiClient = {
  // Clubs
  getClubs: () => fetch(`${API_BASE_URL}/api/clubs`).then(r => r.json()),
  createClub: (club: any) => fetch(`${API_BASE_URL}/api/clubs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(club)
  }).then(r => r.json()),

  // Players
  getPlayers: () => fetch(`${API_BASE_URL}/api/players`).then(r => r.json()),
  createPlayer: (player: any) => fetch(`${API_BASE_URL}/api/players`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(player)
  }).then(r => r.json()),

  // Tournaments
  getTournaments: () => fetch(`${API_BASE_URL}/api/tournaments`).then(r => r.json()),
  createTournament: (tournament: any) => fetch(`${API_BASE_URL}/api/tournaments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tournament)
  }).then(r => r.json()),

  // Add more endpoints as needed...
};
```

---

## 🎯 Step 6: Run the Complete System

### Terminal 1 - Start Python Backend
```bash
cd /home/z/my-project/python-backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Start Next.js Frontend
```bash
cd /home/z/my-project
npm run dev
```

### Access Points:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

---

## 🧪 Step 7: Test the Integration

### 7.1 Create a Club via API
```bash
curl -X POST "http://localhost:8000/api/clubs" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tennis Club A", "code": "TCA"}'
```

### 7.2 Create a Player via API
```bash
curl -X POST "http://localhost:8000/api/players" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "phone": "+1234567890", "age": 25, "club_id": "your-club-id"}'
```

### 7.3 Test Algorithms
```bash
# Generate pairings
curl -X POST "http://localhost:8000/api/algorithms/pairing" \
  -H "Content-Type: application/json" \
  -d '{"player_ids": ["player1-id", "player2-id"]}'
```

---

## 🛠️ Troubleshooting

### Issue: "Supabase connection failed"
**Solution**: Check your `.env` file has correct URL and key

### Issue: "Table does not exist"
**Solution**: Run the SQL script in Supabase SQL Editor

### Issue: "CORS error"
**Solution**: The backend already allows localhost:3000, but check your frontend is running on that port

### Issue: "Module not found"
**Solution**: Make sure you're in the virtual environment
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

---

## 🎉 Success Indicators

✅ You know it's working when:
- Python backend starts without errors
- API docs load at http://localhost:8000/docs
- Health check returns success
- Frontend can call backend APIs
- Data appears in Supabase dashboard

---

## 📱 What You Can Do Now

1. **Create clubs and players** via the API
2. **Set up tournaments** with different types
3. **Generate fixtures** using advanced algorithms
4. **Schedule matches** across multiple courts
5. **Use secure match codes** for access control
6. **View real-time statistics** and standings

---

**🏆 Your XTHLETE Tournament Management System is now running with Python FastAPI + Supabase!**
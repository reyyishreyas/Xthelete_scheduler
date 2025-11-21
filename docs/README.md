# XTHLETE Smart Fixture, Scheduling & Match Management System

A comprehensive tournament management system built with Next.js 15, TypeScript, and Prisma, implementing advanced algorithms for optimal fixture generation and scheduling.

## 🚀 Features

### Core Algorithms
- **Anti-Cluster Distribution**: O(N) grouping algorithm to minimize same-club matchups
- **Backtracking Pairing**: Smart pairing algorithm with penalty-based optimization
- **Round Robin Rotation**: Circle method for balanced round-robin tournaments
- **Smart Scheduling**: Min-Heap based multi-court scheduling with rest time enforcement
- **Knockout Bracket**: Seeded bracket generation with zero bias from quarter-finals
- **Match Security**: SHA-256 based secure match access codes

### System Features
- **Player & Club Management**: Duplicate prevention with fuzzy matching
- **Tournament Types**: Support for Knockout and Round-Robin formats
- **Live Results**: Real-time leaderboard updates and statistics
- **Multi-Court Support**: Efficient scheduling across multiple venues
- **Security**: Role-based access with secure match codes

## 📋 System Requirements

- Node.js 18+
- npm or yarn
- SQLite (for development)
- Prisma CLI

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd xthlete-tournament-system
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL
   ```

4. **Initialize database**
   ```bash
   npx prisma generate
   npm run db:push
   ```

5. **Start development server**
   ```bash
   npm run dev
   ```

## 📊 Database Schema

### Core Models

#### Club
```typescript
interface Club {
  id: string
  name: string
  code: string
  players: Player[]
  teams: Team[]
}
```

#### Player
```typescript
interface Player {
  id: string
  name: string
  phone: string
  age: number
  clubId: string
  club: Club
  registrations: Registration[]
  teamMembers: TeamMember[]
}
```

#### Tournament
```typescript
interface Tournament {
  id: string
  name: string
  eventId: string
  type: 'knockout' | 'round_robin'
  status: 'pending' | 'active' | 'completed'
  event: Event
  rounds: Round[]
  matches: Match[]
  standings: Standing[]
}
```

#### Match
```typescript
interface Match {
  id: string
  tournamentId: string
  roundId: string
  player1Id?: string
  player2Id?: string
  courtId?: string
  scheduledTime?: Date
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed'
  player1Score?: number
  player2Score?: number
  winnerId?: string
  matchCode?: string
}
```

## 🔧 Algorithm Implementation

### 1. Anti-Cluster Distribution Algorithm

**Location**: `src/lib/algorithms/grouping.ts`

**Purpose**: Distribute players across groups to minimize same-club matchups.

**Algorithm Steps**:
1. Bucket players by club
2. Sort clubs by size (largest first)
3. Round-robin distribute across groups
4. Calculate penalty scores

**Complexity**: O(N)

```typescript
const groupingAlgorithm = new GroupingAlgorithm();
const result = groupingAlgorithm.groupPlayers(players, numGroups);
```

### 2. Backtracking Pairing Algorithm

**Location**: `src/lib/algorithms/backtracking-pairing.ts`

**Purpose**: Generate optimal pairings avoiding same-club matches.

**Algorithm Steps**:
1. Handle odd players with BYE
2. Fix first player
3. Try pairing with every other player
4. Recursively pair remaining players
5. Score using penalty system
6. Choose minimum penalty solution

**Complexity**: O(N!) worst case, typically much better

```typescript
const pairingAlgorithm = new BacktrackingPairingAlgorithm();
const result = pairingAlgorithm.generatePairings(players);
```

### 3. Round Robin Rotation Algorithm

**Location**: `src/lib/algorithms/round-robin.ts`

**Purpose**: Generate balanced round-robin schedules.

**Algorithm Steps**:
1. Arrange players in circle
2. Fix one player (add BYE if odd)
3. Rotate players clockwise each round
4. Pair across the circle
5. Sort to prioritize different-club matches

**Complexity**: O(N²)

```typescript
const roundRobinAlgorithm = new RoundRobinRotationAlgorithm();
const result = roundRobinAlgorithm.generateRoundRobin(players);
```

### 4. Smart Scheduling Engine

**Location**: `src/lib/algorithms/scheduling.ts`

**Purpose**: Schedule matches across multiple courts with constraints.

**Features**:
- Min-Heap for court availability
- Player rest time enforcement
- Delay handling and auto-adjustment
- Working hours compliance

**Complexity**: O(M log C)

```typescript
const schedulingEngine = new SmartSchedulingEngine(constraints);
const result = schedulingEngine.scheduleMatches(matches, courts, startTime);
```

### 5. Knockout Bracket Engine

**Location**: `src/lib/algorithms/knockout.ts`

**Purpose**: Generate and manage knockout tournament brackets.

**Features**:
- Smart seeding (top players to opposite halves)
- Zero bias from quarter-finals
- Automatic progression
- BYE handling

**Complexity**: O(N log N)

```typescript
const knockoutEngine = new KnockoutBracketEngine();
const result = knockoutEngine.generateBracket(players, tournamentName);
```

### 6. Match Code Security System

**Location**: `src/lib/algorithms/match-security.ts`

**Purpose**: Generate secure access codes for matches.

**Features**:
- SHA-256 hashing
- Timestamp-based expiration
- Player and court binding
- One-time use codes

```typescript
const matchSecurity = new MatchCodeSecurity();
const code = matchSecurity.generateMatchCode(matchId, playerIds, courtId, tournamentId);
```

## 🌐 API Documentation

### Clubs API

#### GET /api/clubs
Retrieve all clubs with player and team counts.

#### POST /api/clubs
Create a new club.
```json
{
  "name": "Tennis Club A",
  "code": "TCA"
}
```

#### GET /api/clubs/[id]
Retrieve specific club details.

#### PUT /api/clubs/[id]
Update club information.

#### DELETE /api/clubs/[id]
Delete a club (only if no associated players/teams).

### Players API

#### GET /api/players
Retrieve all players with optional filtering.
- `clubId`: Filter by club
- `eventId`: Filter by event registration

#### POST /api/players
Create a new player with duplicate prevention.
```json
{
  "name": "John Doe",
  "phone": "+1234567890",
  "age": 25,
  "clubId": "club-id"
}
```

#### GET /api/players/[id]
Retrieve specific player details.

#### PUT /api/players/[id]
Update player information.

#### DELETE /api/players/[id]
Delete a player (only if no registrations/team memberships).

### Tournaments API

#### GET /api/tournaments
Retrieve all tournaments with optional filtering.
- `status`: Filter by status
- `type`: Filter by type

#### POST /api/tournaments
Create a new tournament.
```json
{
  "name": "Spring Championship",
  "eventId": "event-id",
  "type": "knockout"
}
```

#### GET /api/tournaments/[id]
Retrieve tournament details with brackets and standings.

#### POST /api/tournaments/[id]/generate-fixtures
Generate fixtures for tournament using algorithms.

### Matches API

#### GET /api/matches
Retrieve matches with filtering options.
- `tournamentId`: Filter by tournament
- `roundId`: Filter by round
- `status`: Filter by status
- `courtId`: Filter by court

#### PUT /api/matches/[id]
Update match result and automatically update next round/standings.
```json
{
  "player1Score": 21,
  "player2Score": 15,
  "status": "completed"
}
```

### Scheduling API

#### POST /api/scheduling
Schedule matches using smart scheduling engine.
```json
{
  "tournamentId": "tournament-id",
  "matchIds": ["match-1", "match-2"],
  "courtIds": ["court-1", "court-2"],
  "startTime": "2024-01-01T09:00:00Z",
  "constraints": {
    "matchDuration": 60,
    "minimumRestTime": 30,
    "bufferTime": 15
  }
}
```

### Security API

#### POST /api/security
Generate secure match codes.
```json
{
  "matchId": "match-id",
  "tournamentId": "tournament-id",
  "type": "umpire"
}
```

#### PUT /api/security
Manage match codes (validate, invalidate, extend).
```json
{
  "code": "MATCH-CODE-123",
  "action": "validate"
}
```

### Results API

#### GET /api/results
Retrieve tournament leaderboards and player statistics.
- `tournamentId`: Get specific tournament leaderboard
- `playerId`: Get player results across tournaments
- `format`: Export format (json, csv, html)

#### POST /api/results
Update match results and trigger leaderboard updates.

## 🎯 Usage Examples

### Creating a Complete Tournament

1. **Create clubs and players**
```typescript
// Create club
const club = await fetch('/api/clubs', {
  method: 'POST',
  body: JSON.stringify({ name: 'Tennis Club A', code: 'TCA' })
});

// Create players
const player = await fetch('/api/players', {
  method: 'POST',
  body: JSON.stringify({
    name: 'John Doe',
    phone: '+1234567890',
    age: 25,
    clubId: club.id
  })
});
```

2. **Create tournament and generate fixtures**
```typescript
// Create tournament
const tournament = await fetch('/api/tournaments', {
  method: 'POST',
  body: JSON.stringify({
    name: 'Spring Championship',
    eventId: 'event-id',
    type: 'knockout'
  })
});

// Generate fixtures
const fixtures = await fetch(`/api/tournaments/${tournament.id}/generate-fixtures`, {
  method: 'POST'
});
```

3. **Schedule matches**
```typescript
const schedule = await fetch('/api/scheduling', {
  method: 'POST',
  body: JSON.stringify({
    tournamentId: tournament.id,
    matchIds: ['match-1', 'match-2'],
    courtIds: ['court-1'],
    startTime: '2024-01-01T09:00:00Z'
  })
});
```

4. **Generate match codes**
```typescript
const matchCode = await fetch('/api/security', {
  method: 'POST',
  body: JSON.stringify({
    matchId: 'match-1',
    tournamentId: tournament.id,
    type: 'umpire'
  })
});
```

5. **Update results**
```typescript
const result = await fetch('/api/results', {
  method: 'POST',
  body: JSON.stringify({
    tournamentId: tournament.id,
    matchId: 'match-1',
    player1Score: 21,
    player2Score: 15
  })
});
```

## 🚀 Deployment

### Frontend (Vercel)

1. **Install Vercel CLI**
```bash
npm i -g vercel
```

2. **Deploy**
```bash
vercel --prod
```

3. **Environment Variables**
Set `DATABASE_URL` in Vercel dashboard.

### Backend (Render)

1. **Create `render.yaml`**
```yaml
services:
  - type: web
    name: xthlete-api
    env: node
    buildCommand: npm run build
    startCommand: npm start
    envVars:
      - key: DATABASE_URL
        value: ${DATABASE_URL}
```

2. **Deploy**
```bash
render deploy
```

### Database (Supabase)

1. **Create Supabase project**
2. **Update environment variables**
3. **Run migrations**
```bash
npx prisma db push
```

## 🔒 Security Considerations

- **Match Codes**: SHA-256 encrypted, time-limited access codes
- **Input Validation**: All API endpoints validate input data
- **Duplicate Prevention**: Fuzzy matching for player registration
- **Role-based Access**: Different access levels for umpires and players
- **Data Privacy**: Phone numbers and personal information protected

## 🧪 Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e

# Check code quality
npm run lint
npm run type-check
```

## 📈 Performance

- **Algorithm Efficiency**: All algorithms optimized for tournament sizes
- **Database Indexing**: Proper indexes on frequently queried fields
- **Caching**: In-memory caching for frequently accessed data
- **API Response Times**: < 200ms for most operations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Email: support@xthlete.com
- Documentation: [Link to docs]

## 🗺️ Roadmap

- [ ] Mobile app for match scoring
- [ ] Live streaming integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Integration with external tournament systems
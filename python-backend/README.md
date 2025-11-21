# XTHLETE Tournament Management System - Python Backend

## Overview
This is the Python FastAPI backend for the XTHLETE Tournament Management System, implementing all the required algorithms and APIs for smart fixture generation, scheduling, and match management.

## Features Implemented

### Core Algorithms
1. **Anti-Cluster Distribution Algorithm** - O(N) complexity for optimal player grouping
2. **Backtracking Pairing Algorithm** - Same-club avoidance with minimum penalty scoring
3. **Smart Scheduling Engine** - Min-heap based multi-court scheduling with rest time enforcement
4. **Match Code Security System** - SHA-256 based secure access control
5. **Round Robin Rotation Algorithm** - Circle method with club distribution optimization
6. **Knockout Bracket Engine** - Seeded bracket generation with zero bias from quarter-finals

### API Endpoints
- `/api/clubs` - Club management
- `/api/players` - Player registration with duplicate prevention
- `/api/tournaments` - Tournament creation and management
- `/api/matches` - Match scheduling and management
- `/api/algorithms/*` - Algorithm-specific endpoints
- `/api/statistics` - System statistics

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL or SQLite

### Setup
```bash
# Clone and navigate to the backend directory
cd python-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost/tournament_db"
# or for SQLite:
export DATABASE_URL="sqlite:///./tournament.db"

# Initialize database
python -c "from app.models.database import create_tables; create_tables()"

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Algorithm Details

### 1. Anti-Cluster Distribution Algorithm
```python
# Time Complexity: O(N)
# Space Complexity: O(N)

grouping_algorithm = GroupingAlgorithm()
result = grouping_algorithm.group_players(players, num_groups)
```

### 2. Backtracking Pairing Algorithm
```python
# Time Complexity: O(N!) worst case, much better with pruning
# Space Complexity: O(N) for recursion stack

pairing_algorithm = BacktrackingPairingAlgorithm()
result = pairing_algorithm.generate_pairings(players)
```

### 3. Smart Scheduling Engine
```python
# Time Complexity: O(M log C) where M = matches, C = courts
# Space Complexity: O(M + C)

scheduling_engine = SmartSchedulingEngine(constraints)
result = scheduling_engine.schedule_matches(matches, courts, start_time)
```

### 4. Match Code Security
```python
# SHA-256 based security with timestamp expiration

match_security = MatchCodeSecurity()
code_result = match_security.generate_match_code(match_id, player_ids, court_id, tournament_id)
validation = match_security.validate_match_code(code)
```

## Database Schema

The system uses SQLAlchemy ORM with the following main entities:
- Clubs
- Players (with duplicate prevention)
- Events
- Tournaments (Knockout/Round Robin)
- Matches (with security codes)
- Courts
- Standings

## API Usage Examples

### Create a Club
```bash
curl -X POST "http://localhost:8000/api/clubs" \
  -H "Content-Type: application/json" \
  -d '{"name": "Tennis Club A", "code": "TCA"}'
```

### Register a Player
```bash
curl -X POST "http://localhost:8000/api/players" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "phone": "+1234567890", "age": 25, "club_id": "club_id"}'
```

### Generate Pairings
```bash
curl -X POST "http://localhost:8000/api/algorithms/pairing" \
  -H "Content-Type: application/json" \
  -d '{"player_ids": ["id1", "id2", "id3", "id4"]}'
```

### Schedule Matches
```bash
curl -X POST "http://localhost:8000/api/algorithms/scheduling" \
  -H "Content-Type: application/json" \
  -d '{"match_ids": ["m1", "m2"], "court_ids": ["c1", "c2"], "start_time": "2024-01-01T09:00:00"}'
```

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT secret key (if using authentication)
- `CORS_ORIGINS` - Allowed CORS origins

## Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Performance Characteristics

### Algorithm Performance
- **Grouping**: O(N) - Linear time for any number of players
- **Pairing**: O(N!) worst case, but typically O(N²) with pruning
- **Scheduling**: O(M log C) - Efficient for large tournaments
- **Security**: O(1) - Constant time for code generation/validation

### Scalability
- Supports 1000+ players per tournament
- Handles 50+ concurrent courts
- Real-time scheduling adjustments
- Memory-efficient algorithms

## Security Features

1. **Match Code Security**
   - SHA-256 hashing
   - Timestamp-based expiration (60 minutes default)
   - Player and court binding
   - One-time use codes

2. **Input Validation**
   - Pydantic models for all inputs
   - SQL injection prevention via ORM
   - Duplicate prevention for players

3. **Access Control**
   - Role-based access (extendable)
   - Secure code validation
   - Tournament-specific permissions

## Integration with Frontend

The Python backend provides RESTful APIs that can be consumed by any frontend framework:
- React/Next.js (as shown in the main project)
- Vue.js
- Angular
- Mobile applications

## Monitoring and Logging

Configure logging in production:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Future Enhancements

1. **WebSocket Support** - Real-time match updates
2. **Advanced Analytics** - Performance metrics and insights
3. **Multi-tenancy** - Support for multiple organizations
4. **Mobile API** - Optimized endpoints for mobile apps
5. **Machine Learning** - Predictive scheduling and outcome prediction

## Support

For issues and questions:
- Check the API documentation at `/docs` (Swagger UI)
- Review the algorithm implementations in `app/algorithms/`
- Test with the provided example endpoints
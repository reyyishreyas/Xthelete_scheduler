# API Documentation

## Overview

The XTHLETE Tournament Management System provides a comprehensive RESTful API for managing clubs, players, tournaments, matches, and results. All endpoints follow REST conventions and return JSON responses.

## Base URL
```
https://your-domain.com/api
```

## Authentication

Currently, the API uses basic authentication. In production, implement JWT or OAuth2 for enhanced security.

## Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

## Clubs API

### GET /api/clubs

Retrieve all clubs with player and team counts.

**Query Parameters:**
- None

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "club-1",
      "name": "Tennis Club A",
      "code": "TCA",
      "createdAt": "2024-01-01T00:00:00Z",
      "updatedAt": "2024-01-01T00:00:00Z",
      "players": [
        {
          "id": "player-1",
          "name": "John Doe"
        }
      ],
      "teams": [
        {
          "id": "team-1",
          "name": "Team A"
        }
      ]
    }
  ]
}
```

### POST /api/clubs

Create a new club.

**Request Body:**
```json
{
  "name": "Tennis Club A",
  "code": "TCA"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "club-1",
    "name": "Tennis Club A",
    "code": "TCA",
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T00:00:00Z"
  }
}
```

### GET /api/clubs/[id]

Retrieve specific club details.

**Path Parameters:**
- `id` - Club ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "club-1",
    "name": "Tennis Club A",
    "code": "TCA",
    "players": [...],
    "teams": [...]
  }
}
```

### PUT /api/clubs/[id]

Update club information.

**Path Parameters:**
- `id` - Club ID

**Request Body:**
```json
{
  "name": "Updated Club Name",
  "code": "UCN"
}
```

### DELETE /api/clubs/[id]

Delete a club (only if no associated players or teams).

**Path Parameters:**
- `id` - Club ID

## Players API

### GET /api/players

Retrieve all players with optional filtering.

**Query Parameters:**
- `clubId` (optional) - Filter by club ID
- `eventId` (optional) - Filter by event registration

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "player-1",
      "name": "John Doe",
      "phone": "+1234567890",
      "age": 25,
      "clubId": "club-1",
      "club": {
        "id": "club-1",
        "name": "Tennis Club A",
        "code": "TCA"
      },
      "registrations": [...],
      "teamMembers": [...]
    }
  ]
}
```

### POST /api/players

Create a new player with duplicate prevention.

**Request Body:**
```json
{
  "name": "John Doe",
  "phone": "+1234567890",
  "age": 25,
  "clubId": "club-1"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "player-1",
    "name": "John Doe",
    "phone": "+1234567890",
    "age": 25,
    "clubId": "club-1",
    "club": {
      "id": "club-1",
      "name": "Tennis Club A",
      "code": "TCA"
    }
  }
}
```

### GET /api/players/[id]

Retrieve specific player details.

### PUT /api/players/[id]

Update player information.

### DELETE /api/players/[id]

Delete a player (only if no registrations or team memberships).

## Tournaments API

### GET /api/tournaments

Retrieve all tournaments with optional filtering.

**Query Parameters:**
- `status` (optional) - Filter by status (`pending`, `active`, `completed`)
- `type` (optional) - Filter by type (`knockout`, `round_robin`)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "tournament-1",
      "name": "Spring Championship",
      "eventId": "event-1",
      "type": "knockout",
      "status": "active",
      "event": {
        "id": "event-1",
        "name": "Men's Singles",
        "category": "Open",
        "type": "Singles"
      },
      "rounds": [...],
      "_count": {
        "matches": 15
      }
    }
  ]
}
```

### POST /api/tournaments

Create a new tournament.

**Request Body:**
```json
{
  "name": "Spring Championship",
  "eventId": "event-1",
  "type": "knockout"
}
```

### GET /api/tournaments/[id]

Retrieve tournament details with brackets and standings.

### POST /api/tournaments/[id]/generate-fixtures

Generate fixtures for tournament using algorithms.

**Response:**
```json
{
  "success": true,
  "data": {
    "type": "knockout",
    "rounds": [
      {
        "id": "round-1",
        "roundNumber": 1,
        "matches": [
          {
            "id": "match-1",
            "player1Id": "player-1",
            "player2Id": "player-2",
            "status": "pending"
          }
        ]
      }
    ]
  },
  "message": "Successfully generated knockout fixtures for 8 players"
}
```

## Matches API

### GET /api/matches

Retrieve matches with filtering options.

**Query Parameters:**
- `tournamentId` (optional) - Filter by tournament
- `roundId` (optional) - Filter by round
- `status` (optional) - Filter by status
- `courtId` (optional) - Filter by court

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "match-1",
      "tournamentId": "tournament-1",
      "roundId": "round-1",
      "matchNumber": 1,
      "player1Id": "player-1",
      "player2Id": "player-2",
      "courtId": "court-1",
      "scheduledTime": "2024-01-01T09:00:00Z",
      "status": "scheduled",
      "player1Score": null,
      "player2Score": null,
      "winnerId": null,
      "matchCode": "ABC123-XYZ789",
      "player1": {
        "id": "player-1",
        "name": "John Doe",
        "club": {
          "id": "club-1",
          "name": "Tennis Club A",
          "code": "TCA"
        }
      },
      "player2": {
        "id": "player-2",
        "name": "Jane Smith",
        "club": {
          "id": "club-2",
          "name": "Sports Academy B",
          "code": "SAB"
        }
      },
      "court": {
        "id": "court-1",
        "name": "Court 1",
        "location": "Main Hall"
      }
    }
  ]
}
```

### PUT /api/matches/[id]

Update match result and automatically update next round/standings.

**Request Body:**
```json
{
  "player1Score": 21,
  "player2Score": 15,
  "status": "completed",
  "startTime": "2024-01-01T09:00:00Z",
  "endTime": "2024-01-01T09:45:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "match-1",
    "player1Score": 21,
    "player2Score": 15,
    "winnerId": "player-1",
    "status": "completed"
  }
}
```

## Scheduling API

### POST /api/scheduling

Schedule matches using smart scheduling engine.

**Request Body:**
```json
{
  "tournamentId": "tournament-1",
  "matchIds": ["match-1", "match-2", "match-3"],
  "courtIds": ["court-1", "court-2"],
  "startTime": "2024-01-01T09:00:00Z",
  "constraints": {
    "matchDuration": 60,
    "minimumRestTime": 30,
    "bufferTime": 15,
    "maxMatchesPerDay": 8,
    "workingHoursStart": 8,
    "workingHoursEnd": 22
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scheduledMatches": [
      {
        "id": "match-1",
        "court": {
          "id": "court-1",
          "name": "Court 1"
        },
        "scheduledStartTime": "2024-01-01T09:00:00Z",
        "scheduledEndTime": "2024-01-01T10:00:00Z",
        "status": "scheduled"
      }
    ],
    "totalScheduleTime": 180,
    "courtUtilization": {
      "court-1": 85.5,
      "court-2": 92.3
    },
    "conflicts": [],
    "violations": []
  },
  "message": "Successfully scheduled 3 matches"
}
```

## Security API

### POST /api/security

Generate secure match codes.

**Request Body:**
```json
{
  "matchId": "match-1",
  "tournamentId": "tournament-1",
  "type": "umpire"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "code": "ABC123XYZ789DEF456",
    "expiresAt": "2024-01-01T10:00:00Z",
    "matchInfo": {
      "id": "match-1",
      "player1": "John Doe",
      "player2": "Jane Smith",
      "court": "Court 1"
    }
  },
  "message": "Successfully generated umpire code for match"
}
```

### PUT /api/security

Manage match codes (validate, invalidate, extend).

**Request Body (Validate):**
```json
{
  "code": "ABC123XYZ789DEF456",
  "action": "validate"
}
```

**Request Body (Invalidate):**
```json
{
  "code": "ABC123XYZ789DEF456",
  "action": "invalidate"
}
```

**Request Body (Extend):**
```json
{
  "code": "ABC123XYZ789DEF456",
  "action": "extend",
  "additionalMinutes": 30
}
```

### GET /api/security

Get security statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "activeCodes": 15,
    "usedCodes": 42,
    "expiryMinutes": 60
  }
}
```

## Results API

### GET /api/results

Retrieve tournament leaderboards and player statistics.

**Query Parameters:**
- `tournamentId` (optional) - Get specific tournament leaderboard
- `playerId` (optional) - Get player results across tournaments
- `format` (optional) - Export format (`json`, `csv`, `html`)

**Response (Tournament Leaderboard):**
```json
{
  "success": true,
  "data": {
    "tournamentId": "tournament-1",
    "tournamentName": "Spring Championship",
    "type": "round_robin",
    "lastUpdated": "2024-01-01T12:00:00Z",
    "playerResults": [
      {
        "playerId": "player-1",
        "playerName": "John Doe",
        "clubId": "club-1",
        "clubName": "Tennis Club A",
        "matchesPlayed": 5,
        "wins": 4,
        "losses": 1,
        "draws": 0,
        "pointsScored": 105,
        "pointsConceded": 78,
        "points": 8,
        "position": 1
      }
    ],
    "isComplete": false
  }
}
```

### POST /api/results

Update match results and trigger leaderboard updates.

**Request Body:**
```json
{
  "tournamentId": "tournament-1",
  "matchId": "match-1",
  "player1Score": 21,
  "player2Score": 15,
  "status": "completed"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "matchId": "match-1",
    "player1Id": "player-1",
    "player2Id": "player-2",
    "player1Score": 21,
    "player2Score": 15,
    "winnerId": "player-1",
    "timestamp": "2024-01-01T12:00:00Z",
    "status": "completed"
  },
  "message": "Match result updated successfully"
}
```

## Error Handling

### Common Error Codes

- `VALIDATION_ERROR` - Invalid input data
- `DUPLICATE_ENTRY` - Resource already exists
- `RESOURCE_NOT_FOUND` - Resource doesn't exist
- `CONSTRAINT_VIOLATION` - Business rule violation
- `INTERNAL_ERROR` - Server error

### Example Error Response

```json
{
  "success": false,
  "error": "Player with this name and phone already exists",
  "code": "DUPLICATE_ENTRY"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## Pagination

For endpoints returning large datasets, pagination is supported:

**Query Parameters:**
- `page` (default: 1) - Page number
- `limit` (default: 20) - Items per page
- `sort` (optional) - Sort field
- `order` (optional) - Sort order (`asc`, `desc`)

**Response:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Webhooks

The system supports webhooks for real-time notifications:

### Configure Webhook

```json
{
  "url": "https://your-webhook-url.com/endpoint",
  "events": ["match_completed", "tournament_started", "player_registered"]
}
```

### Webhook Payload

```json
{
  "event": "match_completed",
  "data": {
    "matchId": "match-1",
    "tournamentId": "tournament-1",
    "winnerId": "player-1",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## SDK Examples

### JavaScript/TypeScript

```typescript
// Create tournament
const tournament = await fetch('/api/tournaments', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Spring Championship',
    eventId: 'event-1',
    type: 'knockout'
  })
});

// Generate fixtures
const fixtures = await fetch(`/api/tournaments/${tournament.id}/generate-fixtures`, {
  method: 'POST'
});

// Schedule matches
const schedule = await fetch('/api/scheduling', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tournamentId: tournament.id,
    matchIds: ['match-1', 'match-2'],
    courtIds: ['court-1'],
    startTime: '2024-01-01T09:00:00Z'
  })
});
```

### Python

```python
import requests

# Create tournament
tournament = requests.post('/api/tournaments', json={
    'name': 'Spring Championship',
    'eventId': 'event-1',
    'type': 'knockout'
})

# Generate fixtures
fixtures = requests.post(f'/api/tournaments/{tournament.json()["data"]["id"]}/generate-fixtures')

# Update match result
result = requests.put('/api/matches/match-1', json={
    'player1Score': 21,
    'player2Score': 15,
    'status': 'completed'
})
```

This API provides comprehensive functionality for managing tournament operations with proper error handling, security, and performance considerations.
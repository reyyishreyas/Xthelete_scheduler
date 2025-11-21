from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from app.models.schemas import RegistrationBase
import os
from datetime import datetime
import uuid

from .models.schemas import *
from .supabase_client import get_db, SupabaseClient
from .algorithms.tournament_algorithms import (
    GroupingAlgorithm, 
    BacktrackingPairingAlgorithm, 
    SmartSchedulingEngine,
    MatchCodeSecurity,
    RoundRobinRotationAlgorithm,
    KnockoutBracketEngine
)

# Create FastAPI app
app = FastAPI(
    title="XTHLETE Tournament Management API",
    description="Smart Fixture, Scheduling & Match Management System - Python FastAPI Backend with Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize algorithms
grouping_algorithm = GroupingAlgorithm()
pairing_algorithm = BacktrackingPairingAlgorithm()
scheduling_engine = SmartSchedulingEngine()
match_security = MatchCodeSecurity()
round_robin_engine = RoundRobinRotationAlgorithm()
knockout_engine = KnockoutBracketEngine()

# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    return APIResponse(
        success=True,
        data={"status": "healthy", "message": "XTHLETE Tournament API is running", "timestamp": datetime.now()}
    )

# Club endpoints
@app.get("/api/clubs", response_model=APIResponse)
async def get_clubs(db: SupabaseClient = Depends(get_db)):
    """Get all clubs with player counts"""
    try:
        clubs = await db.get_clubs_with_player_count()
        return APIResponse(success=True, data=clubs)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/registrations", response_model=APIResponse)
async def register_player(data: RegistrationCreate):
    result = supabase.table("registrations").insert(data.model_dump()).execute()
    return APIResponse(success=True, data=result.data)

@app.post("/api/clubs", response_model=APIResponse)
async def create_club(club: ClubCreate, db: SupabaseClient = Depends(get_db)):
    """Create a new club"""
    try:
        # Check if club already exists
        existing_clubs = await db.get_all("clubs", filters={"name": club.name})
        if existing_clubs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Club with this name already exists"
            )
        
        existing_clubs = await db.get_all("clubs", filters={"code": club.code})
        if existing_clubs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Club with this code already exists"
            )
        
        # Create club
        club_data = {
            "id": str(uuid.uuid4()),
            "name": club.name,
            "code": club.code.upper(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        new_club = await db.insert("clubs", club_data)
        return APIResponse(success=True, data=new_club)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Player endpoints
@app.get("/api/players", response_model=APIResponse)
async def get_players(db: SupabaseClient = Depends(get_db)):
    """Get all players with club information"""
    try:
        players = await db.get_with_joins("players", "*, club:club_id(*)")
        return APIResponse(success=True, data=players)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/players", response_model=APIResponse)
async def create_player(player: PlayerCreate, db: SupabaseClient = Depends(get_db)):
    """Create a new player with duplicate prevention"""
    try:
        # Check for duplicates
        existing_player = await db.check_duplicate_player(player.name, player.phone)
        if existing_player:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Player with this name and phone already exists"
            )
        
        # Check if club exists
        club = await db.get_by_id("clubs", player.club_id)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Club not found"
            )
        
        # Create player
        player_data = {
            "id": str(uuid.uuid4()),
            "name": player.name,
            "phone": player.phone,
            "age": player.age,
            "club_id": player.club_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        new_player = await db.insert("players", player_data)
        
        # Get player with club info
        player_with_club = await db.get_with_joins("players", "*, club:club_id(*)", filters={"id": new_player["id"]})
        
        return APIResponse(success=True, data=player_with_club[0] if player_with_club else new_player)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Event endpoints
@app.get("/api/events", response_model=APIResponse)
async def get_events(db: SupabaseClient = Depends(get_db)):
    """Get all events"""
    try:
        events = await db.get_all("events")
        return APIResponse(success=True, data=events)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/events", response_model=APIResponse)
async def create_event(event: EventBase, db: SupabaseClient = Depends(get_db)):
    """Create a new event"""
    try:
        event_data = {
            "id": str(uuid.uuid4()),
            "name": event.name,
            "category": event.category.value,
            "type": event.type.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        new_event = await db.insert("events", event_data)
        return APIResponse(success=True, data=new_event)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Registration endpoints
@app.post("/api/registrations", response_model=APIResponse)
async def create_registration(registration: RegistrationBase, db: SupabaseClient = Depends(get_db)):
    """Register a player for an event"""
    try:
        # Check if player exists
        player = await db.get_by_id("players", registration.player_id)
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found"
            )
        
        # Check if event exists
        event = await db.get_by_id("events", registration.event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Check if already registered
        existing = await db.get_all("registrations", filters={
            "player_id": registration.player_id,
            "event_id": registration.event_id
        })
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Player already registered for this event"
            )
        
        # Create registration
        registration_data = {
            "id": str(uuid.uuid4()),
            "player_id": registration.player_id,
            "event_id": registration.event_id,
            "created_at": datetime.now().isoformat()
        }
        
        new_registration = await db.insert("registrations", registration_data)
        return APIResponse(success=True, data=new_registration)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/registrations/event/{event_id}", response_model=APIResponse)
async def get_event_registrations(event_id: str, db: SupabaseClient = Depends(get_db)):
    """Get all registrations for an event with player details"""
    try:
        registrations = await db.get_event_registrations(event_id)
        return APIResponse(success=True, data=registrations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Tournament endpoints
@app.get("/api/tournaments", response_model=APIResponse)
async def get_tournaments(db: SupabaseClient = Depends(get_db)):
    """Get all tournaments with event details"""
    try:
        tournaments = await db.get_with_joins("tournaments", "*, event:event_id(*)")
        return APIResponse(success=True, data=tournaments)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/tournaments", response_model=APIResponse)
async def create_tournament(tournament: TournamentCreate, db: SupabaseClient = Depends(get_db)):
    """Create a new tournament"""
    try:
        # Check if event exists
        event = await db.get_by_id("events", tournament.event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Create tournament
        tournament_data = {
            "id": str(uuid.uuid4()),
            "name": tournament.name,
            "event_id": tournament.event_id,
            "type": tournament.type.value,
            "status": tournament.status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        new_tournament = await db.insert("tournaments", tournament_data)
        
        # Get tournament with event info
        tournament_with_event = await db.get_with_joins("tournaments", "*, event:event_id(*)", filters={"id": new_tournament["id"]})
        
        return APIResponse(success=True, data=tournament_with_event[0] if tournament_with_event else new_tournament)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Court endpoints
@app.get("/api/courts", response_model=APIResponse)
async def get_courts(db: SupabaseClient = Depends(get_db)):
    """Get all courts"""
    try:
        courts = await db.get_all("courts")
        return APIResponse(success=True, data=courts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/courts", response_model=APIResponse)
async def create_court(court: CourtCreate, db: SupabaseClient = Depends(get_db)):
    """Create a new court"""
    try:
        court_data = {
            "id": str(uuid.uuid4()),
            "name": court.name,
            "location": court.location,
            "is_active": court.is_active,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        new_court = await db.insert("courts", court_data)
        return APIResponse(success=True, data=new_court)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/courts/active", response_model=APIResponse)
async def get_active_courts(db: SupabaseClient = Depends(get_db)):
    """Get all active courts"""
    try:
        courts = await db.get_active_courts()
        return APIResponse(success=True, data=courts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Match endpoints
@app.get("/api/matches", response_model=APIResponse)
async def get_matches(db: SupabaseClient = Depends(get_db)):
    """Get all matches with full details"""
    try:
        matches = await db.get_with_joins("matches", """
            *,
            player1:player1_id(*),
            player2:player2_id(*),
            court:court_id(*),
            round:round_id(*),
            tournament:tournament_id(*)
        """)
        return APIResponse(success=True, data=matches)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/matches/tournament/{tournament_id}", response_model=APIResponse)
async def get_tournament_matches(tournament_id: str, db: SupabaseClient = Depends(get_db)):
    """Get all matches for a tournament"""
    try:
        matches = await db.get_tournament_matches(tournament_id)
        return APIResponse(success=True, data=matches)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/matches", response_model=APIResponse)
async def create_match(match: MatchCreate, db: SupabaseClient = Depends(get_db)):
    """Create a new match with security code"""
    try:
        # Get match count for this round
        existing_matches = await db.get_all("matches", filters={"round_id": match.round_id})
        match_number = len(existing_matches) + 1
        
        # Create match
        match_data = {
            "id": str(uuid.uuid4()),
            "tournament_id": match.tournament_id,
            "round_id": match.round_id,
            "match_number": match_number,
            "player1_id": match.player1_id,
            "player2_id": match.player2_id,
            "team1_id": match.team1_id,
            "team2_id": match.team2_id,
            "court_id": match.court_id,
            "scheduled_time": match.scheduled_time.isoformat() if match.scheduled_time else None,
            "status": match.status.value,
            "player1_score": match.player1_score,
            "player2_score": match.player2_score,
            "winner_id": match.winner_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        new_match = await db.insert("matches", match_data)
        
        # Generate match security code if both players exist
        player_ids = [match.player1_id, match.player2_id]
        player_ids = [pid for pid in player_ids if pid]  # Remove None values
        
        if player_ids:
            match_code_result = match_security.generate_match_code(
                new_match["id"],
                player_ids,
                match.court_id,
                match.tournament_id
            )
            
            # Update match with security code
            await db.update("matches", new_match["id"], {"match_code": match_code_result["code"]})
            new_match["match_code"] = match_code_result["code"]
        
        # Get full match details
        full_match = await db.get_tournament_matches(match.tournament_id)
        created_match = next((m for m in full_match if m["id"] == new_match["id"]), None)
        
        return APIResponse(success=True, data=created_match or new_match)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.put("/api/matches/{match_id}/score", response_model=APIResponse)
async def update_match_score(match_id: str, score_data: UpdateScoreRequest, db: SupabaseClient = Depends(get_db)):
    """Update match score and winner"""
    try:
        success = await db.update_match_scores(
            match_id, 
            score_data.player1_score, 
            score_data.player2_score, 
            score_data.winner_id
        )
        
        if success:
            return APIResponse(success=True, message="Match score updated successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update match score"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Algorithm endpoints
@app.post("/api/algorithms/grouping", response_model=APIResponse)
async def group_players(request: GroupingRequest, db: SupabaseClient = Depends(get_db)):
    """Group players using anti-cluster distribution"""
    try:
        # Get players from database
        players = await db.get_all("players", filters={"id": request.player_ids})
        
        if not players:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No players found"
            )
        
        # Convert to algorithm format
        algorithm_players = [
            AlgorithmPlayer(**player) for player in players
        ]
        
        # Apply grouping algorithm
        result = grouping_algorithm.group_players(algorithm_players, request.num_groups)
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/algorithms/pairing", response_model=APIResponse)
async def generate_pairings(request: PairingRequest, db: SupabaseClient = Depends(get_db)):
    """Generate pairings using backtracking algorithm"""
    try:
        # Get players from database
        players = await db.get_all("players", filters={"id": request.player_ids})
        
        if not players:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No players found"
            )
        
        # Convert to algorithm format
        algorithm_players = [
            AlgorithmPlayer(**player) for player in players
        ]
        
        # Apply pairing algorithm
        result = pairing_algorithm.generate_pairings(algorithm_players)
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/algorithms/round-robin", response_model=APIResponse)
async def generate_round_robin(request: PairingRequest, db: SupabaseClient = Depends(get_db)):
    """Generate round robin fixtures"""
    try:
        # Get players from database
        players = await db.get_all("players", filters={"id": request.player_ids})
        
        if not players:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No players found"
            )
        
        # Convert to algorithm format
        algorithm_players = [
            AlgorithmPlayer(**player) for player in players
        ]
        
        # Apply round robin algorithm
        result = round_robin_engine.generate_round_robin(algorithm_players)
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/algorithms/knockout", response_model=APIResponse)
async def generate_knockout_bracket(request: PairingRequest, db: SupabaseClient = Depends(get_db)):
    """Generate knockout bracket"""
    try:
        # Get players from database
        players = await db.get_all("players", filters={"id": request.player_ids})
        
        if not players:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No players found"
            )
        
        # Convert to algorithm format
        algorithm_players = [
            AlgorithmPlayer(**player) for player in players
        ]
        
        # Apply knockout algorithm
        result = knockout_engine.generate_bracket(algorithm_players, "Tournament")
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/algorithms/scheduling", response_model=APIResponse)
async def schedule_matches(request: SchedulingRequest, db: SupabaseClient = Depends(get_db)):
    """Schedule matches using smart scheduling engine"""
    try:
        # Get matches from database
        matches = await db.get_all("matches", filters={"id": request.match_ids})
        
        # Get courts from database
        courts = await db.get_all("courts", filters={"id": request.court_ids, "is_active": True})
        
        if not matches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matches found"
            )
        
        if not courts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active courts found"
            )
        
        # Convert matches to algorithm format
        algorithm_matches = []
        for match in matches:
            if match.get("player1_id") and match.get("player2_id"):
                player1 = await db.get_by_id("players", match["player1_id"])
                player2 = await db.get_by_id("players", match["player2_id"])
                
                if player1 and player2:
                    algorithm_match = AlgorithmMatch(
                        player1=AlgorithmPlayer(**player1),
                        player2=AlgorithmPlayer(**player2),
                        penalty=1 if player1["club_id"] == player2["club_id"] else 0
                    )
                    algorithm_matches.append(algorithm_match)
        
        # Convert courts to algorithm format
        court_schemas = [
            Court(**court) for court in courts
        ]
        
        # Apply scheduling algorithm
        constraints = request.constraints.dict() if request.constraints else {}
        scheduling_engine = SmartSchedulingEngine(constraints)
        result = scheduling_engine.schedule_matches(algorithm_matches, court_schemas, request.start_time)
        
        # Update matches with scheduled times
        for scheduled_match in result["scheduled_matches"]:
            await db.update("matches", scheduled_match["id"], {
                "court_id": scheduled_match["court"]["id"],
                "scheduled_time": scheduled_match["scheduled_start_time"].isoformat(),
                "status": "scheduled"
            })
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/algorithms/match-code", response_model=APIResponse)
async def generate_match_code(request: MatchCodeRequest):
    """Generate secure match code"""
    try:
        if not request.match_id or not request.player_ids or not request.tournament_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required parameters"
            )
        
        # Generate match code
        result = match_security.generate_match_code(
            request.match_id, 
            request.player_ids, 
            request.court_id, 
            request.tournament_id
        )
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/algorithms/validate-match-code", response_model=APIResponse)
async def validate_match_code(request: ValidateCodeRequest):
    """Validate match code"""
    try:
        if not request.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code is required"
            )
        
        # Validate match code
        result = match_security.validate_match_code(request.code)
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Statistics endpoint
@app.get("/api/statistics", response_model=APIResponse)
async def get_statistics(db: SupabaseClient = Depends(get_db)):
    """Get system statistics"""
    try:
        # Get counts
        players = await db.get_all("players")
        clubs = await db.get_all("clubs")
        tournaments = await db.get_all("tournaments")
        matches = await db.get_all("matches")
        
        # Get security stats
        security_stats = match_security.get_statistics()
        
        stats = {
            "total_players": len(players),
            "total_clubs": len(clubs),
            "total_tournaments": len(tournaments),
            "total_matches": len(matches),
            **security_stats
        }
        
        return APIResponse(success=True, data=stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
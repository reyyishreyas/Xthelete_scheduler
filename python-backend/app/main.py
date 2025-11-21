from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List, Optional
import uvicorn
import os
import uuid
from datetime import datetime
import pandas as pd
import io
import csv
from app.models.schemas import KnockoutRequest
from .models.schemas import *
from .supabase_client import get_db, SupabaseClient

# Import algorithms from separate files
from .algorithms.grouping import GroupingAlgorithm
from .algorithms.pairing import BacktrackingPairingAlgorithm
from .algorithms.round_robin import RoundRobinRotationAlgorithm
from .algorithms.knockout import KnockoutBracketEngine
from .algorithms.scheduling import SmartSchedulingEngine
from .algorithms.match_code_security import MatchCodeSecurity
from .algorithms.csv_registration import CSVRegistrationService

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
round_robin_engine = RoundRobinRotationAlgorithm()
knockout_engine = KnockoutBracketEngine()
match_security = MatchCodeSecurity()
csv_service = CSVRegistrationService()

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
        
        # Apply grouping algorithm
        result = grouping_algorithm.group_players(players, request.num_groups)
        
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
        
        # Apply pairing algorithm
        result = pairing_algorithm.generate_pairings(players)
        
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
        
        # Apply round robin algorithm
        result = round_robin_engine.generate_round_robin(players)
        
        return APIResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/algorithms/knockout", response_model=APIResponse)
async def generate_knockout_bracket(request: KnockoutRequest, db: SupabaseClient = Depends(get_db)):
    """Generate knockout bracket with dynamic seeding"""
    try:
        # Get players from database
        players = await db.get_all("players", filters={"id": request.player_ids})
        
        if not players:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No players found"
            )
        
        # Apply knockout algorithm with dynamic seeding
        result = knockout_engine.generate_bracket(
            players, 
            request.tournament_name or "Tournament",
            request.seeding_method or "performance",
            request.performance_data
        )
        
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
                    algorithm_match = {
                        'player1': player1,
                        'player2': player2,
                        'penalty': 1 if player1["club_id"] == player2["club_id"] else 0
                    }
                    algorithm_matches.append(algorithm_match)
        
        # Apply scheduling algorithm
        constraints = request.constraints.dict() if request.constraints else {}
        scheduling_engine = SmartSchedulingEngine(constraints)
        result = scheduling_engine.schedule_matches(algorithm_matches, courts, request.start_time)
        
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

# CSV Registration endpoints
@app.get("/api/csv/upload-template", response_model=APIResponse)
async def download_csv_template():
    """Download CSV template for player registration"""
    try:
        csv_content = csv_service.export_registration_template()
        
        def iterfile():
            yield csv_content.encode('utf-8')
        
        return StreamingResponse(
            iterfile(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=player_registration_template.csv"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/csv/validate", response_model=APIResponse)
async def validate_csv(file: UploadFile = File(...)):
    """Validate CSV structure and content"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are allowed"
            )
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Validate CSV structure
        validation_result = csv_service.validate_csv_structure(csv_content)
        
        if not validation_result['valid']:
            return APIResponse(
                success=False,
                data=validation_result
            )
        
        # Parse and validate data
        valid_rows, error_rows = csv_service.parse_csv_data(csv_content)
        
        return APIResponse(
            success=True,
            data={
                'validation': validation_result,
                'data_validation': {
                    'valid_rows': len(valid_rows),
                    'error_rows': len(error_rows),
                    'sample_valid_rows': valid_rows[:3],
                    'error_details': error_rows[:10]  # Show first 10 errors
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post("/api/csv/register-players", response_model=APIResponse)
async def register_players_from_csv(
    file: UploadFile = File(...),
    club_id: str = Form(...),
    event_ids: Optional[str] = Form(None),
    db: SupabaseClient = Depends(get_db)
):
    """Register players from CSV with automatic event registration"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are allowed"
            )
        
        # Verify club exists
        club = await db.get_by_id("clubs", club_id)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Club not found"
            )
        
        # Parse event IDs
        target_event_ids = []
        if event_ids:
            target_event_ids = [eid.strip() for eid in event_ids.split(',') if eid.strip()]
        
        # Validate events exist
        if target_event_ids:
            events = await db.get_all("events", filters={"id": target_event_ids})
            found_event_ids = {event['id'] for event in events}
            missing_events = set(target_event_ids) - found_event_ids
            
            if missing_events:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Events not found: {', '.join(missing_events)}"
                )
        
        # Read and parse CSV
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Validate CSV structure
        validation_result = csv_service.validate_csv_structure(csv_content)
        if not validation_result['valid']:
            return APIResponse(
                success=False,
                data=validation_result
            )
        
        # Parse data
        valid_rows, error_rows = csv_service.parse_csv_data(csv_content)
        
        if not valid_rows:
            return APIResponse(
                success=False,
                data={
                    'message': 'No valid players found in CSV',
                    'errors': error_rows
                }
            )
        
        # Prepare player data
        prepared_players = csv_service.prepare_player_data(valid_rows, club_id)
        
        # Check existing players
        existing_players = await db.get_all("players")
        new_players, duplicate_players = csv_service.check_existing_players(
            prepared_players, existing_players
        )
        
        # Register new players
        registered_players = []
        registration_errors = []
        
        for player in new_players:
            try:
                player_data = player.copy()
                player_data['id'] = str(uuid.uuid4())
                registered_player = await db.insert("players", player_data)
                if registered_player:
                    registered_players.append(registered_player)
            except Exception as e:
                registration_errors.append({
                    'player': player,
                    'error': str(e)
                })
        
        # Register to events if specified
        event_registrations = []
        if target_event_ids and registered_players:
            for player in registered_players:
                # Check existing registrations
                existing_regs = await db.get_all("registrations", filters={
                    "player_id": player['id']
                })
                
                reg_validation = csv_service.validate_event_registrations(
                    player['id'], target_event_ids, existing_regs
                )
                
                # Create new registrations
                for reg_data in reg_validation['new_registrations']:
                    try:
                        registration = await db.insert("registrations", {
                            **reg_data,
                            'id': str(uuid.uuid4())
                        })
                        if registration:
                            event_registrations.append(registration)
                    except Exception as e:
                        registration_errors.append({
                            'type': 'event_registration',
                            'player_id': player['id'],
                            'event_id': reg_data['event_id'],
                            'error': str(e)
                        })
        
        # Generate summary
        summary = csv_service.generate_registration_summary(
            validation_result,
            {
                'valid_players': registered_players,
                'duplicate_players': duplicate_players,
                'event_registrations': event_registrations,
                'clubs': [club],
                'errors': registration_errors
            }
        )
        
        return APIResponse(
            success=summary['success'],
            data={
                'summary': summary,
                'registered_players': registered_players,
                'duplicate_players': duplicate_players,
                'event_registrations': event_registrations,
                'errors': registration_errors
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/csv/registration-status/{club_id}", response_model=APIResponse)
async def get_registration_status(club_id: str, db: SupabaseClient = Depends(get_db)):
    """Get registration status for a club"""
    try:
        # Get club info
        club = await db.get_by_id("clubs", club_id)
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Club not found"
            )
        
        # Get all players for this club
        players = await db.get_all("players", filters={"club_id": club_id})
        
        # Get registrations for these players
        player_ids = [p['id'] for p in players]
        registrations = []
        if player_ids:
            registrations = await db.get_all("registrations", filters={"player_id": player_ids})
        
        # Get available events
        events = await db.get_all("events")
        
        # Calculate registration statistics
        total_players = len(players)
        registered_players = len(set(r['player_id'] for r in registrations))
        unregistered_players = total_players - registered_players
        
        # Event registration breakdown
        event_stats = {}
        for event in events:
            event_regs = [r for r in registrations if r['event_id'] == event['id']]
            event_stats[event['id']] = {
                'event_name': event['name'],
                'registered_count': len(event_regs),
                'registered_players': event_regs
            }
        
        return APIResponse(
            success=True,
            data={
                'club': club,
                'statistics': {
                    'total_players': total_players,
                    'registered_players': registered_players,
                    'unregistered_players': unregistered_players,
                    'registration_rate': (registered_players / total_players * 100) if total_players > 0 else 0
                },
                'event_registrations': event_stats,
                'recent_registrations': registrations[-10:]  # Last 10 registrations
            }
        )
        
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
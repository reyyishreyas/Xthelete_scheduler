from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TournamentType(str, Enum):
    KNOCKOUT = "knockout"
    ROUND_ROBIN = "round_robin"

class MatchStatus(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventType(str, Enum):
    SINGLES = "singles"
    DOUBLES = "doubles"
    MIXED_DOUBLES = "mixed_doubles"

class Category(str, Enum):
    U15 = "U15"
    U17 = "U17"
    ADULTS = "adults"
    OPEN = "open"

# Base Models
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True

# Club Models
class ClubBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)

class ClubCreate(ClubBase):
    pass

class Club(ClubBase):
    id: str
    created_at: datetime
    updated_at: datetime
    player_count: Optional[int] = 0

# Player Models
class PlayerBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    age: int = Field(..., ge=5, le=100)
    club_id: str

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: str
    created_at: datetime
    updated_at: datetime
    club: Optional[Dict] = None

# Event Models
class EventBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    category: Category
    type: EventType

class Event(EventBase):
    id: str
    created_at: datetime
    updated_at: datetime

# Tournament Models
class TournamentBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    event_id: str
    type: TournamentType
    status: str = "pending"

class TournamentCreate(TournamentBase):
    pass

class Tournament(TournamentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    event: Optional[Dict] = None

# Court Models
class CourtBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = None
    is_active: bool = True

class CourtCreate(CourtBase):
    pass

class Court(CourtBase):
    id: str
    created_at: datetime
    updated_at: datetime

# Match Models
class MatchBase(BaseSchema):
    player1_id: Optional[str] = None
    player2_id: Optional[str] = None
    court_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: MatchStatus = MatchStatus.PENDING
    player1_score: Optional[int] = None
    player2_score: Optional[int] = None
    winner_id: Optional[str] = None
    match_code: Optional[str] = None

class MatchCreate(MatchBase):
    tournament_id: str
    round_id: str
    match_number: int

class Match(MatchBase):
    id: str
    tournament_id: str
    round_id: str
    match_number: int
    created_at: datetime
    updated_at: datetime
    player1: Optional[Dict] = None
    player2: Optional[Dict] = None
    court: Optional[Court] = None
    round: Optional[Dict] = None
    tournament: Optional[Tournament] = None
# Registration Models
class RegistrationBase(BaseSchema):
    player_id: str
    event_id: str

class RegistrationCreate(RegistrationBase):
    pass

class Registration(RegistrationBase):
    id: str
    created_at: datetime

# Algorithm Models
class AlgorithmPlayer(BaseModel):
    id: str
    name: str
    phone: str
    age: int
    club_id: str
    created_at: datetime
    updated_at: datetime

class AlgorithmMatch(BaseModel):
    player1: AlgorithmPlayer
    player2: AlgorithmPlayer
    penalty: int

class PairingResult(BaseModel):
    matches: List[AlgorithmMatch]
    total_penalty: int
    has_bye: bool = False
    bye_player: Optional[AlgorithmPlayer] = None

class Group(BaseModel):
    id: str
    players: List[AlgorithmPlayer]
    club_distribution: Dict[str, int]

class GroupingResult(BaseModel):
    groups: List[Group]
    total_penalty: int

class RoundRobinResult(BaseModel):
    rounds: List[List[Dict]]
    total_penalty: int
    num_rounds: int
    has_odd_players: bool

class KnockoutBracket(BaseModel):
    id: str
    name: str
    total_players: int
    rounds: int
    matches: List[List[Dict]]
    seeds: List[AlgorithmPlayer]
    is_complete: bool = False
    winner: Optional[AlgorithmPlayer] = None

# Scheduling Models
class SchedulingConstraints(BaseModel):
    match_duration: int = 60
    minimum_rest_time: int = 30
    buffer_time: int = 15
    max_matches_per_day: int = 8
    working_hours_start: int = 8
    working_hours_end: int = 22

class SchedulingResult(BaseModel):
    scheduled_matches: List[Dict]
    total_schedule_time: int
    court_utilization: Dict[str, float]
    player_rest_violations: List[str]
    scheduling_conflicts: List[str]

# Security Models
class MatchCodeData(BaseModel):
    match_id: str
    player_ids: List[str]
    court_id: Optional[str] = None
    timestamp: int
    tournament_id: str
    expires_at: int

class MatchCodeResult(BaseModel):
    code: str
    data: MatchCodeData
    expires_at: datetime

class CodeValidationResult(BaseModel):
    is_valid: bool
    match_data: Optional[MatchCodeData] = None
    error: Optional[str] = None
    is_expired: Optional[bool] = None

# API Response Models
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None

# Request Models for Algorithms
class GroupingRequest(BaseModel):
    player_ids: List[str]
    num_groups: int

class PairingRequest(BaseModel):
    player_ids: List[str]

class SchedulingRequest(BaseModel):
    match_ids: List[str]
    court_ids: List[str]
    start_time: datetime
    constraints: Optional[SchedulingConstraints] = None

class MatchCodeRequest(BaseModel):
    match_id: str
    player_ids: List[str]
    court_id: Optional[str] = None
    tournament_id: str

class ValidateCodeRequest(BaseModel):
    code: str

class UpdateScoreRequest(BaseModel):
    player1_score: int
    player2_score: int
    winner_id: str
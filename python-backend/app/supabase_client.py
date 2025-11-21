import os
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://bbvufkecifsjbycjpaan.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJidnVma2VjaWZzamJ5Y2pwYWFuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM2NTc4MjIsImV4cCI6MjA3OTIzMzgyMn0.2bcF2yRvMKscyxiAffg5rsRQd1a1a1QpkvDnAbCHkKw")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseClient:
    """Wrapper class for Supabase operations"""
    
    def __init__(self):
        self.client = supabase
    
    # Generic CRUD operations
    async def get_all(self, table: str, select: str = "*", filters: Dict = None) -> List[Dict]:
        """Get all records from a table"""
        try:
            query = self.client.table(table).select(select)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting {table}: {e}")
            return []
    
    async def get_by_id(self, table: str, id: str, select: str = "*") -> Optional[Dict]:
        """Get a record by ID"""
        try:
            result = self.client.table(table).select(select).eq("id", id).single().execute()
            return result.data if result.data else None
        except Exception as e:
            print(f"Error getting {table} by ID: {e}")
            return None
    
    async def insert(self, table: str, data: Dict) -> Optional[Dict]:
        """Insert a new record"""
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error inserting into {table}: {e}")
            return None
    
    async def update(self, table: str, id: str, data: Dict) -> Optional[Dict]:
        """Update a record by ID"""
        try:
            result = self.client.table(table).update(data).eq("id", id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating {table}: {e}")
            return None
    
    async def delete(self, table: str, id: str) -> bool:
        """Delete a record by ID"""
        try:
            self.client.table(table).delete().eq("id", id).execute()
            return True
        except Exception as e:
            print(f"Error deleting from {table}: {e}")
            return False
    
    async def get_with_joins(self, table: str, select: str = "*", filters: Dict = None) -> List[Dict]:
        """Get records with joined data"""
        try:
            query = self.client.table(table).select(select)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting {table} with joins: {e}")
            return []
    
    # Specific operations for our tournament system
    async def get_clubs_with_player_count(self) -> List[Dict]:
        """Get clubs with player counts"""
        try:
            # Get all clubs
            clubs_result = self.client.table("clubs").select("*").execute()
            clubs = clubs_result.data if clubs_result.data else []
            
            # Get player counts for each club
            for club in clubs:
                players_result = self.client.table("players").select("id").eq("club_id", club["id"]).execute()
                club["player_count"] = len(players_result.data) if players_result.data else 0
            
            return clubs
        except Exception as e:
            print(f"Error getting clubs with player count: {e}")
            return []
    
    async def check_duplicate_player(self, name: str, phone: str) -> Optional[Dict]:
        """Check for duplicate player by name and phone"""
        try:
            result = self.client.table("players").select("*").or_(f"name.eq.{name},phone.eq.{phone}").execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error checking duplicate player: {e}")
            return None
    
    async def get_players_by_club(self, club_id: str) -> List[Dict]:
        """Get all players for a specific club"""
        return await self.get_all("players", filters={"club_id": club_id})
    
    async def get_tournament_matches(self, tournament_id: str) -> List[Dict]:
        """Get all matches for a tournament with player details"""
        try:
            result = self.client.table("matches").select("""
                *,
                player1:player1_id(*),
                player2:player2_id(*),
                court:court_id(*),
                round:round_id(*),
                tournament:tournament_id(*)
            """).eq("tournament_id", tournament_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting tournament matches: {e}")
            return []
    
    async def get_event_registrations(self, event_id: str) -> List[Dict]:
        """Get all registrations for an event with player details"""
        try:
            result = self.client.table("registrations").select("""
                *,
                player:player_id(*),
                event:event_id(*)
            """).eq("event_id", event_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting event registrations: {e}")
            return []
    
    async def get_active_courts(self) -> List[Dict]:
        """Get all active courts"""
        return await self.get_all("courts", filters={"is_active": True})
    
    async def update_match_scores(self, match_id: str, player1_score: int, player2_score: int, winner_id: str) -> bool:
        """Update match scores and winner"""
        try:
            data = {
                "player1_score": player1_score,
                "player2_score": player2_score,
                "winner_id": winner_id,
                "status": "completed",
                "updated_at": datetime.now().isoformat()
            }
            result = await self.update("matches", match_id, data)
            return result is not None
        except Exception as e:
            print(f"Error updating match scores: {e}")
            return False
    
    async def get_tournament_standings(self, tournament_id: str) -> List[Dict]:
        """Get tournament standings"""
        try:
            result = self.client.table("standings").select("""
                *,
                player:player_id(*),
                team:team_id(*)
            """).eq("tournament_id", tournament_id).order("position").execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting tournament standings: {e}")
            return []

# Create global instance
db_client = SupabaseClient()

# Dependency for FastAPI routes
async def get_db():
    return db_client
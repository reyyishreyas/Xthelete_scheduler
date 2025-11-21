from typing import List, Dict, Set, Optional, Tuple, Any
import heapq
from datetime import datetime, timedelta
import hashlib
import random
import string

class GroupingAlgorithm:
    """
    Anti-Cluster Distribution Algorithm
    
    Time Complexity: O(N)
    Space Complexity: O(N)
    """
    
    def bucket_players_by_club(self, players: List[Dict]) -> Dict[str, List[Dict]]:
        """Bucket players by club first"""
        club_buckets = {}
        
        for player in players:
            club_id = player['club_id']
            if club_id not in club_buckets:
                club_buckets[club_id] = []
            club_buckets[club_id].append(player)
        
        return club_buckets

    def calculate_group_penalty(self, group: List[Dict]) -> int:
        """Calculate penalty score for a group (same-club pairs)"""
        club_counts = {}
        penalty = 0
        
        for player in group:
            club_id = player['club_id']
            count = club_counts.get(club_id, 0)
            club_counts[club_id] = count + 1
            
            # Each additional player from same club adds to penalty
            if count > 0:
                penalty += count
        
        return penalty

    def distribute_players(self, club_buckets: Dict[str, List[Dict]], num_groups: int) -> List[Dict]:
        """Distribute players across groups using round-robin approach"""
        groups = []
        for i in range(num_groups):
            groups.append({
                'id': f'group-{i + 1}',
                'players': [],
                'club_distribution': {}
            })

        # Sort clubs by size (largest first) for better distribution
        sorted_clubs = sorted(club_buckets.items(), key=lambda x: len(x[1]), reverse=True)

        for club_id, club_players in sorted_clubs:
            # Distribute players from this club round-robin across groups
            for i, player in enumerate(club_players):
                target_group_index = i % num_groups
                target_group = groups[target_group_index]
                
                target_group['players'].append(player)
                
                # Update club distribution
                current_count = target_group['club_distribution'].get(club_id, 0)
                target_group['club_distribution'][club_id] = current_count + 1

        return groups

    def group_players(self, players: List[Dict], num_groups: int) -> Dict:
        """Main grouping function"""
        if num_groups <= 0:
            raise ValueError('Number of groups must be positive')
        
        if len(players) == 0:
            return {'groups': [], 'total_penalty': 0}

        # Step 1: Bucket players by club
        club_buckets = self.bucket_players_by_club(players)

        # Step 2: Distribute players across groups
        groups = self.distribute_players(club_buckets, num_groups)

        # Step 3: Calculate total penalty
        total_penalty = 0
        for group in groups:
            total_penalty += self.calculate_group_penalty(group['players'])

        return {'groups': groups, 'total_penalty': total_penalty}


class BacktrackingPairingAlgorithm:
    """
    Backtracking Pairing Algorithm (Same-Club Avoidance)
    
    Time Complexity: O(N!) in worst case, but typically much better due to pruning
    Space Complexity: O(N) for recursion stack
    """
    
    def __init__(self):
        self.best_result = None
        self.visited_states = set()

    def calculate_match_penalty(self, player1: Dict, player2: Dict) -> int:
        """Calculate penalty for a match (0 if different clubs, 1 if same club)"""
        return 1 if player1['club_id'] == player2['club_id'] else 0

    def generate_state_key(self, players: List[Dict]) -> str:
        """Generate state key for memoization"""
        sorted_ids = sorted([p['id'] for p in players])
        return ','.join(sorted_ids)

    def is_bye_player(self, player: Dict) -> bool:
        """Check if a player is a BYE dummy"""
        return player['id'] == 'BYE'

    def create_bye_player(self) -> Dict:
        """Create a BYE dummy player"""
        return {
            'id': 'BYE',
            'name': 'BYE',
            'phone': '',
            'age': 0,
            'club_id': 'BYE',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

    def find_optimal_pairing(self, players: List[Dict], current_matches: List[Dict] = None, 
                           current_penalty: int = 0, depth: int = 0) -> None:
        """Try to find optimal pairing using backtracking"""
        if current_matches is None:
            current_matches = []

        # Prune if current penalty already exceeds best found
        if self.best_result and current_penalty >= self.best_result['total_penalty']:
            return

        # Base case: all players paired
        if len(players) == 0:
            result = {
                'matches': current_matches.copy(),
                'total_penalty': current_penalty,
                'has_bye': False
            }

            # Check if any match involves BYE
            bye_match = next((m for m in current_matches if 
                             self.is_bye_player(m['player1']) or self.is_bye_player(m['player2'])), None)
            
            if bye_match:
                result['has_bye'] = True
                bye_player = bye_match['player2'] if self.is_bye_player(bye_match['player1']) else bye_match['player1']
                result['bye_player'] = bye_player
                # Remove BYE match from results
                result['matches'] = [m for m in current_matches if m != bye_match]

            # Update best result if better
            if not self.best_result or current_penalty < self.best_result['total_penalty']:
                self.best_result = result
            return

        # Memoization: skip if we've seen this state with better or equal penalty
        state_key = self.generate_state_key(players)
        if state_key in self.visited_states:
            return
        self.visited_states.add(state_key)

        # Fix first player and try pairing with others
        first_player = players[0]
        remaining_players = players[1:]

        # If only one player left, they get a BYE
        if len(remaining_players) == 0:
            bye_player = self.create_bye_player()
            match = {
                'player1': first_player,
                'player2': bye_player,
                'penalty': 0
            }

            self.find_optimal_pairing(
                [],
                current_matches + [match],
                current_penalty,
                depth + 1
            )
            return

        # Try pairing first player with each remaining player
        for i, second_player in enumerate(remaining_players):
            match_penalty = self.calculate_match_penalty(first_player, second_player)
            
            match = {
                'player1': first_player,
                'player2': second_player,
                'penalty': match_penalty
            }

            # Create new list of remaining players (remove both paired players)
            new_remaining = remaining_players[:i] + remaining_players[i+1:]

            # Recursively try to pair the rest
            self.find_optimal_pairing(
                new_remaining,
                current_matches + [match],
                current_penalty + match_penalty,
                depth + 1
            )

        # Clean up visited state for this branch
        self.visited_states.discard(state_key)

    def generate_pairings(self, players: List[Dict]) -> Dict:
        """Main pairing function"""
        if len(players) < 2:
            return {
                'matches': [],
                'total_penalty': 0,
                'has_bye': len(players) == 1,
                'bye_player': players[0] if players else None
            }

        # Reset state
        self.best_result = None
        self.visited_states.clear()

        # Sort players by club and name for consistent results
        sorted_players = sorted(players, key=lambda p: (p['club_id'], p['name']))

        # Start backtracking
        self.find_optimal_pairing(sorted_players)

        if not self.best_result:
            raise ValueError('Failed to generate pairings')

        return self.best_result


class RoundRobinRotationAlgorithm:
    """
    Round Robin Rotation Algorithm
    
    Time Complexity: O(n²)
    Space Complexity: O(n²)
    """
    
    def generate_round_robin(self, players: List[Dict]) -> Dict:
        """Generate round robin fixtures"""
        if len(players) < 2:
            return {
                'rounds': [],
                'total_penalty': 0,
                'num_rounds': 0,
                'has_odd_players': len(players) % 2 == 1
            }
        
        # Handle odd number of players by adding a BYE
        has_odd_players = len(players) % 2 == 1
        working_players = players.copy()
        
        if has_odd_players:
            bye_player = {
                'id': 'BYE',
                'name': 'BYE',
                'phone': '',
                'age': 0,
                'club_id': 'BYE',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            working_players.append(bye_player)
        
        num_players = len(working_players)
        num_rounds = num_players - 1
        matches_per_round = num_players // 2
        
        # Sort players for consistent seeding
        working_players = sorted(working_players, key=lambda p: (p['club_id'], p['name']))
        
        # Fix first player, rotate others
        fixed_player = working_players[0]
        rotating_players = working_players[1:]
        
        rounds = []
        total_penalty = 0
        
        for round_num in range(num_rounds):
            round_matches = []
            
            # Pair fixed player with first rotating player
            match1 = {
                'round': round_num + 1,
                'match': 1,
                'player1': fixed_player,
                'player2': rotating_players[0],
                'penalty': self._calculate_penalty(fixed_player, rotating_players[0])
            }
            
            if not self._is_bye_player(match1['player1']) and not self._is_bye_player(match1['player2']):
                round_matches.append(match1)
                total_penalty += match1['penalty']
            
            # Pair remaining rotating players
            for i in range(1, matches_per_round):
                player1 = rotating_players[i]
                player2 = rotating_players[num_players - 1 - i]
                
                match = {
                    'round': round_num + 1,
                    'match': i + 1,
                    'player1': player1,
                    'player2': player2,
                    'penalty': self._calculate_penalty(player1, player2)
                }
                
                if not self._is_bye_player(match['player1']) and not self._is_bye_player(match['player2']):
                    round_matches.append(match)
                    total_penalty += match['penalty']
            
            # Sort matches within round by penalty (different-club first)
            round_matches.sort(key=lambda m: m['penalty'])
            
            rounds.append(round_matches)
            
            # Rotate players (clockwise)
            if len(rotating_players) > 1:
                rotating_players = [rotating_players[-1]] + rotating_players[:-1]
        
        return {
            'rounds': rounds,
            'total_penalty': total_penalty,
            'num_rounds': num_rounds,
            'has_odd_players': has_odd_players
        }
    
    def _calculate_penalty(self, player1: Dict, player2: Dict) -> int:
        """Calculate penalty for a match"""
        return 1 if player1['club_id'] == player2['club_id'] else 0
    
    def _is_bye_player(self, player: Dict) -> bool:
        """Check if player is a BYE"""
        return player['id'] == 'BYE'


class KnockoutBracketEngine:
    """
    Knockout Bracket Engine
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    
    def generate_bracket(self, players: List[Dict], tournament_name: str) -> Dict:
        """Generate knockout bracket"""
        if len(players) < 2:
            raise ValueError('At least 2 players required for knockout tournament')
        
        # Sort players by club and name for seeding
        sorted_players = sorted(players, key=lambda p: (p['club_id'], p['name']))
        
        # Calculate power of 2
        num_players = len(sorted_players)
        next_power_of_2 = 1
        while next_power_of_2 < num_players:
            next_power_of_2 *= 2
        
        num_byes = next_power_of_2 - num_players
        num_rounds = next_power_of_2.bit_length() - 1
        
        # Create bracket
        bracket = self._create_bracket_structure(sorted_players, num_rounds, num_byes)
        
        return {
            'id': f'bracket-{datetime.now().timestamp()}',
            'name': tournament_name,
            'total_players': num_players,
            'rounds': num_rounds,
            'matches': bracket,
            'seeds': sorted_players,
            'is_complete': False,
            'winner': None
        }
    
    def _create_bracket_structure(self, players: List[Dict], num_rounds: int, num_byes: int) -> List[List[Dict]]:
        """Create bracket structure with matches"""
        matches = []
        
        # First round with byes
        first_round_matches = []
        remaining_players = players.copy()
        
        # Assign byes to top players
        bye_players = remaining_players[:num_byes] if num_byes > 0 else []
        playing_players = remaining_players[num_byes:] if num_byes > 0 else remaining_players
        
        # Create first round matches
        for i in range(0, len(playing_players), 2):
            if i + 1 < len(playing_players):
                match = {
                    'id': f'match-1-{len(first_round_matches) + 1}',
                    'round': 1,
                    'position': len(first_round_matches) + 1,
                    'player1': playing_players[i],
                    'player2': playing_players[i + 1],
                    'player1_seed': players.index(playing_players[i]) + 1,
                    'player2_seed': players.index(playing_players[i + 1]) + 1,
                    'winner': None,
                    'score1': None,
                    'score2': None,
                    'status': 'pending',
                    'bye': False
                }
                first_round_matches.append(match)
        
        # Add bye players as automatic winners
        for bye_player in bye_players:
            match = {
                'id': f'match-1-{len(first_round_matches) + 1}',
                'round': 1,
                'position': len(first_round_matches) + 1,
                'player1': bye_player,
                'player2': None,
                'player1_seed': players.index(bye_player) + 1,
                'player2_seed': None,
                'winner': bye_player,
                'score1': None,
                'score2': None,
                'status': 'completed',
                'bye': True
            }
            first_round_matches.append(match)
        
        matches.append(first_round_matches)
        
        # Create subsequent rounds
        for round_num in range(2, num_rounds + 1):
            round_matches = []
            num_matches_in_round = len(first_round_matches) // (2 ** (round_num - 2))
            
            for i in range(num_matches_in_round):
                match = {
                    'id': f'match-{round_num}-{i + 1}',
                    'round': round_num,
                    'position': i + 1,
                    'player1': None,
                    'player2': None,
                    'player1_seed': None,
                    'player2_seed': None,
                    'winner': None,
                    'score1': None,
                    'score2': None,
                    'status': 'pending',
                    'bye': False
                }
                round_matches.append(match)
            
            matches.append(round_matches)
        
        return matches


class SmartSchedulingEngine:
    """
    Smart Scheduling Engine using Min-Heap
    
    Time Complexity: O(M log C) where M = number of matches, C = number of courts
    Space Complexity: O(M + C)
    """
    
    def __init__(self, constraints: Dict = None):
        self.constraints = {
            'match_duration': 60,  # 1 hour default
            'minimum_rest_time': 30,  # 30 minutes default
            'buffer_time': 15,  # 15 minutes default
            'max_matches_per_day': 8,
            'working_hours_start': 8,
            'working_hours_end': 22,
            **(constraints or {})
        }
        self.courts_heap = []
        self.player_rest_map = {}

    def initialize_courts_heap(self, courts: List[Dict], start_time: datetime) -> None:
        """Initialize courts heap with available courts"""
        self.courts_heap = []
        for court in courts:
            heapq.heappush(self.courts_heap, (start_time, court))

    def get_earliest_available_court(self) -> Optional[Tuple[datetime, Dict]]:
        """Get earliest available court"""
        if not self.courts_heap:
            return None
        return self.courts_heap[0]

    def update_court_availability(self, court: Dict, match_end_time: datetime) -> None:
        """Update court availability after scheduling a match"""
        # Remove the old entry and add the new one
        for i, (time, existing_court) in enumerate(self.courts_heap):
            if existing_court['id'] == court['id']:
                self.courts_heap.pop(i)
                heapq.heapify(self.courts_heap)
                heapq.heappush(self.courts_heap, (match_end_time, court))
                break

    def is_player_available(self, player_id: str, proposed_time: datetime) -> bool:
        """Check if player is available for a match at given time"""
        rest_info = self.player_rest_map.get(player_id)
        if not rest_info:
            return True
        return proposed_time >= rest_info['next_available_time']

    def update_player_rest_info(self, player_id: str, match_end_time: datetime) -> None:
        """Update player rest information after scheduling a match"""
        next_available_time = match_end_time + timedelta(minutes=self.constraints['minimum_rest_time'])
        
        self.player_rest_map[player_id] = {
            'player_id': player_id,
            'last_match_end_time': match_end_time,
            'minimum_rest_time': self.constraints['minimum_rest_time'],
            'next_available_time': next_available_time
        }

    def is_within_working_hours(self, date: datetime) -> bool:
        """Check if proposed time is within working hours"""
        hour = date.hour
        return self.constraints['working_hours_start'] <= hour < self.constraints['working_hours_end']

    def adjust_to_working_hours(self, date: datetime) -> datetime:
        """Adjust time to be within working hours"""
        adjusted = date
        hour = adjusted.hour

        if hour < self.constraints['working_hours_start']:
            adjusted = adjusted.replace(hour=self.constraints['working_hours_start'], minute=0, second=0, microsecond=0)
        elif hour >= self.constraints['working_hours_end']:
            # Move to next day
            adjusted = adjusted + timedelta(days=1)
            adjusted = adjusted.replace(hour=self.constraints['working_hours_start'], minute=0, second=0, microsecond=0)

        return adjusted

    def calculate_earliest_start_time(self, court_time: datetime, player1_id: str, player2_id: str) -> datetime:
        """Calculate earliest possible start time for a match"""
        player1_ready_time = self.player_rest_map.get(player1_id, {}).get('next_available_time', court_time)
        player2_ready_time = self.player_rest_map.get(player2_id, {}).get('next_available_time', court_time)

        # Take the latest of all three times
        earliest_time = max(court_time, player1_ready_time, player2_ready_time)

        # Adjust to working hours
        return self.adjust_to_working_hours(earliest_time)

    def schedule_match(self, match: Dict, match_index: int, courts: List[Dict]) -> Optional[Dict]:
        """Schedule a single match"""
        if not self.courts_heap:
            raise ValueError('No courts available for scheduling')

        court_time, court = heapq.heappop(self.courts_heap)

        # Calculate earliest start time considering player rest
        earliest_start_time = self.calculate_earliest_start_time(
            court_time, match['player1']['id'], match['player2']['id']
        )

        scheduled_end_time = earliest_start_time + timedelta(minutes=self.constraints['match_duration'])

        # Create scheduled match
        scheduled_match = {
            'id': f'match-{match_index + 1}',
            'match': match,
            'court': court,
            'scheduled_start_time': earliest_start_time,
            'scheduled_end_time': scheduled_end_time,
            'status': 'scheduled'
        }

        # Update court availability
        self.update_court_availability(court, scheduled_end_time)

        # Update player rest information
        self.update_player_rest_info(match['player1']['id'], scheduled_end_time)
        self.update_player_rest_info(match['player2']['id'], scheduled_end_time)

        return scheduled_match

    def schedule_matches(self, matches: List[Dict], courts: List[Dict], 
                        start_time: datetime = None) -> Dict:
        """Main scheduling function"""
        if start_time is None:
            start_time = datetime.now()

        # Reset state
        self.player_rest_map.clear()
        self.initialize_courts_heap(courts, start_time)

        scheduled_matches = []
        conflicts = []
        rest_violations = []

        # Sort matches by priority (you can customize this logic)
        sorted_matches = sorted(matches, key=lambda m: (m['penalty'], m['player1']['name'], m['player2']['name']))

        # Schedule each match
        for i, match in enumerate(sorted_matches):
            try:
                scheduled_match = self.schedule_match(match, i, courts)
                if scheduled_match:
                    scheduled_matches.append(scheduled_match)
            except Exception as e:
                conflicts.append(f'Failed to schedule match {i + 1}: {str(e)}')

        # Calculate statistics
        total_schedule_time = 0
        if scheduled_matches:
            start_times = [m['scheduled_start_time'] for m in scheduled_matches]
            end_times = [m['scheduled_end_time'] for m in scheduled_matches]
            total_schedule_time = (max(end_times) - min(start_times)).total_seconds() / 60  # in minutes

        court_utilization = {}
        for court in courts:
            court_matches = [m for m in scheduled_matches if m['court']['id'] == court['id']]
            total_scheduled_time = sum(
                (m['scheduled_end_time'] - m['scheduled_start_time']).total_seconds() / 60
                for m in court_matches
            )
            
            if scheduled_matches:
                schedule_start = min(m['scheduled_start_time'] for m in scheduled_matches)
                schedule_end = max(m['scheduled_end_time'] for m in scheduled_matches)
                total_time = (schedule_end - schedule_start).total_seconds() / 60
                utilization = (total_scheduled_time / total_time) * 100 if total_time > 0 else 0
                court_utilization[court['id']] = utilization

        return {
            'scheduled_matches': scheduled_matches,
            'total_schedule_time': total_schedule_time,
            'court_utilization': court_utilization,
            'player_rest_violations': rest_violations,
            'scheduling_conflicts': conflicts
        }


class MatchCodeSecurity:
    """
    Match Code Security System
    
    Time Complexity: O(1) for generation and validation
    Space Complexity: O(1) for code storage
    """
    
    def __init__(self):
        self.CODE_EXPIRY_MINUTES = 60  # Code expires after 60 minutes
        self.CODE_LENGTH = 32  # Length of generated code
        self.SALT = 'XTHLETE_MATCH_SECURITY_2024'  # Salt for hashing
        
        # In-memory storage for active codes (in production, use Redis or database)
        self.active_codes = {}
        self.used_codes = set()

    def generate_hash(self, data: str) -> str:
        """Generate SHA-256 hash for match code"""
        return hashlib.sha256((data + self.SALT).encode()).hexdigest()

    def generate_random_code(self, length: int) -> str:
        """Generate random alphanumeric code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def create_match_data(self, match_id: str, player_ids: List[str], court_id: Optional[str], 
                         tournament_id: str) -> Dict:
        """Create match data payload"""
        now = int(datetime.now().timestamp())
        expires_at = now + (self.CODE_EXPIRY_MINUTES * 60)

        return {
            'match_id': match_id,
            'player_ids': sorted(player_ids),  # Sort for consistency
            'court_id': court_id,
            'timestamp': now,
            'tournament_id': tournament_id,
            'expires_at': expires_at
        }

    def generate_match_code(self, match_id: str, player_ids: List[str], court_id: Optional[str], 
                           tournament_id: str) -> Dict:
        """Generate secure match code"""
        if not match_id or not player_ids or not tournament_id:
            raise ValueError('Invalid parameters for match code generation')

        # Create match data
        match_data = self.create_match_data(match_id, player_ids, court_id, tournament_id)
        
        # Generate base code
        base_code = self.generate_random_code(self.CODE_LENGTH)
        
        # Create hash payload
        import json
        payload = json.dumps(match_data, sort_keys=True)
        hash_value = self.generate_hash(payload + base_code)
        
        # Combine base code with hash for final code
        final_code = f'{base_code}-{hash_value[:16]}'
        
        # Store in active codes
        self.active_codes[final_code] = match_data
        
        # Clean up expired codes
        self.cleanup_expired_codes()
        
        return {
            'code': final_code,
            'data': match_data,
            'expires_at': datetime.fromtimestamp(match_data['expires_at'])
        }

    def validate_match_code(self, code: str) -> Dict:
        """Validate match code"""
        if not code:
            return {'is_valid': False, 'error': 'No code provided'}

        # Check if code has been used
        if code in self.used_codes:
            return {'is_valid': False, 'error': 'Code has already been used'}

        # Check if code exists in active codes
        match_data = self.active_codes.get(code)
        if not match_data:
            return {'is_valid': False, 'error': 'Invalid or expired code'}

        # Check if code is expired
        now = int(datetime.now().timestamp())
        if now > match_data['expires_at']:
            del self.active_codes[code]
            return {'is_valid': False, 'error': 'Code has expired', 'is_expired': True}

        # Additional validation: verify hash integrity
        if '-' not in code:
            return {'is_valid': False, 'error': 'Invalid code format'}

        base_code, hash_part = code.split('-', 1)
        if not base_code or not hash_part:
            return {'is_valid': False, 'error': 'Invalid code format'}

        import json
        payload = json.dumps(match_data, sort_keys=True)
        expected_hash = self.generate_hash(payload + base_code)
        
        if expected_hash[:16] != hash_part:
            return {'is_valid': False, 'error': 'Code integrity check failed'}

        return {
            'is_valid': True,
            'match_data': match_data
        }

    def invalidate_code(self, code: str) -> bool:
        """Invalidate code after use"""
        validation = self.validate_match_code(code)
        if not validation['is_valid']:
            return False

        # Move from active to used codes
        if code in self.active_codes:
            del self.active_codes[code]
        self.used_codes.add(code)
        
        return True

    def cleanup_expired_codes(self) -> None:
        """Clean up expired codes"""
        now = int(datetime.now().timestamp())
        expired_codes = [
            code for code, data in self.active_codes.items()
            if now > data['expires_at']
        ]
        
        for code in expired_codes:
            del self.active_codes[code]

    def get_statistics(self) -> Dict:
        """Export code statistics"""
        return {
            'active_codes': len(self.active_codes),
            'used_codes': len(self.used_codes),
            'expiry_minutes': self.CODE_EXPIRY_MINUTES
        }
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict


class RoundRobinRotationAlgorithm:
    """
    Round Robin Rotation Algorithm with Dynamic Knockout and Tie-Breaking
    
    Time Complexity: O(n²)
    Space Complexity: O(n²)
    """
    
    def generate_round_robin(
        self, 
        players: List[Dict], 
        dynamic_knockout: bool = False,
        elimination_frequency: int = 0,
        elimination_count: int = 0,
        min_players: int = 4
    ) -> Dict:
        """
        Generate round robin fixtures with optional dynamic knockout
        
        Args:
            players: List of player dictionaries
            dynamic_knockout: Whether to enable dynamic knockout during round-robin
            elimination_frequency: Eliminate after every N rounds
            elimination_count: Number of players to eliminate each time
            min_players: Minimum players to continue tournament
            
        Returns:
            Dictionary with rounds, elimination info, and tournament statistics
        """
        if len(players) < 2:
            return {
                'rounds': [],
                'total_penalty': 0,
                'num_rounds': 0,
                'has_odd_players': len(players) % 2 == 1,
                'eliminated_players': [],
                'dynamic_knockout_enabled': dynamic_knockout
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
        
        # For dynamic knockout, we need to recalculate fixtures after eliminations
        if dynamic_knockout and elimination_frequency > 0 and elimination_count > 0:
            return self._generate_dynamic_knockout_rounds(
                working_players, 
                elimination_frequency, 
                elimination_count,
                min_players
            )
        
        # Original algorithm for non-dynamic knockout
        return self._generate_standard_round_robin(working_players)
    
    def _generate_standard_round_robin(self, players: List[Dict]) -> Dict:
        """Generate standard round-robin without dynamic knockout."""
        num_players = len(players)
        num_rounds = num_players - 1
        matches_per_round = num_players // 2
        
        # Sort players for consistent seeding
        working_players = sorted(players, key=lambda p: (p['club_id'], p['name']))
        
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
            'has_odd_players': len(players) % 2 == 1,
            'eliminated_players': [],
            'dynamic_knockout_enabled': False
        }
    
    def _generate_dynamic_knockout_rounds(
        self, 
        players: List[Dict], 
        elimination_frequency: int,
        elimination_count: int,
        min_players: int
    ) -> Dict:
        """Generate rounds with dynamic knockout functionality."""
        all_rounds = []
        eliminated_players = []
        current_players = players.copy()
        player_stats = self._initialize_player_stats(current_players)
        total_penalty = 0
        round_num = 1
        
        # Continue until we have the minimum number of players
        while len(current_players) > min_players:
            # Determine how many rounds to generate before next elimination
            rounds_to_generate = min(elimination_frequency, len(current_players) - 1)
            
            # Generate rounds for current set of players
            temp_result = self._generate_partial_round_robin(
                current_players, 
                start_round=round_num,
                num_rounds=rounds_to_generate
            )
            
            all_rounds.extend(temp_result['rounds'])
            total_penalty += temp_result['total_penalty']
            round_num += rounds_to_generate
            
            # Update player stats based on these rounds
            self._update_player_stats(player_stats, temp_result['rounds'])
            
            # Eliminate the worst performing players
            if len(current_players) > min_players:
                players_to_eliminate = min(elimination_count, len(current_players) - min_players)
                newly_eliminated = self._eliminate_players(
                    player_stats, 
                    players_to_eliminate
                )
                
                eliminated_players.extend(newly_eliminated)
                
                # Remove eliminated players from current list
                eliminated_ids = {p['id'] for p in newly_eliminated}
                current_players = [p for p in current_players if p['id'] not in eliminated_ids]
                
                # Handle BYE players for odd counts
                current_players = self._adjust_bye_players(current_players)
        
        # Generate final rounds with remaining players
        if len(current_players) >= 2:
            temp_result = self._generate_partial_round_robin(
                current_players, 
                start_round=round_num,
                num_rounds=len(current_players) - 1
            )
            all_rounds.extend(temp_result['rounds'])
            total_penalty += temp_result['total_penalty']
        
        return {
            'rounds': all_rounds,
            'total_penalty': total_penalty,
            'num_rounds': round_num - 1,
            'has_odd_players': len(current_players) % 2 == 1,
            'eliminated_players': eliminated_players,
            'dynamic_knockout_enabled': True,
            'final_players': current_players
        }
    
    def _generate_partial_round_robin(
        self, 
        players: List[Dict], 
        start_round: int = 1,
        num_rounds: Optional[int] = None
    ) -> Dict:
        """Generate a partial round-robin for the given players."""
        if len(players) < 2:
            return {
                'rounds': [],
                'total_penalty': 0,
                'num_rounds': 0
            }
        
        num_players = len(players)
        if num_rounds is None:
            num_rounds = num_players - 1
        else:
            num_rounds = min(num_rounds, num_players - 1)
            
        matches_per_round = num_players // 2
        
        # Sort players for consistent seeding
        sorted_players = sorted(players, key=lambda p: (p['club_id'], p['name']))
        
        # Fix first player, rotate others
        fixed_player = sorted_players[0]
        rotating_players = sorted_players[1:]
        
        rounds = []
        total_penalty = 0
        
        for round_offset in range(num_rounds):
            round_num = start_round + round_offset
            round_matches = []
            
            # Pair fixed player with first rotating player
            match1 = {
                'round': round_num,
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
                    'round': round_num,
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
            'num_rounds': num_rounds
        }
    
    def _adjust_bye_players(self, players: List[Dict]) -> List[Dict]:
        """Adjust BYE players based on current player count."""
        # If we have an odd number of players and no BYE, add one
        if len(players) % 2 == 1 and not any(p['id'] == 'BYE' for p in players):
            bye_player = {
                'id': 'BYE',
                'name': 'BYE',
                'phone': '',
                'age': 0,
                'club_id': 'BYE',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            players.append(bye_player)
        
        # If we have a BYE and now have an even number, remove the BYE
        if len(players) % 2 == 0 and any(p['id'] == 'BYE' for p in players):
            players = [p for p in players if p['id'] != 'BYE']
        
        return players
    
    def _initialize_player_stats(self, players: List[Dict]) -> Dict:
        """Initialize statistics tracking for all players."""
        stats = {}
        for player in players:
            if player['id'] != 'BYE':
                stats[player['id']] = {
                    'player': player,
                    'points': 0,
                    'played': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'scored': 0,
                    'conceded': 0,
                    'head_to_head': defaultdict(int),
                    'opponents': set()
                }
        return stats
    
    def _update_player_stats(
        self, 
        player_stats: Dict, 
        rounds: List[List[Dict]]
    ) -> None:
        """Update player statistics based on match results."""
        for round_matches in rounds:
            for m in round_matches:
                p1 = m['player1']
                p2 = m['player2']
                
                # Skip BYE matches
                if p1['id'] == 'BYE' or p2['id'] == 'BYE':
                    continue
                
                s1 = m.get('score1')
                s2 = m.get('score2')
                
                # If result not yet entered, skip
                if s1 is None or s2 is None:
                    continue
                
                st1 = player_stats[p1['id']]
                st2 = player_stats[p2['id']]
                
                # Track opponents
                st1['opponents'].add(p2['id'])
                st2['opponents'].add(p1['id'])
                
                st1['played'] += 1
                st2['played'] += 1
                st1['scored'] += s1
                st1['conceded'] += s2
                st2['scored'] += s2
                st2['conceded'] += s1
                
                if s1 > s2:
                    st1['wins'] += 1
                    st2['losses'] += 1
                    st1['points'] += 3
                    st2['points'] += 0
                    st1['head_to_head'][p2['id']] += 3
                    st2['head_to_head'][p1['id']] += 0
                elif s2 > s1:
                    st2['wins'] += 1
                    st1['losses'] += 1
                    st2['points'] += 3
                    st1['points'] += 0
                    st2['head_to_head'][p1['id']] += 3
                    st1['head_to_head'][p2['id']] += 0
                else:
                    # Draw
                    st1['draws'] += 1
                    st2['draws'] += 1
                    st1['points'] += 1
                    st2['points'] += 1
                    st1['head_to_head'][p2['id']] += 1
                    st2['head_to_head'][p1['id']] += 1
    
    def _eliminate_players(
        self, 
        player_stats: Dict, 
        count: int
    ) -> List[Dict]:
        """Eliminate the worst performing players using comprehensive tie-breaking."""
        # Convert to list and add score_diff
        standings_list = []
        for s in player_stats.values():
            s['score_diff'] = s['scored'] - s['conceded']
            standings_list.append(s)
        
        # Sort using comprehensive tie-breaking
        standings_list.sort(key=lambda s: self._get_tie_break_key(s, player_stats))
        
        # Return the bottom players
        return [s['player'] for s in standings_list[:count]]

    def _get_tie_break_key(
        self, 
        player_stat: Dict, 
        all_stats: Dict
    ) -> Tuple:
        """
        Generate a comprehensive tie-breaking key for sorting players.
        Returns a tuple that can be used for sorting (lower values are worse).
        """
        player = player_stat['player']
        
        # Primary criteria (negative for ascending sort)
        primary = (
            -player_stat['points'],      # Fewer points is worse
            -player_stat['score_diff'],  # Worse goal difference
            -player_stat['wins'],        # Fewer wins
            -player_stat['scored'],      # Fewer goals scored
            player_stat['conceded'],     # More goals conceded
        )
        
        # Secondary criteria for tied players
        secondary = self._get_head_to_head_tie_break(player_stat, all_stats)
        
        # Tertiary criteria
        tertiary = (player['name'],)  # Alphabetical order as last resort
        
        return primary + secondary + tertiary
    
    def _get_head_to_head_tie_break(
        self, 
        player_stat: Dict, 
        all_stats: Dict
    ) -> Tuple:
        """
        Calculate head-to-head tie-breaking for players with identical stats.
        """
        player_id = player_stat['player']['id']
        
        # Find players with identical primary stats
        tied_players = []
        for pid, stats in all_stats.items():
            if (pid != player_id and 
                stats['points'] == player_stat['points'] and
                (stats['scored'] - stats['conceded']) == player_stat['score_diff'] and
                stats['wins'] == player_stat['wins'] and
                stats['scored'] == player_stat['scored'] and
                stats['conceded'] == player_stat['conceded']):
                tied_players.append(pid)
        
        if not tied_players:
            return (0,)  # No ties, return neutral value
        
        # Calculate head-to-head record against tied opponents
        h2h_points = 0
        
        for opponent_id in tied_players:
            if opponent_id in player_stat['head_to_head']:
                h2h_points += player_stat['head_to_head'][opponent_id]
        
        # Return negative for ascending sort (fewer h2h points is worse)
        return (-h2h_points,)

    def _calculate_penalty(self, player1: Dict, player2: Dict) -> int:
        """Calculate penalty for a match (same-club = 1, otherwise 0)."""
        return 1 if player1['club_id'] == player2['club_id'] else 0

    def _is_bye_player(self, player: Dict) -> bool:
        """Check if player is a BYE."""
        return player['id'] == 'BYE'


def compute_standings(
    rounds: List[List[Dict]],
    win_points: int = 3,
    draw_points: int = 1,
    loss_points: int = 0
) -> List[Dict]:
    """
    Compute standings from played round-robin fixtures with comprehensive tie-breaking.
    
    Args:
        rounds: List of rounds with matches
        win_points: Points awarded for a win (default: 3)
        draw_points: Points awarded for a draw (default: 1)
        loss_points: Points awarded for a loss (default: 0)
        
    Returns:
        List of player standings sorted by tie-breaking criteria
    """
    standings: Dict[str, Dict] = {}

    def ensure_player(player: Dict):
        pid = player['id']
        if pid not in standings and pid != 'BYE':
            standings[pid] = {
                'player': player,
                'points': 0,
                'played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'scored': 0,
                'conceded': 0,
                'head_to_head': defaultdict(int),
                'opponents': set()
            }

    for round_matches in rounds:
        for m in round_matches:
            p1 = m['player1']
            p2 = m['player2']

            # Skip BYE matches
            if p1['id'] == 'BYE' or p2['id'] == 'BYE':
                continue

            ensure_player(p1)
            ensure_player(p2)

            s1 = m.get('score1')
            s2 = m.get('score2')

            # If result not yet entered, skip
            if s1 is None or s2 is None:
                continue

            st1 = standings[p1['id']]
            st2 = standings[p2['id']]

            # Track opponents
            st1['opponents'].add(p2['id'])
            st2['opponents'].add(p1['id'])

            st1['played'] += 1
            st2['played'] += 1
            st1['scored'] += s1
            st1['conceded'] += s2
            st2['scored'] += s2
            st2['conceded'] += s1

            if s1 > s2:
                st1['wins'] += 1
                st2['losses'] += 1
                st1['points'] += win_points
                st2['points'] += loss_points
                st1['head_to_head'][p2['id']] += win_points
                st2['head_to_head'][p1['id']] += loss_points
            elif s2 > s1:
                st2['wins'] += 1
                st1['losses'] += 1
                st2['points'] += win_points
                st1['points'] += loss_points
                st2['head_to_head'][p1['id']] += win_points
                st1['head_to_head'][p2['id']] += loss_points
            else:
                # Draw
                st1['draws'] += 1
                st2['draws'] += 1
                st1['points'] += draw_points
                st2['points'] += draw_points
                st1['head_to_head'][p2['id']] += draw_points
                st2['head_to_head'][p1['id']] += draw_points

    # Convert to list and add score_diff
    standings_list: List[Dict] = []
    for s in standings.values():
        s['score_diff'] = s['scored'] - s['conceded']
        standings_list.append(s)

    # Sort using comprehensive tie-breaking
    def get_sort_key(player_stat):
        # Primary criteria (negative for descending sort)
        primary = (
            -player_stat['points'],
            -player_stat['score_diff'],
            -player_stat['wins'],
            -player_stat['scored'],
            player_stat['conceded'],
        )
        
        # Head-to-head tie-breaking
        player_id = player_stat['player']['id']
        tied_players = []
        
        for other_id, other_stat in standings.items():
            if (other_id != player_id and 
                other_stat['points'] == player_stat['points'] and
                (other_stat['scored'] - other_stat['conceded']) == player_stat['score_diff'] and
                other_stat['wins'] == player_stat['wins'] and
                other_stat['scored'] == player_stat['scored'] and
                other_stat['conceded'] == player_stat['conceded']):
                tied_players.append(other_id)
        
        h2h_points = 0
        for opponent_id in tied_players:
            if opponent_id in player_stat['head_to_head']:
                h2h_points += player_stat['head_to_head'][opponent_id]
        
        # Tertiary criteria
        tertiary = (player_stat['player']['name'],)
        
        return primary + (-h2h_points,) + tertiary

    standings_list.sort(key=get_sort_key)

    # Add rank field
    for i, s in enumerate(standings_list, start=1):
        s['rank'] = i

    return standings_list


def pick_qualifiers(standings: List[Dict], num_qualifiers: int) -> List[Dict]:
    """
    Select top N players from the standings to advance to knockout.
    
    Args:
        standings: List of player standings
        num_qualifiers: Number of players to select
        
    Returns:
        List of top players who qualify for knockout
    """
    return standings[:num_qualifiers]


def generate_knockout_bracket(qualifiers: List[Dict]) -> List[Dict]:
    """
    Generate a knockout bracket based on qualifiers.
    
    Args:
        qualifiers: List of player standings sorted by rank
        
    Returns:
        List of knockout matches with high and low seed players
        
    Raises:
        ValueError: If number of qualifiers is not a power of 2
    """
    n = len(qualifiers)
    if n == 0 or (n & (n - 1)) != 0:
        raise ValueError("Number of qualifiers must be a power of 2 (e.g. 8, 16, 32).")

    matches: List[Dict] = []
    for i in range(n // 2):
        high_seed_player = qualifiers[i]['player']
        low_seed_player = qualifiers[n - 1 - i]['player']
        matches.append({
            'match': i + 1,
            'player_high_seed': high_seed_player,
            'player_low_seed': low_seed_player,
        })

    return matches
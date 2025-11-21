from typing import List, Dict
from datetime import datetime


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
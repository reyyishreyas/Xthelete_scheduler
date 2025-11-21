from typing import List, Dict
from datetime import datetime


class KnockoutBracketEngine:
    
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

from typing import List, Dict, Set, Optional
from datetime import datetime


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
        state_key = self.generate_state_key(players)
        if state_key in self.visited_states:
            return
        self.visited_states.add(state_key)
        first_player = players[0]
        remaining_players = players[1:]

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

        sorted_players = sorted(players, key=lambda p: (p['club_id'], p['name']))

        # Start backtracking
        self.find_optimal_pairing(sorted_players)

        if not self.best_result:
            raise ValueError('Failed to generate pairings')

        return self.best_result

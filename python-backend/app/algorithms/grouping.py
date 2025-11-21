from typing import List, Dict
import heapq
from datetime import datetime


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
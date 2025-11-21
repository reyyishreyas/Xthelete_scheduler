from typing import List, Dict, Optional, Tuple
import heapq
from datetime import datetime, timedelta


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
        # Remove old entry and add new one
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
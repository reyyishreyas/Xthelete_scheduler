from typing import List, Dict, Optional
import hashlib
import random
import string
from datetime import datetime


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
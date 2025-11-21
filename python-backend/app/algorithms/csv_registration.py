import pandas as pd
import io
import csv
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class CSVRegistrationService:
    """
    CSV Player Registration Service
    
    Handles bulk player registration from CSV files with:
    - Duplicate prevention
    - Automatic event registration
    - Data validation
    - Error reporting
    """
    
    def __init__(self):
        self.REQUIRED_COLUMNS = ['name', 'phone', 'age', 'club_code']
        self.OPTIONAL_COLUMNS = ['email', 'address', 'emergency_contact']
        self.VALID_CATEGORIES = ['U15', 'U17', 'adults', 'open']
        self.VALID_EVENT_TYPES = ['singles', 'doubles', 'mixed_doubles']
        
    def validate_csv_structure(self, csv_content: str) -> Dict:
        """Validate CSV structure and return validation result"""
        try:
            # Try to parse CSV
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Check required columns
            missing_columns = []
            for col in self.REQUIRED_COLUMNS:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                return {
                    'valid': False,
                    'error': f'Missing required columns: {", ".join(missing_columns)}',
                    'required_columns': self.REQUIRED_COLUMNS,
                    'found_columns': list(df.columns)
                }
            
            # Check if DataFrame is empty
            if df.empty:
                return {
                    'valid': False,
                    'error': 'CSV file is empty',
                    'row_count': 0
                }
            
            return {
                'valid': True,
                'row_count': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict('records')
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Invalid CSV format: {str(e)}'
            }
    
    def parse_csv_data(self, csv_content: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse CSV and return valid rows with errors"""
        try:
            df = pd.read_csv(io.StringIO(csv_content))
            
            valid_rows = []
            error_rows = []
            
            for index, row in df.iterrows():
                row_dict = row.to_dict()
                validation_error = self.validate_player_row(row_dict, index + 1)
                
                if validation_error:
                    error_rows.append({
                        'row_number': index + 1,
                        'data': row_dict,
                        'error': validation_error
                    })
                else:
                    valid_rows.append(row_dict)
            
            return valid_rows, error_rows
            
        except Exception as e:
            return [], [{
                'row_number': 0,
                'data': {},
                'error': f'CSV parsing error: {str(e)}'
            }]
    
    def validate_player_row(self, row: Dict, row_number: int) -> Optional[str]:
        """Validate individual player row"""
        errors = []
        
        # Name validation
        name = str(row.get('name', '')).strip()
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters')
        elif len(name) > 100:
            errors.append('Name must be less than 100 characters')
        
        # Phone validation
        phone = str(row.get('phone', '')).strip()
        if not phone or len(phone) < 10:
            errors.append('Phone must be at least 10 characters')
        
        # Age validation
        try:
            age = int(row.get('age', 0))
            if age < 5 or age > 100:
                errors.append('Age must be between 5 and 100')
        except ValueError:
            errors.append('Age must be a valid number')
        
        # Club code validation
        club_code = str(row.get('club_code', '')).strip()
        if not club_code or len(club_code) < 2:
            errors.append('Club code must be at least 2 characters')
        
        # Optional email validation
        email = str(row.get('email', '')).strip()
        if email and '@' not in email:
            errors.append('Invalid email format')
        
        return '; '.join(errors) if errors else None
    
    def prepare_player_data(self, valid_rows: List[Dict], club_id: str) -> List[Dict]:
        """Prepare player data for database insertion"""
        prepared_players = []
        
        for row in valid_rows:
            player_data = {
                'name': str(row['name']).strip(),
                'phone': str(row['phone']).strip(),
                'age': int(row['age']),
                'club_id': club_id,
                'email': str(row.get('email', '')).strip(),
                'address': str(row.get('address', '')).strip(),
                'emergency_contact': str(row.get('emergency_contact', '')).strip(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            prepared_players.append(player_data)
        
        return prepared_players
    
    def check_existing_players(self, players: List[Dict], existing_players: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Check for duplicate players and separate new vs existing"""
        new_players = []
        duplicate_players = []
        
        # Create lookup for existing players
        existing_lookup = {}
        for player in existing_players:
            key = f"{player['name'].lower()}_{player['phone']}"
            existing_lookup[key] = player
        
        for player in players:
            key = f"{player['name'].lower()}_{player['phone']}"
            
            if key in existing_lookup:
                duplicate_players.append({
                    'player': player,
                    'existing_player': existing_lookup[key],
                    'duplicate_type': 'name_and_phone'
                })
            else:
                # Check phone-only duplicates
                phone_exists = any(p['phone'] == player['phone'] for p in existing_players)
                if phone_exists:
                    duplicate_players.append({
                        'player': player,
                        'duplicate_type': 'phone_only'
                    })
                else:
                    new_players.append(player)
        
        return new_players, duplicate_players
    
    def register_players_to_events(self, players: List[Dict], event_ids: List[str]) -> List[Dict]:
        """Prepare event registrations for players"""
        registrations = []
        
        for player in players:
            for event_id in event_ids:
                registration = {
                    'player_id': player['id'],
                    'event_id': event_id,
                    'created_at': datetime.now().isoformat()
                }
                registrations.append(registration)
        
        return registrations
    
    def generate_registration_summary(self, csv_data: Dict, registration_result: Dict) -> Dict:
        """Generate comprehensive registration summary"""
        return {
            'csv_info': {
                'total_rows': csv_data.get('row_count', 0),
                'valid_rows': len(registration_result.get('valid_players', [])),
                'error_rows': len(registration_result.get('error_rows', []))
            },
            'registration_result': {
                'new_players_registered': len(registration_result.get('new_players', [])),
                'duplicate_players_found': len(registration_result.get('duplicate_players', [])),
                'event_registrations_created': len(registration_result.get('event_registrations', [])),
                'clubs_processed': len(registration_result.get('clubs', []))
            },
            'errors': registration_result.get('errors', []),
            'warnings': registration_result.get('warnings', []),
            'success': len(registration_result.get('errors', [])) == 0
        }
    
    def export_registration_template(self) -> str:
        """Generate CSV template for clubs"""
        template_data = {
            'name': ['John Doe', 'Jane Smith'],
            'phone': ['+1234567890', '+0987654321'],
            'age': [25, 28],
            'club_code': ['TCA', 'TCB'],
            'email': ['john@example.com', 'jane@example.com'],
            'address': ['123 Main St', '456 Oak Ave'],
            'emergency_contact': ['+1122334455', '+9988776655']
        }
        
        df = pd.DataFrame(template_data)
        return df.to_csv(index=False)
    
    def validate_event_registrations(self, player_id: str, event_ids: List[str], 
                                 existing_registrations: List[Dict]) -> Dict:
        """Validate event registrations for a player"""
        existing_player_regs = [r for r in existing_registrations if r['player_id'] == player_id]
        existing_event_ids = {r['event_id'] for r in existing_player_regs}
        
        new_registrations = []
        duplicate_registrations = []
        
        for event_id in event_ids:
            if event_id in existing_event_ids:
                duplicate_registrations.append({
                    'player_id': player_id,
                    'event_id': event_id,
                    'reason': 'Already registered for this event'
                })
            else:
                new_registrations.append({
                    'player_id': player_id,
                    'event_id': event_id
                })
        
        return {
            'new_registrations': new_registrations,
            'duplicate_registrations': duplicate_registrations
        }
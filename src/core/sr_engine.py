"""
Safety Rating Engine for F1 Telemetry
Implements iRacing-style safety rating with moving average over corners
"""
from collections import deque
from typing import Dict, Any
from ..adapters.base_adapter import RaceState


class SREngine:
    """
    Safety Rating calculation engine
    
    Uses a moving average of incident points over the last N corners
    - 1x (off-track): 1 point
    - 2x (spin): 2 points
    - 4x (collision): 4 points
    
    SR = 100 - (average_incidents_per_corner * multiplier)
    """
    
    def __init__(self, window_size: int = 100, sr_multiplier: float = 10.0):
        """
        Initialize SR engine
        
        Args:
            window_size: Number of corners to track (moving average)
            sr_multiplier: Multiplier for incident impact on SR
        """
        self.window_size = window_size
        self.sr_multiplier = sr_multiplier
        
        # Incident tracking
        self.corner_incidents: deque = deque(maxlen=window_size)  # Incident points per corner
        self.current_sr = 100.0
        
        # State tracking
        self.last_lap_number = 0
        self.last_off_track_state = False
        self.last_damage_values = {
            'front_left': 0.0,
            'front_right': 0.0,
            'rear_left': 0.0,
            'rear_right': 0.0
        }
        
        # Session statistics
        self.session_incidents = {
            '1x': 0,
            '2x': 0,
            '4x': 0
        }
        self.corners_completed = 0
        self.current_corner_incidents = 0
        
        # Incident detection thresholds
        self.DAMAGE_THRESHOLD = 5.0  # % damage to trigger collision
        self.SPIN_DETECTION_ENABLED = False  # TODO: Implement via gyro data
    
    def process_telemetry(self, race_state: RaceState) -> Dict[str, Any]:
        """
        Process telemetry and update SR
        
        Args:
            race_state: Current race state from adapter
            
        Returns:
            Dict with current SR stats
        """
        # Detect lap change (new corner)
        if race_state.current_lap != self.last_lap_number and race_state.current_lap > 0:
            self._complete_corner()
            self.last_lap_number = race_state.current_lap
        
        # Detect off-track (1x)
        if race_state.is_off_track and not self.last_off_track_state:
            self._add_incident('1x')
        self.last_off_track_state = race_state.is_off_track
        
        # Detect collision (4x) via damage increase
        damage_change = self._calculate_damage_change(race_state)
        if damage_change > self.DAMAGE_THRESHOLD:
            self._add_incident('4x')
        
        # Update damage tracking
        self._update_damage_state(race_state)
        
        # Calculate current SR
        self._update_sr()
        
        return self.get_stats()
    
    def _complete_corner(self):
        """Mark a corner as completed and update moving average"""
        # Add current corner's incidents to the window
        self.corner_incidents.append(self.current_corner_incidents)
        self.corners_completed += 1
        
        # Reset for next corner
        self.current_corner_incidents = 0
    
    def _add_incident(self, incident_type: str):
        """
        Add an incident to current corner
        
        Args:
            incident_type: '1x', '2x', or '4x'
        """
        incident_value = int(incident_type[0])  # Extract number from '1x', '2x', '4x'
        self.current_corner_incidents += incident_value
        self.session_incidents[incident_type] += 1
        
        print(f"[SR Engine] Incident detected: {incident_type} (Total this corner: {self.current_corner_incidents})")
    
    def _calculate_damage_change(self, race_state: RaceState) -> float:
        """Calculate total damage increase since last check"""
        fl_change = max(0, race_state.front_left_damage - self.last_damage_values['front_left'])
        fr_change = max(0, race_state.front_right_damage - self.last_damage_values['front_right'])
        rl_change = max(0, race_state.rear_left_damage - self.last_damage_values['rear_left'])
        rr_change = max(0, race_state.rear_right_damage - self.last_damage_values['rear_right'])
        
        return fl_change + fr_change + rl_change + rr_change
    
    def _update_damage_state(self, race_state: RaceState):
        """Update tracked damage values"""
        self.last_damage_values['front_left'] = race_state.front_left_damage
        self.last_damage_values['front_right'] = race_state.front_right_damage
        self.last_damage_values['rear_left'] = race_state.rear_left_damage
        self.last_damage_values['rear_right'] = race_state.rear_right_damage
    
    def _update_sr(self):
        """Recalculate Safety Rating based on moving average"""
        if not self.corner_incidents:
            self.current_sr = 100.0
            return
        
        # Calculate average incidents per corner
        total_incidents = sum(self.corner_incidents)
        avg_incidents = total_incidents / len(self.corner_incidents)
        
        # SR = 100 - (average * multiplier)
        # Clamp between 0 and 100
        self.current_sr = max(0.0, min(100.0, 100.0 - (avg_incidents * self.sr_multiplier)))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current SR statistics"""
        total_incidents = sum(self.session_incidents.values())
        
        return {
            'current_sr': round(self.current_sr, 2),
            'corners_completed': self.corners_completed,
            'total_incidents': total_incidents,
            'incidents_1x': self.session_incidents['1x'],
            'incidents_2x': self.session_incidents['2x'],
            'incidents_4x': self.session_incidents['4x'],
            'incidents_in_window': sum(self.corner_incidents),
            'avg_incidents_per_corner': round(sum(self.corner_incidents) / max(1, len(self.corner_incidents)), 3)
        }
    
    def reset_session(self):
        """Reset SR engine for new session"""
        # Keep the corner history for SR calculation
        # Only reset session-specific stats
        self.session_incidents = {'1x': 0, '2x': 0, '4x': 0}
        self.corners_completed = 0
        self.current_corner_incidents = 0
        self.last_lap_number = 0
        self.last_off_track_state = False
        
        print("[SR Engine] Session reset")
    
    def set_sr(self, sr_value: float):
        """Manually set SR (e.g., loading from database)"""
        self.current_sr = max(0.0, min(100.0, sr_value))
    
    def calculate_cpi(self, total_corners: int) -> float:
        """
        Calculate Corners Per Incident (CPI)
        
        Args:
            total_corners: Total corners driven in the session
            
        Returns:
            CPI value
        """
        total_incidents = sum(self.session_incidents.values())
        if total_incidents == 0:
            return float('inf')  # No incidents = infinite CPI
        return round(total_corners / total_incidents, 2)

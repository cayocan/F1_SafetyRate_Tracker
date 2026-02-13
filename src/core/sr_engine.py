"""
Safety Rating Engine for F1 Telemetry
Implements iRacing-style safety rating with moving average over corners
"""
from collections import deque
from typing import Dict, Any
from ..adapters.base_adapter import RaceState


class SREngine:
    """
    Safety Rating calculation engine - iRacing style
    
    Uses a moving average of incident points over the last N corners
    - 1x (off-track): 1 point
    - 2x (spin): 2 points
    - 4x (collision): 4 points
    
    SR Scale: 2.50 to 7.99 (iRacing system)
    Initial SR: 2.50 (Rookie)
    
    License Classes:
    - Rookie: 2.50-2.99
    - D: 3.00-3.99
    - C: 4.00-4.99
    - B: 5.00-5.99
    - A: 6.00-6.99
    - SS: 7.00-7.99
    
    Boundary Bonus: When crossing integer boundaries (e.g., 2.99→3.00),
    system adds ~0.40 bonus to prevent "ping-ponging" between classes.
    """
    
    # Class boundaries and bonus system
    BOUNDARY_BONUS = 0.40
    MIN_SR = 2.50
    MAX_SR = 7.99
    
    def __init__(self, window_size: int = 100, sr_multiplier: float = 0.05):
        """
        Initialize SR engine
        
        Args:
            window_size: Number of corners to track (moving average)
            sr_multiplier: Multiplier for incident impact on SR (iRacing style)
                          Default 0.05 for gradual progression like iRacing
        """
        self.window_size = window_size
        self.sr_multiplier = sr_multiplier
        
        # Incident tracking
        self.corner_incidents: deque = deque(maxlen=window_size)  # Incident points per corner
        self.current_sr = 2.50  # iRacing initial SR (Rookie)
        self.last_sr = 2.50  # Track last SR for boundary detection
        
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
        """Recalculate Safety Rating based on moving average (iRacing style)"""
        if not self.corner_incidents:
            self.current_sr = self.MIN_SR  # Default to Rookie
            return
        
        # Save last SR for boundary detection
        old_sr = self.current_sr
        
        # Calculate CPI (Corners Per Incident) - iRacing style
        # Higher CPI = cleaner driving = SR increases
        # Lower CPI = more incidents = SR decreases
        total_incidents = sum(self.corner_incidents)
        corners_tracked = len(self.corner_incidents)
        
        if total_incidents == 0:
            # Perfect driving - use a high CPI value
            current_cpi = 100.0  # Effectively infinite safety
        else:
            current_cpi = corners_tracked / total_incidents
        
        # Target CPI for maintaining SR (iRacing benchmark)
        # ~25-40 CPI is considered "safe" driving in iRacing
        target_cpi = 30.0
        
        # Calculate incremental SR change based on performance
        # If current_cpi > target_cpi: good performance, SR goes up
        # If current_cpi < target_cpi: poor performance, SR goes down
        cpi_ratio = current_cpi / target_cpi
        
        # SR delta scales with how far from target
        # sr_multiplier controls how fast SR changes per update
        sr_delta = (cpi_ratio - 1.0) * self.sr_multiplier
        
        # Apply incremental change to current SR (not to a fixed base!)
        new_sr = old_sr + sr_delta
        
        # Clamp between MIN_SR and MAX_SR
        new_sr = max(self.MIN_SR, min(self.MAX_SR, new_sr))
        
        # Apply boundary bonus (iRacing system)
        new_sr = self._apply_boundary_bonus(old_sr, new_sr)
        
        self.current_sr = new_sr
        self.last_sr = old_sr
    
    def _apply_boundary_bonus(self, old_sr: float, new_sr: float) -> float:
        """Apply iRacing-style boundary bonus when crossing integer thresholds
        
        When SR crosses an integer boundary (e.g., 2.99→3.00 or 3.01→2.99),
        add/subtract 0.40 bonus to prevent "ping-ponging" between classes.
        
        Args:
            old_sr: Previous SR value
            new_sr: New calculated SR value
            
        Returns:
            Adjusted SR with boundary bonus applied
        """
        old_floor = int(old_sr)
        new_floor = int(new_sr)
        
        # Check if we crossed an integer boundary
        if old_floor != new_floor:
            if new_sr > old_sr:
                # Moving up: crossed boundary upward (e.g., 2.99 → 3.02)
                # Add bonus to push further into new class
                new_sr += self.BOUNDARY_BONUS
                print(f"[SR] Boundary crossed UP! {old_sr:.2f} → {new_sr:.2f} (bonus: +{self.BOUNDARY_BONUS})")
            else:
                # Moving down: crossed boundary downward (e.g., 3.01 → 2.98)
                # Subtract bonus to push further into lower class
                new_sr -= self.BOUNDARY_BONUS
                print(f"[SR] Boundary crossed DOWN! {old_sr:.2f} → {new_sr:.2f} (penalty: -{self.BOUNDARY_BONUS})")
            
            # Still clamp to valid range
            new_sr = max(self.MIN_SR, min(self.MAX_SR, new_sr))
        
        return new_sr
    
    def get_license_class(self, sr: float = None) -> tuple[str, str]:
        """Get license class and color based on SR (iRacing system)
        
        Args:
            sr: Safety Rating (uses current_sr if None)
            
        Returns:
            Tuple of (class_name, color)
        """
        if sr is None:
            sr = self.current_sr
        
        if sr >= 7.0:
            return ('SS', '#FFD700')  # Gold - Super Safety
        elif sr >= 6.0:
            return ('A', '#0066FF')  # Blue
        elif sr >= 5.0:
            return ('B', '#00AA00')  # Green
        elif sr >= 4.0:
            return ('C', '#FFAA00')  # Orange
        elif sr >= 3.0:
            return ('D', '#FF0000')  # Red
        else:
            return ('Rookie', '#888888')  # Gray
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current SR statistics"""
        total_incidents = sum(self.session_incidents.values())
        license_class, license_color = self.get_license_class()
        
        return {
            'current_sr': round(self.current_sr, 2),
            'license_class': license_class,
            'license_color': license_color,
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
        # Handle legacy values (0-100 range) by converting to new scale
        if sr_value > self.MAX_SR:
            # Legacy 0-100 scale, convert to 2.50-7.99
            # 100 -> 7.99, 50 -> 5.25, 0 -> 2.50
            normalized = sr_value / 100.0  # 0.0 to 1.0
            sr_value = self.MIN_SR + (normalized * (self.MAX_SR - self.MIN_SR))
        
        self.current_sr = max(self.MIN_SR, min(self.MAX_SR, sr_value))
        self.last_sr = self.current_sr
    
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

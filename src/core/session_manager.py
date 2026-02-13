"""
Session Manager for F1 Safety Rating System
Handles race session lifecycle detection and triggers save events
"""
from typing import Optional, Callable
from enum import Enum
from ..adapters.base_adapter import RaceState


class SessionState(Enum):
    """Race session states"""
    IDLE = "idle"
    QUALIFYING = "qualifying"
    PRACTICE = "practice"
    RACE_STARTING = "race_starting"
    RACE_ACTIVE = "race_active"
    RACE_ENDING = "race_ending"
    RACE_FINISHED = "race_finished"


class SessionManager:
    """
    Manages F1 race session lifecycle and transitions
    
    Session Detection Rules:
    - START: m_sessionType == 10 (Race) AND m_sessionTime > 0
    - END: m_sessionType changes OR m_gamePaused for extended period OR Result packet
    """
    
    def __init__(self, 
                 on_race_start: Optional[Callable[[str, int, float], None]] = None,
                 on_race_end: Optional[Callable[[str, float], None]] = None):
        """
        Initialize session manager with event callbacks
        
        Args:
            on_race_start: Callback(session_uid, track_id, start_sr) when race starts
            on_race_end: Callback(session_uid, end_sr) when race ends
        """
        self.current_state = SessionState.IDLE
        self.active_session_uid: Optional[str] = None
        self.active_track_id: Optional[int] = None
        self.last_session_type: Optional[int] = None
        self.race_start_time: Optional[float] = None
        self.pause_start_time: Optional[float] = None
        
        # Callbacks
        self.on_race_start = on_race_start
        self.on_race_end = on_race_end
        
        # Configuration
        self.PAUSE_THRESHOLD = 30.0  # Seconds of pause before considering race ended
        self.MIN_RACE_DURATION = 60.0  # Minimum race time to consider valid (1 minute)
    
    def process_telemetry(self, race_state: RaceState):
        """
        Process incoming telemetry and detect session transitions
        
        Args:
            race_state: Current race state from telemetry
        """
        current_session_type = race_state.session_type
        session_time = race_state.session_time
        session_uid = str(race_state.session_uid)
        track_id = race_state.track_id
        is_paused = race_state.game_paused
        
        # Detect race start
        if self._should_start_race(current_session_type, session_time, session_uid):
            self._start_race(session_uid, track_id, session_time)
        
        # Detect race end
        elif self._should_end_race(current_session_type, session_uid, is_paused, 
                                   race_state.timestamp):
            self._end_race(session_uid, session_time)
        
        # Update pause tracking
        if self.current_state == SessionState.RACE_ACTIVE:
            if is_paused:
                if self.pause_start_time is None:
                    self.pause_start_time = race_state.timestamp
            else:
                self.pause_start_time = None
        
        # Track session type changes
        self.last_session_type = current_session_type
    
    def _should_start_race(self, session_type: int, session_time: float, 
                          session_uid: str) -> bool:
        """
        Determine if a race session should be started
        
        Conditions:
        1. Current state is IDLE or non-race
        2. Session type is 10 (Race)
        3. Session time > 0 (race has begun)
        4. Not already tracking this session
        """
        is_race_type = session_type == 10
        has_started = session_time > 0
        is_new_session = (self.active_session_uid != session_uid)
        is_not_racing = self.current_state not in [SessionState.RACE_ACTIVE, 
                                                    SessionState.RACE_STARTING]
        
        return is_race_type and has_started and is_new_session and is_not_racing
    
    def _should_end_race(self, session_type: int, session_uid: str, 
                        is_paused: bool, current_timestamp: float) -> bool:
        """
        Determine if the current race should be ended
        
        Conditions:
        1. Currently in an active race
        2. Session type changed from Race (10) to something else, OR
        3. Game has been paused for more than PAUSE_THRESHOLD seconds, OR
        4. Session UID changed (new session started)
        """
        if self.current_state != SessionState.RACE_ACTIVE:
            return False
        
        # Session type changed away from Race
        if session_type != 10 and self.last_session_type == 10:
            return True
        
        # Different session UID (shouldn't happen, but safety check)
        if session_uid != self.active_session_uid:
            return True
        
        # Extended pause
        if is_paused and self.pause_start_time is not None:
            pause_duration = current_timestamp - self.pause_start_time
            if pause_duration > self.PAUSE_THRESHOLD:
                return True
        
        return False
    
    def _start_race(self, session_uid: str, track_id: int, session_time: float):
        """
        Start tracking a new race session
        
        Args:
            session_uid: Unique session identifier
            track_id: Track being raced on
            session_time: Game session time
        """
        self.current_state = SessionState.RACE_ACTIVE
        self.active_session_uid = session_uid
        self.active_track_id = track_id
        self.race_start_time = session_time
        self.pause_start_time = None
        
        print(f"[SessionManager] Race started - Session: {session_uid}, Track: {track_id}")
        
        # Trigger callback
        if self.on_race_start:
            # Note: start_sr should be retrieved from SR engine
            # For now, we'll let the callback handler get it
            self.on_race_start(session_uid, track_id, 0.0)
    
    def _end_race(self, session_uid: str, session_time: float):
        """
        End the current race session
        
        Args:
            session_uid: Session identifier
            session_time: Final game session time
        """
        # Validate race duration
        if self.race_start_time is not None:
            race_duration = session_time - self.race_start_time
            if race_duration < self.MIN_RACE_DURATION:
                print(f"[SessionManager] Race too short ({race_duration}s), not saving")
                self._reset()
                return
        
        print(f"[SessionManager] Race ended - Session: {session_uid}")
        
        # Trigger callback
        if self.on_race_end:
            # Note: end_sr should be retrieved from SR engine
            self.on_race_end(session_uid, 0.0)
        
        self._reset()
    
    def _reset(self):
        """Reset session tracking state"""
        self.current_state = SessionState.IDLE
        self.active_session_uid = None
        self.active_track_id = None
        self.race_start_time = None
        self.pause_start_time = None
    
    def force_end_current_session(self):
        """Manually end the current session (e.g., on application shutdown)"""
        if self.current_state == SessionState.RACE_ACTIVE and self.active_session_uid:
            print("[SessionManager] Force ending current session")
            if self.on_race_end:
                self.on_race_end(self.active_session_uid, 0.0)
            self._reset()
    
    def is_race_active(self) -> bool:
        """Check if a race is currently active"""
        return self.current_state == SessionState.RACE_ACTIVE
    
    def get_current_session_uid(self) -> Optional[str]:
        """Get the UID of the currently active session"""
        return self.active_session_uid
    
    def get_current_track_id(self) -> Optional[int]:
        """Get the track ID of the currently active session"""
        return self.active_track_id

"""
Base Adapter Interface for F1 Telemetry Games
Defines the contract that all game-specific adapters must follow.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class RaceState:
    """Unified telemetry state across all F1 games"""
    # Session Info
    session_uid: int
    session_type: int  # 10 = Race, 11 = Time Trial, etc.
    session_time: float
    game_paused: bool
    
    # Track Info
    track_id: int
    
    # Lap Data
    current_lap: int
    is_off_track: bool
    
    # Damage/Collision Data
    front_left_damage: float
    front_right_damage: float
    rear_left_damage: float
    rear_right_damage: float
    
    # Telemetry timestamp
    timestamp: float


class BaseAdapter(ABC):
    """Abstract base class for telemetry adapters"""
    
    @abstractmethod
    def parse_packet(self, data: bytes) -> Optional[RaceState]:
        """
        Parse raw UDP packet into RaceState
        
        Args:
            data: Raw bytes from UDP socket
            
        Returns:
            RaceState object or None if packet should be ignored
        """
        pass
    
    @abstractmethod
    def get_game_version(self) -> str:
        """Return the game version this adapter supports"""
        pass

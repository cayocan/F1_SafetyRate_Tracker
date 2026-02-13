"""
F1 2019 Telemetry Adapter
Handles binary packet parsing for F1 2019 UDP telemetry (Port 20777)
Focus: Packet ID 1 (Session), ID 2 (Lap Data), ID 10 (Car Damage)
"""
import struct
import time
from typing import Optional
from .base_adapter import BaseAdapter, RaceState


class F12019Adapter(BaseAdapter):
    """Adapter for F1 2019 telemetry protocol"""
    
    def __init__(self):
        self.last_race_state = None
        
    def get_game_version(self) -> str:
        return "F1 2019"
    
    def parse_packet(self, data: bytes) -> Optional[RaceState]:
        """
        Parse F1 2019 UDP packet
        
        Packet structure starts with a header:
        - packetFormat (uint16)
        - gameMajorVersion (uint8)
        - gameMinorVersion (uint8)
        - packetVersion (uint8)
        - packetId (uint8)
        - sessionUID (uint64)
        - sessionTime (float)
        - frameIdentifier (uint32)
        - playerCarIndex (uint8)
        """
        if len(data) < 24:  # Minimum header size
            return None
        
        try:
            # Parse header (first 24 bytes)
            header = struct.unpack('<HBBBBQfIB', data[:24])
            # packet_format = header[0]  # Currently unused
            packet_id = header[4]
            session_uid = header[5]
            session_time = header[6]
            player_car_index = header[8]
            
            # Route to specific parser based on packet ID
            if packet_id == 1:
                # Session packet
                return self._parse_session_packet(data, session_uid, session_time, player_car_index)
            elif packet_id == 2:
                # Lap Data packet
                return self._parse_lap_data_packet(data, session_uid, session_time, player_car_index)
            elif packet_id == 6:
                # Car Damage packet
                return self._parse_car_damage_packet(data, session_uid, session_time, player_car_index)
            else:
                return None
                
        except struct.error:
            return None
    
    def _parse_session_packet(self, data: bytes, session_uid: int, session_time: float, player_index: int) -> Optional[RaceState]:
        """
        Parse Session Data Packet (ID 1)
        Offset 24: weather, trackTemperature, airTemperature, etc.
        Offset 149: m_sessionTimeLeft (uint16)
        Offset 151: m_sessionDuration (uint16)
        Offset 153: m_pitSpeedLimit (uint8)
        Offset 154: m_gamePaused (uint8)
        Offset 155: m_isSpectating (uint8)
        Offset 156: m_spectatorCarIndex (uint8)
        Offset 157: m_sliProNativeSupport (uint8)
        Offset 158: m_numMarshalZones (uint8)
        ...
        Offset 232: m_trackId (int8)
        Offset 233: m_formula (uint8)
        Offset 234: m_sessionTimeLeft (uint16)
        Offset 236: m_sessionDuration (uint16)
        Offset 238: m_pitSpeedLimit (uint8)
        Offset 239: m_gamePaused (uint8)
        """
        try:
            # Extract session-specific fields
            # Based on F1 2019 telemetry spec
            if len(data) < 240:
                return None
            
            # Session type at offset 24
            session_type = struct.unpack_from('<B', data, 24)[0]
            
            # Track ID at offset 25
            track_id = struct.unpack_from('<b', data, 25)[0]
            
            # Game paused at offset 239
            game_paused = struct.unpack_from('<B', data, 239)[0] == 1
            
            # Update or create race state
            if self.last_race_state:
                self.last_race_state.session_type = session_type
                self.last_race_state.track_id = track_id
                self.last_race_state.game_paused = game_paused
                self.last_race_state.session_time = session_time
                self.last_race_state.session_uid = session_uid
                return self.last_race_state
            else:
                # Create new state with defaults
                return RaceState(
                    session_uid=session_uid,
                    session_type=session_type,
                    session_time=session_time,
                    game_paused=game_paused,
                    track_id=track_id,
                    current_lap=0,
                    is_off_track=False,
                    front_left_damage=0.0,
                    front_right_damage=0.0,
                    rear_left_damage=0.0,
                    rear_right_damage=0.0,
                    timestamp=time.time()
                )
        except struct.error:
            return None
    
    def _parse_lap_data_packet(self, data: bytes, session_uid: int, session_time: float, player_index: int) -> Optional[RaceState]:
        """
        Parse Lap Data Packet (ID 2)
        Contains lap times, penalties, and off-track status
        
        Structure: Header (24 bytes) + 20 cars * LapData (41 bytes each)
        LapData per car:
        - lastLapTime (float)
        - currentLapTime (float)
        - bestLapTime (float)
        - sector1Time (float)
        - sector2Time (float)
        - lapDistance (float)
        - totalDistance (float)
        - safetyCarDelta (float)
        - carPosition (uint8)
        - currentLapNum (uint8)
        - pitStatus (uint8)
        - sector (uint8)
        - currentLapInvalid (uint8)
        - penalties (uint8)
        - gridPosition (uint8)
        - driverStatus (uint8)
        - resultStatus (uint8)
        """
        try:
            if len(data) < 24 + (player_index + 1) * 41:
                return None
            
            # Calculate offset for player's car data
            offset = 24 + (player_index * 41)
            
            # Parse player's lap data
            lap_data = struct.unpack_from('<ffffffffBBBBBBBBB', data, offset)
            
            current_lap_num = lap_data[9]
            current_lap_invalid = lap_data[12] == 1  # This indicates off-track or cutting
            
            # Update or create race state
            if self.last_race_state:
                self.last_race_state.current_lap = current_lap_num
                self.last_race_state.is_off_track = current_lap_invalid
                self.last_race_state.session_time = session_time
                self.last_race_state.session_uid = session_uid
                return self.last_race_state
            else:
                return RaceState(
                    session_uid=session_uid,
                    session_type=0,
                    session_time=session_time,
                    game_paused=False,
                    track_id=0,
                    current_lap=current_lap_num,
                    is_off_track=current_lap_invalid,
                    front_left_damage=0.0,
                    front_right_damage=0.0,
                    rear_left_damage=0.0,
                    rear_right_damage=0.0,
                    timestamp=time.time()
                )
        except struct.error:
            return None
    
    def _parse_car_damage_packet(self, data: bytes, session_uid: int, session_time: float, player_index: int) -> Optional[RaceState]:
        """
        Parse Car Damage Packet (ID 6)
        Contains tyre wear, wing damage, and collision data
        
        Structure: Header (24 bytes) + 20 cars * CarDamageData
        CarDamageData per car:
        - tyresWear[4] (float * 4)
        - tyresDamage[4] (uint8 * 4)
        - brakesDamage[4] (uint8 * 4)
        - frontLeftWingDamage (uint8)
        - frontRightWingDamage (uint8)
        - rearWingDamage (uint8)
        - engineDamage (uint8)
        - gearBoxDamage (uint8)
        """
        try:
            # Each car damage data is 39 bytes
            if len(data) < 24 + (player_index + 1) * 39:
                return None
            
            # Calculate offset for player's car damage
            offset = 24 + (player_index * 39)
            
            # Parse damage data
            damage_data = struct.unpack_from('<ffffBBBBBBBBBBBB', data, offset)
            
            # Wing damage (indices 20, 21)
            front_left_wing = damage_data[20]
            front_right_wing = damage_data[21]
            rear_wing = damage_data[22]
            
            # Update or create race state
            if self.last_race_state:
                self.last_race_state.front_left_damage = front_left_wing
                self.last_race_state.front_right_damage = front_right_wing
                self.last_race_state.rear_left_damage = rear_wing
                self.last_race_state.rear_right_damage = rear_wing
                self.last_race_state.session_time = session_time
                self.last_race_state.session_uid = session_uid
                return self.last_race_state
            else:
                return RaceState(
                    session_uid=session_uid,
                    session_type=0,
                    session_time=session_time,
                    game_paused=False,
                    track_id=0,
                    current_lap=0,
                    is_off_track=False,
                    front_left_damage=front_left_wing,
                    front_right_damage=front_right_wing,
                    rear_left_damage=rear_wing,
                    rear_right_damage=rear_wing,
                    timestamp=time.time()
                )
        except struct.error:
            return None

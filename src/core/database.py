"""
SQLite Database Handler for F1 Safety Rating System
Manages race history, incidents, and user profile persistence
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Tuple


class Database:
    """SQLite database manager for F1 Safety Rating tracking"""
    
    def __init__(self, db_path: str = "history.db"):
        """
        Initialize database connection and create tables if needed
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: sqlite3.Connection
        self._connect()
        self._create_tables()
        self._initialize_tracks()
        self._initialize_user_profile()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
    
    def _create_tables(self):
        """Create all required tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Tracks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_track_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                corner_count INTEGER NOT NULL
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                track_id INTEGER NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                start_sr FLOAT NOT NULL,
                end_sr FLOAT,
                total_incidents INTEGER DEFAULT 0,
                FOREIGN KEY (track_id) REFERENCES tracks(id)
            )
        """)
        
        # Incidents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                lap_number INTEGER NOT NULL,
                incident_type TEXT NOT NULL,
                session_time FLOAT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # User profile table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_sr FLOAT NOT NULL DEFAULT 100.0,
                total_distance FLOAT NOT NULL DEFAULT 0.0
            )
        """)
        
        self.conn.commit()
    
    def _initialize_tracks(self):
        """Initialize F1 2019 track data"""
        tracks_data = [
            (0, "Melbourne", 16),
            (1, "Paul Ricard", 15),
            (2, "Shanghai", 16),
            (3, "Sakhir (Bahrain)", 15),
            (4, "Catalunya", 16),
            (5, "Monaco", 19),
            (6, "Montreal", 14),
            (7, "Silverstone", 18),
            (8, "Hockenheim", 17),
            (9, "Hungaroring", 14),
            (10, "Spa-Francorchamps", 19),
            (11, "Monza", 11),
            (12, "Singapore", 23),
            (13, "Suzuka", 18),
            (14, "Abu Dhabi", 21),
            (15, "Texas (COTA)", 20),
            (16, "Brazil (Interlagos)", 15),
            (17, "Austria", 10),
            (18, "Sochi", 18),
            (19, "Mexico", 17),
            (20, "Baku", 20),
            (21, "Sakhir Short", 11),
            (22, "Silverstone Short", 13),
            (23, "Texas Short", 12),
            (24, "Suzuka Short", 13),
        ]
        
        cursor = self.conn.cursor()
        for game_id, name, corners in tracks_data:
            cursor.execute("""
                INSERT OR IGNORE INTO tracks (game_track_id, name, corner_count)
                VALUES (?, ?, ?)
            """, (game_id, name, corners))
        
        self.conn.commit()
    
    def _initialize_user_profile(self):
        """Initialize user profile if it doesn't exist"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO user_profile (id, current_sr, total_distance)
            VALUES (1, 100.0, 0.0)
        """)
        self.conn.commit()
    
    # === User Profile Methods ===
    
    def get_current_sr(self) -> float:
        """Get current Safety Rating"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT current_sr FROM user_profile WHERE id = 1")
        row = cursor.fetchone()
        return row[0] if row else 100.0
    
    def update_sr(self, new_sr: float):
        """Update current Safety Rating"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE user_profile SET current_sr = ? WHERE id = 1
        """, (new_sr,))
        self.conn.commit()
    
    def add_distance(self, distance: float):
        """Add to total distance driven"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE user_profile SET total_distance = total_distance + ? WHERE id = 1
        """, (distance,))
        self.conn.commit()
    
    def get_user_stats(self) -> Dict[str, float]:
        """Get complete user profile statistics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT current_sr, total_distance FROM user_profile WHERE id = 1")
        row = cursor.fetchone()
        if row:
            return {
                'current_sr': row[0],
                'total_distance': row[1]
            }
        return {'current_sr': 100.0, 'total_distance': 0.0}
    
    # === Track Methods ===
    
    def get_track_by_game_id(self, game_track_id: int) -> Optional[Dict]:
        """Get track info by game's track ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, game_track_id, name, corner_count
            FROM tracks
            WHERE game_track_id = ?
        """, (game_track_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'game_track_id': row[1],
                'name': row[2],
                'corner_count': row[3]
            }
        return None
    
    # === Session Methods ===
    
    def start_session(self, session_uid: str, track_id: int, start_sr: float) -> bool:
        """
        Start a new race session
        
        Args:
            session_uid: Unique session identifier from telemetry
            track_id: Internal track ID from tracks table
            start_sr: Safety Rating at session start
            
        Returns:
            True if session created successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (session_id, track_id, start_time, start_sr)
                VALUES (?, ?, ?, ?)
            """, (session_uid, track_id, datetime.now(), start_sr))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Session already exists
            return False
    
    def end_session(self, session_uid: str, end_sr: float) -> bool:
        """
        End a race session
        
        Args:
            session_uid: Session identifier
            end_sr: Final Safety Rating
            
        Returns:
            True if session updated successfully
        """
        try:
            cursor = self.conn.cursor()
            
            # Count total incidents for this session
            cursor.execute("""
                SELECT COUNT(*) FROM incidents WHERE session_id = ?
            """, (session_uid,))
            total_incidents = cursor.fetchone()[0]
            
            # Update session
            cursor.execute("""
                UPDATE sessions
                SET end_time = ?, end_sr = ?, total_incidents = ?
                WHERE session_id = ?
            """, (datetime.now(), end_sr, total_incidents, session_uid))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error ending session: {e}")
            return False
    
    def get_session(self, session_uid: str) -> Optional[Dict]:
        """Get session details"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.session_id, s.track_id, s.start_time, s.end_time,
                   s.start_sr, s.end_sr, s.total_incidents, t.name
            FROM sessions s
            JOIN tracks t ON s.track_id = t.id
            WHERE s.session_id = ?
        """, (session_uid,))
        row = cursor.fetchone()
        if row:
            return {
                'session_id': row[0],
                'track_id': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'start_sr': row[4],
                'end_sr': row[5],
                'total_incidents': row[6],
                'track_name': row[7]
            }
        return None
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent race sessions with track info"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.session_id, s.start_time, s.end_time,
                   s.start_sr, s.end_sr, s.total_incidents,
                   t.name, t.corner_count
            FROM sessions s
            JOIN tracks t ON s.track_id = t.id
            WHERE s.end_time IS NOT NULL
            ORDER BY s.start_time DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'session_id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'start_sr': row[3],
                'end_sr': row[4],
                'total_incidents': row[5],
                'track_name': row[6],
                'corner_count': row[7]
            })
        return results
    
    # === Incident Methods ===
    
    def add_incident(self, session_uid: str, lap_number: int, 
                     incident_type: str, session_time: float) -> bool:
        """
        Record an incident during a race
        
        Args:
            session_uid: Session identifier
            lap_number: Current lap when incident occurred
            incident_type: '1x', '2x', or '4x'
            session_time: Game session time (for debugging)
            
        Returns:
            True if incident recorded successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO incidents (session_id, lap_number, incident_type, session_time)
                VALUES (?, ?, ?, ?)
            """, (session_uid, lap_number, incident_type, session_time))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding incident: {e}")
            return False
    
    def get_session_incidents(self, session_uid: str) -> List[Dict]:
        """Get all incidents for a specific session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, lap_number, incident_type, session_time
            FROM incidents
            WHERE session_id = ?
            ORDER BY session_time ASC
        """, (session_uid,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'lap_number': row[1],
                'incident_type': row[2],
                'session_time': row[3]
            })
        return results
    
    def get_incident_stats_by_type(self, session_uid: str) -> Dict[str, int]:
        """Get incident breakdown by type for a session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT incident_type, COUNT(*) as count
            FROM incidents
            WHERE session_id = ?
            GROUP BY incident_type
        """, (session_uid,))
        
        stats = {'1x': 0, '2x': 0, '4x': 0}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        return stats
    
    # === Analytics Methods ===
    
    def get_sr_history(self, limit: int = 50) -> List[Tuple[str, float]]:
        """Get SR progression over time"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT start_time, end_sr
            FROM sessions
            WHERE end_sr IS NOT NULL
            ORDER BY start_time ASC
            LIMIT ?
        """, (limit,))
        return [(row[0], row[1]) for row in cursor.fetchall()]
    
    def get_track_statistics(self) -> List[Dict]:
        """Get performance statistics per track"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.name, 
                   COUNT(s.session_id) as races,
                   AVG(s.total_incidents) as avg_incidents,
                   AVG(s.end_sr - s.start_sr) as avg_sr_change
            FROM tracks t
            LEFT JOIN sessions s ON t.id = s.track_id AND s.end_time IS NOT NULL
            GROUP BY t.id, t.name
            HAVING races > 0
            ORDER BY avg_sr_change DESC
        """)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'track': row[0],
                'races': row[1],
                'avg_incidents': round(row[2], 2),
                'avg_sr_change': round(row[3], 2)
            })
        return results
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

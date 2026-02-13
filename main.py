"""
F1 2019 Safety Rating Tracker - Main Entry Point
Integrates UDP listener, telemetry processing, SR calculation, overlay, and web dashboard
"""
import socket
import sys
import signal
from threading import Thread
from typing import Optional

from src.adapters import F12019Adapter
from src.core import Database, SessionManager, SREngine
from src.ui import create_overlay, F1TrayIcon
from src.web import Dashboard


class F1SafetyRateTracker:
    """Main application controller"""
    
    def __init__(self, 
                 udp_port: int = 20777,
                 web_port: int = 5000,
                 enable_overlay: bool = True,
                 enable_dashboard: bool = True):
        """
        Initialize F1 Safety Rating Tracker
        
        Args:
            udp_port: UDP port for F1 2019 telemetry (default: 20777)
            web_port: Port for web dashboard (default: 5000)
            enable_overlay: Show real-time overlay window
            enable_dashboard: Start web dashboard server
        """
        print("=" * 60)
        print("F1 2019 SAFETY RATING TRACKER")
        print("=" * 60)
        
        # Configuration
        self.udp_port = udp_port
        self.web_port = web_port
        self.enable_overlay = enable_overlay
        self.enable_dashboard = enable_dashboard
        
        # Components
        self.db = Database("history.db")
        self.adapter = F12019Adapter()
        self.sr_engine = SREngine(window_size=100, sr_multiplier=10.0)
        
        # Load current SR from database
        current_sr = self.db.get_current_sr()
        self.sr_engine.set_sr(current_sr)
        print(f"[Init] Loaded SR from database: {current_sr:.2f}")
        
        # Session manager with callbacks
        self.session_manager = SessionManager(
            on_race_start=self._on_race_start,
            on_race_end=self._on_race_end
        )
        
        # UDP socket
        self.sock: Optional[socket.socket] = None
        self.running = False
        
        # UI components
        self.overlay_app = None
        self.overlay_window = None
        self.dashboard = None
        self.dashboard_thread = None
        self.tray_icon = None
        
        # Sync timer for database updates
        self.last_db_sync_time = 0
        self.db_sync_interval = 2.0  # Sync to database every 2 seconds during race
        
        # Statistics
        self.packets_received = 0
        self.current_track_name = "Unknown"
    
    def _on_race_start(self, session_uid: str, track_id: int, start_sr: float):
        """
        Callback when race session starts
        
        Args:
            session_uid: Unique session identifier
            track_id: Track being raced on
            start_sr: Starting Safety Rating (unused, we get from SR engine)
        """
        # Get track info
        track_info = self.db.get_track_by_game_id(track_id)
        if track_info:
            self.current_track_name = track_info['name']
            track_db_id = track_info['id']
        else:
            self.current_track_name = f"Track #{track_id}"
            track_db_id = 1  # Default to first track
        
        # Get current SR from engine
        current_sr = self.sr_engine.current_sr
        
        # Start session in database
        success = self.db.start_session(session_uid, track_db_id, current_sr)
        
        if success:
            print("\n" + "=" * 60)
            print("🏁 RACE STARTED")
            print("=" * 60)
            print(f"Track: {self.current_track_name}")
            print(f"Session ID: {session_uid}")
            print(f"Starting SR: {current_sr:.2f}")
            print("=" * 60 + "\n")
            
            # Reset SR engine for new session
            self.sr_engine.reset_session()
        else:
            print(f"[Warning] Session {session_uid} already exists in database")
    
    def _on_race_end(self, session_uid: str, end_sr: float):
        """
        Callback when race session ends
        
        Args:
            session_uid: Session identifier
            end_sr: Ending Safety Rating (unused, we get from SR engine)
        """
        # Get final SR from engine
        final_sr = self.sr_engine.current_sr
        stats = self.sr_engine.get_stats()
        
        # Update session in database
        success = self.db.end_session(session_uid, final_sr)
        
        # Save incidents to database
        session_incidents = self.session_manager.active_session_uid
        if session_incidents:
            # Note: In a full implementation, we'd track each incident's lap/time
            # For now, we just save final counts
            pass
        
        # Update user profile SR
        self.db.update_sr(final_sr)
        
        if success:
            # Get track info for CPI calculation
            total_corners = stats['corners_completed']
            cpi = self.sr_engine.calculate_cpi(total_corners)
            
            print("\n" + "=" * 60)
            print("🏁 RACE FINISHED")
            print("=" * 60)
            print(f"Track: {self.current_track_name}")
            print(f"Final SR: {final_sr:.2f}")
            print(f"Incidents: 1x={stats['incidents_1x']}, 2x={stats['incidents_2x']}, 4x={stats['incidents_4x']}")
            print(f"Total Incidents: {stats['total_incidents']}")
            print(f"Corners Completed: {stats['corners_completed']}")
            print(f"CPI (Corners/Incident): {cpi}")
            print("=" * 60 + "\n")
        else:
            print(f"[Warning] Failed to end session {session_uid}")
    
    def _setup_udp_socket(self):
        """Initialize UDP socket for telemetry reception"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.udp_port))
        self.sock.settimeout(1.0)  # 1 second timeout for graceful shutdown
        print(f"[UDP] Listening on port {self.udp_port}")
    
    def _telemetry_loop(self):
        """Main telemetry reception loop"""
        print("[Telemetry] Starting UDP listener...")
        
        while self.running:
            try:
                if self.sock is None:
                    break
                data, addr = self.sock.recvfrom(2048)
                self.packets_received += 1
                
                # Parse telemetry packet
                race_state = self.adapter.parse_packet(data)
                
                if race_state:
                    # Process through session manager
                    self.session_manager.process_telemetry(race_state)
                    
                    # If race is active, update SR engine
                    if self.session_manager.is_race_active():
                        self.sr_engine.process_telemetry(race_state)
                        
                        # Periodically sync SR to database during active race
                        self._sync_sr_to_database_if_needed()
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Error] Telemetry processing error: {e}")
                continue
    
    def _get_overlay_stats(self) -> dict:
        """Get current stats for overlay display"""
        stats = self.sr_engine.get_stats()
        stats['is_race_active'] = self.session_manager.is_race_active()
        
        # Calculate CPI if race is active
        if self.session_manager.is_race_active() and stats['corners_completed'] > 0:
            total_corners = stats['corners_completed']
            stats['cpi'] = self.sr_engine.calculate_cpi(total_corners)
        else:
            stats['cpi'] = 0.0
        
        return stats
    
    def _sync_sr_to_database_if_needed(self):
        """Sync SR to database during active race (every few seconds)"""
        import time
        current_time = time.time()
        
        # Only sync if enough time has passed
        if current_time - self.last_db_sync_time >= self.db_sync_interval:
            try:
                current_sr = self.sr_engine.current_sr
                self.db.update_sr(current_sr)
                self.last_db_sync_time = current_time
                # Silent sync - no need to log every time
            except Exception as e:
                print(f"[Warning] Failed to sync SR to database: {e}")
    
    def _update_tray_tooltip(self):
        """Update system tray tooltip with current SR info"""
        if self.tray_icon and self.sr_engine:
            sr = self.sr_engine.current_sr
            license_class, _ = self.sr_engine.get_license_class()
            self.tray_icon.update_tooltip(sr, license_class)
    
    def start(self):
        """Start the application"""
        self.running = True
        
        # Setup UDP socket
        self._setup_udp_socket()
        
        # Start web dashboard in background thread
        if self.enable_dashboard:
            self.dashboard = Dashboard(self.db, port=self.web_port)
            self.dashboard_thread = self.dashboard.run_threaded()
            print(f"[Dashboard] Web interface available at http://127.0.0.1:{self.web_port}")
        
        # Start telemetry in background thread
        telemetry_thread = Thread(target=self._telemetry_loop, daemon=True)
        telemetry_thread.start()
        
        # Start overlay (must be on main thread for PyQt6)
        if self.enable_overlay:
            print("[Overlay] Starting real-time overlay...")
            self.overlay_app, self.overlay_window = create_overlay(
                update_callback=self._get_overlay_stats
            )
            
            # Create system tray icon
            print("[System Tray] Creating tray icon...")
            self.tray_icon = F1TrayIcon(self.overlay_app, self, self.web_port)
            self.tray_icon.show_startup_message()
            
            # Update tray tooltip periodically
            from PyQt6.QtCore import QTimer
            self.tooltip_timer = QTimer()
            self.tooltip_timer.timeout.connect(self._update_tray_tooltip)
            self.tooltip_timer.start(5000)  # Update every 5 seconds
            
            # Handle Ctrl+C gracefully
            signal.signal(signal.SIGINT, lambda *args: self.stop())
            
            print("[Main] Application running in background. Check system tray icon.")
            print("[Main] Right-click tray icon for options, or press Ctrl+C to exit.")
            
            # Run Qt event loop (blocking)
            self.overlay_app.exec()
        else:
            # No overlay, just keep running
            print("[Main] Running without overlay. Press Ctrl+C to exit.")
            try:
                while self.running:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[Main] Shutting down...")
        
        self.stop()
    
    def stop(self):
        """Stop the application gracefully"""
        if not self.running:
            return
        
        print("\n[Main] Stopping application...")
        self.running = False
        
        # End any active session
        if self.session_manager.is_race_active():
            self.session_manager.force_end_current_session()
        
        # Close socket
        if self.sock:
            self.sock.close()
        
        # Close database
        self.db.close()
        
        print(f"[Stats] Total packets received: {self.packets_received}")
        print("[Main] Shutdown complete")
        
        # Exit application
        if self.overlay_app:
            self.overlay_app.quit()
        sys.exit(0)


def main():
    """Application entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="F1 2019 Safety Rating Tracker")
    parser.add_argument('--udp-port', type=int, default=20777, 
                       help='UDP port for F1 2019 telemetry (default: 20777)')
    parser.add_argument('--web-port', type=int, default=5000,
                       help='Port for web dashboard (default: 5000)')
    parser.add_argument('--no-overlay', action='store_true',
                       help='Disable real-time overlay')
    parser.add_argument('--no-dashboard', action='store_true',
                       help='Disable web dashboard')
    
    args = parser.parse_args()
    
    # Create and start tracker
    tracker = F1SafetyRateTracker(
        udp_port=args.udp_port,
        web_port=args.web_port,
        enable_overlay=not args.no_overlay,
        enable_dashboard=not args.no_dashboard
    )
    
    try:
        tracker.start()
    except KeyboardInterrupt:
        tracker.stop()


if __name__ == "__main__":
    main()

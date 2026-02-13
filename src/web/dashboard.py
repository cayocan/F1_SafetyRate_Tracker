"""
Flask Web Dashboard for F1 Safety Rating History
Displays race history, charts, and statistics
"""
from flask import Flask, render_template, jsonify


class Dashboard:
    """Web dashboard server for race history visualization"""
    
    def __init__(self, database, host: str = "127.0.0.1", port: int = 5000):
        """
        Initialize Flask dashboard
        
        Args:
            database: Database instance for querying history
            host: Server host
            port: Server port
        """
        self.db = database
        self.host = host
        self.port = port
        
        # Create Flask app
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('index.html')
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get overall user statistics"""
            try:
                user_stats = self.db.get_user_stats()
                recent_sessions = self.db.get_recent_sessions(limit=1)
                
                last_race = None
                if recent_sessions:
                    last_race = {
                        'track': recent_sessions[0]['track_name'],
                        'date': recent_sessions[0]['start_time'],
                        'sr_change': recent_sessions[0]['end_sr'] - recent_sessions[0]['start_sr']
                    }
                
                return jsonify({
                    'current_sr': user_stats['current_sr'],
                    'total_distance': user_stats['total_distance'],
                    'last_race': last_race
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/history')
        def get_history():
            """Get race session history"""
            try:
                sessions = self.db.get_recent_sessions(limit=50)
                
                history = []
                for session in sessions:
                    sr_change = session['end_sr'] - session['start_sr']
                    history.append({
                        'session_id': session['session_id'],
                        'date': session['start_time'],
                        'track': session['track_name'],
                        'start_sr': round(session['start_sr'], 2),
                        'end_sr': round(session['end_sr'], 2),
                        'sr_change': round(sr_change, 2),
                        'incidents': session['total_incidents']
                    })
                
                return jsonify(history)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/session/<session_id>')
        def get_session_details(session_id):
            """Get detailed info for a specific session"""
            try:
                session = self.db.get_session(session_id)
                if not session:
                    return jsonify({'error': 'Session not found'}), 404
                
                incidents = self.db.get_session_incidents(session_id)
                incident_stats = self.db.get_incident_stats_by_type(session_id)
                
                return jsonify({
                    'session': session,
                    'incidents': incidents,
                    'incident_breakdown': incident_stats
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/sr-history')
        def get_sr_history():
            """Get SR progression over time for charting"""
            try:
                history = self.db.get_sr_history(limit=50)
                
                data = {
                    'dates': [entry[0] for entry in history],
                    'sr_values': [entry[1] for entry in history]
                }
                
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/track-stats')
        def get_track_stats():
            """Get performance statistics per track"""
            try:
                stats = self.db.get_track_statistics()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def run(self, debug: bool = False):
        """
        Start the Flask development server
        
        Args:
            debug: Enable debug mode
        """
        print(f"[Dashboard] Starting web server at http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=debug, use_reloader=False)
    
    def run_threaded(self):
        """Run dashboard in a separate thread"""
        import threading
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread

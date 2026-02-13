# F1 2019 Safety Rating Tracker - Pro Version

A complete ecosystem for tracking your F1 2019 Safety Rating (SR) with real-time overlay, persistence layer, and web dashboard.

## Features

### 🎮 Real-time Telemetry Processing
- UDP telemetry listener (Port 20777)
- Binary packet decoding for F1 2019
- Session detection (Practice, Qualifying, Race)
- Incident tracking (Off-track, Spins, Collisions)

### 📊 Safety Rating System
- iRacing-style moving average over corners
- Incident classification:
  - **1x** (Off-track): 1 point
  - **2x** (Spin): 2 points
  - **4x** (Collision): 4 points
- Corners Per Incident (CPI) calculation
- Historical SR tracking

### 🖥️ Real-time Overlay (PyQt6)
- Transparent window overlay
- Live SR display with color coding
- Incident counters (1x, 2x, 4x)
- Corners completed
- CPI meter
- Draggable and always-on-top

### 🌐 Web Dashboard
- Race history with statistics
- SR progression charts
- Per-track performance analysis
- Detailed incident breakdown
- Responsive design

### 💾 SQLite Database
- Race session history
- Incident logging with timestamps
- Track database (25 F1 2019 tracks)
- User profile with total stats

## Installation

### Prerequisites
- Python 3.8+
- F1 2019 game with UDP telemetry enabled

### Quick Setup with Virtual Environment (Recommended)

#### Windows PowerShell
```powershell
# 1. Setup environment (creates .venv and installs everything)
.\setup_venv.ps1

# 2. Activate environment (every time you open a new terminal)
.\activate.ps1

# 3. Run the tracker
python main.py
```

#### Windows CMD/Batch
```cmd
REM 1. Setup environment
setup_venv.bat

REM 2. Activate environment
activate.bat

REM 3. Run the tracker
python main.py
```

### Manual Installation (Alternative)

1. Clone or download this repository

2. Create virtual environment:
```bash
python -m venv .venv
```

3. Activate virtual environment:
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Enable UDP telemetry in F1 2019:
   - Go to Game Settings → Telemetry Settings
   - Set UDP Telemetry to "On"
   - Set UDP Broadcast Mode to "On"
   - Default port: 20777

## Usage

### Quick Start (Recommended)

**One-Click Launch** - Checks everything and runs automatically:

```batch
REM Windows (Double-click or run in CMD)
run.bat

REM Or PowerShell
.\run.ps1
```

The launcher will:
- ✅ Check if Python is installed
- ✅ Create virtual environment if missing
- ✅ Install/update dependencies automatically
- ✅ Run system checks
- ✅ Launch the application

### Manual Start

```powershell
# Activate environment (if not already active)
.\activate.ps1

# Run the tracker
python main.py
```

This will start:
- UDP telemetry listener on port 20777
- Real-time SR overlay (PyQt6)
- Web dashboard on http://127.0.0.1:5000

### Alternative Launch Methods

**Method 1: One-Click Launcher** (Easiest)
```batch
run.bat          # Windows CMD/Batch
.\run.ps1        # Windows PowerShell
```

**Method 2: Manual Activation**
```powershell
.\activate.ps1   # Activate environment
python main.py   # Run tracker
```

**Method 3: Full Setup + Run**
```powershell
.\setup_venv.ps1 # One-time setup
python main.py   # Run tracker
```

### Command Line Options
```bash
python main.py --help

Options:
  --udp-port PORT        UDP port for telemetry (default: 20777)
  --web-port PORT        Web dashboard port (default: 5000)
  --no-overlay          Disable real-time overlay
  --no-dashboard        Disable web dashboard
```

### Examples

**Run without overlay (headless mode):**
```bash
python main.py --no-overlay
```

**Custom ports:**
```bash
python main.py --udp-port 30777 --web-port 8080
```

**Only overlay (no web dashboard):**
```bash
python main.py --no-dashboard
```

## Project Structure

```
F1_SafetyRate_Tracker/
│
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── history.db                  # SQLite database (created on first run)
│
└── src/
    ├── adapters/               # Telemetry packet parsers
    │   ├── base_adapter.py     # Abstract adapter interface
    │   └── f12019_adapter.py   # F1 2019 specific implementation
    │
    ├── core/                   # Core logic
    │   ├── database.py         # SQLite handlers
    │   ├── session_manager.py  # Race session lifecycle
    │   └── sr_engine.py        # Safety Rating calculation
    │
    ├── ui/                     # User interface
    │   └── overlay.py          # PyQt6 transparent overlay
    │
    └── web/                    # Web dashboard
        ├── dashboard.py        # Flask server
        └── templates/
            └── index.html      # Dashboard HTML

```

## How It Works

### Session Detection
- **Start Trigger:** `m_sessionType == 10` (Race) AND `m_sessionTime > 0`
- **End Trigger:** Session type changes OR extended pause OR Result Screen

### Safety Rating Algorithm
1. Track incidents per corner
2. Maintain moving average over last 100 corners
3. Calculate SR: `SR = 100 - (avg_incidents * multiplier)`
4. Clamp result between 0-100

### Incident Detection
- **Off-track (1x):** Detected via `m_currentLapInvalid` flag
- **Collision (4x):** Detected via damage increase > threshold
- **Spin (2x):** Currently disabled (requires gyro data)

## Database Schema

### Tables
- **tracks**: F1 2019 track information (25 tracks)
- **sessions**: Race session records
- **incidents**: Individual incident logs
- **user_profile**: Global SR and statistics

### SQL Queries
View your stats directly:
```sql
-- Current SR
SELECT current_sr FROM user_profile;

-- Recent races
SELECT * FROM sessions ORDER BY start_time DESC LIMIT 10;

-- Track performance
SELECT t.name, COUNT(*) as races, AVG(s.total_incidents) as avg_incidents
FROM sessions s JOIN tracks t ON s.track_id = t.id
GROUP BY t.name;
```

## Web Dashboard Features

### Main Stats Panel
- Current Safety Rating (color-coded)
- Total distance driven
- Last race summary

### SR History Chart
- Line chart showing SR progression over time
- Interactive Chart.js visualization

### Recent Races Table
- Date, track, SR change, incident count
- Sortable and filterable

### Track Performance
- Average incidents per track
- Average SR change per track
- Total races per track

## Overlay Controls

- **Drag to move:** Left-click and drag anywhere
- **Close:** `Ctrl+Q` or close main window
- **Always on top:** Stays above game window

## Troubleshooting

### Launcher Issues

**Launcher freezes at "Verificacao final":**
- ✅ **FIXED** - Update to latest `run.bat`/`run.ps1`
- See [FIX_LOG_FREEZE.md](FIX_LOG_FREEZE.md) for details

**Unicode/Encoding errors:**
- ✅ **FIXED** - `check_install.py` now handles Windows encoding
- See [FIX_LOG_ENCODING.md](FIX_LOG_ENCODING.md) for details

**Port already in use (WinError 10048):**
- Another instance is running - close it first
- Or use custom port: `python main.py --udp-port 20778`

### No telemetry received
1. Check F1 2019 UDP settings are enabled
2. Verify firewall allows UDP on port 20777
3. Ensure correct port in application settings

### Overlay not showing
1. Install PyQt6: `pip install PyQt6`
2. Check if running on Windows (Linux may need X11 config)

### Database errors
1. Delete `history.db` to reset database
2. Check file permissions

### Web dashboard not loading
1. Check port 5000 is not in use
2. Try custom port: `--web-port 8080`
3. Navigate to `http://127.0.0.1:5000` in browser

## Performance Notes

- Minimal CPU usage (~1-2%)
- Database writes only on session end
- Overlay updates at 10 Hz
- UDP packet processing: <1ms

## 📚 Additional Documentation

- **[LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md)** - Complete guide for the one-click launcher (`run.bat`/`run.ps1`)
- **[QUICK_START_VENV.md](QUICK_START_VENV.md)** - Virtual environment quick reference
- Inline code comments for implementation details

## Future Enhancements

- [ ] Spin detection via gyroscope data
- [ ] Multi-class SR (per car type)
- [ ] Competitive mode (race-specific SR)
- [ ] Discord integration for notifications
- [ ] Cloud sync for cross-device access
- [ ] Machine learning incident prediction
- [ ] VR overlay support

## License

This project is provided as-is for personal use with F1 2019.

## Credits

- F1 2019 UDP specification: Codemasters
- Safety Rating concept: iRacing
- Built with Python, PyQt6, Flask, Chart.js

---

**Happy Racing! Drive safe and improve your SR! 🏎️**

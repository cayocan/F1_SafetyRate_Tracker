"""
PyQt6 Transparent Overlay for Real-time SR Display
Shows Safety Rating, incidents, and session stats during racing
"""
import sys
from typing import Dict, Any, Optional, Callable
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class SROverlay(QWidget):
    """Transparent overlay window for real-time telemetry display"""
    
    def __init__(self, update_callback: Optional[Callable[[], Dict[str, Any]]] = None):
        """
        Initialize overlay window
        
        Args:
            update_callback: Function to call for getting latest stats
        """
        super().__init__()
        self.update_callback = update_callback
        self.init_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)  # Update every 100ms
    
    def init_ui(self):
        """Initialize UI components"""
        # Window settings
        self.setWindowTitle("F1 Safety Rating Overlay")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position and size
        self.setGeometry(50, 50, 350, 250)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        self.title_label = self._create_label("F1 SAFETY RATING", 16, bold=True)
        layout.addWidget(self.title_label)
        
        # SR Display
        self.sr_label = self._create_label("SR: --.-", 32, bold=True, color="#00FF00")
        layout.addWidget(self.sr_label)
        
        # Session status
        self.status_label = self._create_label("Status: Idle", 12, color="#FFFF00")
        layout.addWidget(self.status_label)
        
        # Incident counters
        self.incidents_label = self._create_label("Incidents: 1x:0 | 2x:0 | 4x:0", 12)
        layout.addWidget(self.incidents_label)
        
        # Corners
        self.corners_label = self._create_label("Corners: 0", 12)
        layout.addWidget(self.corners_label)
        
        # CPI
        self.cpi_label = self._create_label("CPI: --", 12)
        layout.addWidget(self.cpi_label)
        
        # Average incidents
        self.avg_label = self._create_label("Avg Inc/Corner: 0.000", 10, color="#AAAAAA")
        layout.addWidget(self.avg_label)
        
        # Instructions
        self.help_label = self._create_label("Drag to move | Ctrl+Q to close", 8, color="#666666")
        layout.addWidget(self.help_label)
        
        self.setLayout(layout)
        
        # Make draggable
        self.dragging = False
        self.drag_position = None
    
    def _create_label(self, text: str, size: int, bold: bool = False, 
                      color: str = "#FFFFFF") -> QLabel:
        """Create a styled label"""
        label = QLabel(text)
        font = QFont("Consolas", size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                background-color: rgba(0, 0, 0, 180);
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label
    
    def update_display(self):
        """Update overlay with latest data"""
        if self.update_callback:
            stats = self.update_callback()
            if stats is not None:
                self._update_labels(stats)
    
    def _update_labels(self, stats: Dict[str, Any]):
        """Update label texts with new stats"""
        # SR with color coding
        sr = stats.get('current_sr', 0.0)
        sr_color = self._get_sr_color(sr)
        self.sr_label.setText(f"SR: {sr:.1f}")
        self.sr_label.setStyleSheet(f"""
            QLabel {{
                color: {sr_color};
                background-color: rgba(0, 0, 0, 200);
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
        # Status
        is_active = stats.get('is_race_active', False)
        status_text = "⚫ Racing" if is_active else "⭕ Idle"
        status_color = "#00FF00" if is_active else "#888888"
        self.status_label.setText(f"Status: {status_text}")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                background-color: rgba(0, 0, 0, 180);
                padding: 5px;
                border-radius: 3px;
            }}
        """)
        
        # Incidents
        inc_1x = stats.get('incidents_1x', 0)
        inc_2x = stats.get('incidents_2x', 0)
        inc_4x = stats.get('incidents_4x', 0)
        total_inc = stats.get('total_incidents', 0)
        self.incidents_label.setText(f"Incidents: 1x:{inc_1x} | 2x:{inc_2x} | 4x:{inc_4x} (Total: {total_inc})")
        
        # Corners
        corners = stats.get('corners_completed', 0)
        self.corners_label.setText(f"Corners Completed: {corners}")
        
        # CPI
        cpi = stats.get('cpi', 0.0)
        cpi_text = f"{cpi:.2f}" if cpi < 9999 else "∞"
        self.cpi_label.setText(f"CPI (Corners/Incident): {cpi_text}")
        
        # Average
        avg = stats.get('avg_incidents_per_corner', 0.0)
        self.avg_label.setText(f"Avg Incidents/Corner: {avg:.3f}")
    
    def _get_sr_color(self, sr: float) -> str:
        """Get color based on SR value"""
        if sr >= 90:
            return "#00FF00"  # Green
        elif sr >= 75:
            return "#88FF00"  # Yellow-green
        elif sr >= 60:
            return "#FFFF00"  # Yellow
        elif sr >= 45:
            return "#FFAA00"  # Orange
        else:
            return "#FF0000"  # Red
    
    # Mouse event handlers for dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Q and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.close()


def create_overlay(update_callback: Optional[Callable[[], Dict[str, Any]]] = None) -> tuple:
    """
    Create and show overlay window
    
    Args:
        update_callback: Function to call for stats updates
        
    Returns:
        Tuple of (QApplication, SROverlay)
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    overlay = SROverlay(update_callback)
    overlay.show()
    
    return app, overlay

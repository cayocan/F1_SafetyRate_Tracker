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
        
        # State management
        self.simple_mode = False  # Toggle between full/simple display
        self.scale_factor = 1.0   # Scale for resizing (0.5 to 2.0)
        self.is_visible = True    # For toggle visibility
        
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
        
        # License Class (iRacing style)
        self.license_label = self._create_label("Class C", 20, bold=True, color="#FFAA00")
        layout.addWidget(self.license_label)
        
        # SR Display
        self.sr_label = self._create_label("SR: 2.50", 32, bold=True, color="#FFAA00")
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
        self.help_label = self._create_label(
            "Drag to move | Ctrl+Q: Hide/Show | Ctrl+M: Simple Mode | Ctrl+=/−: Resize", 
            8, color="#666666"
        )
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
        # SR with license class and color coding (iRacing style)
        sr = stats.get('current_sr', 2.50)
        license_class = stats.get('license_class', 'C')
        license_color = stats.get('license_color', '#FFAA00')
        
        # Update license class label
        self.license_label.setText(f"Class {license_class}")
        self.license_label.setStyleSheet(f"""
            QLabel {{
                color: {license_color};
                background-color: rgba(0, 0, 0, 200);
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
        # Update SR with same color as license
        self.sr_label.setText(f"SR: {sr:.2f}")
        self.sr_label.setStyleSheet(f"""
            QLabel {{
                color: {license_color};
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
        # Ctrl+Q: Toggle visibility (hide/show)
        if event.key() == Qt.Key.Key_Q and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_visibility()
            event.accept()
        
        # Ctrl+M: Toggle simple mode
        elif event.key() == Qt.Key.Key_M and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_simple_mode()
            event.accept()
        
        # Ctrl+= or Ctrl++: Increase size
        elif (event.key() in [Qt.Key.Key_Equal, Qt.Key.Key_Plus]) and \
             event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.resize_overlay(1.1)
            event.accept()
        
        # Ctrl+-: Decrease size
        elif event.key() == Qt.Key.Key_Minus and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.resize_overlay(0.9)
            event.accept()
        
        # Ctrl+0: Reset size
        elif event.key() == Qt.Key.Key_0 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.resize_overlay(1.0, absolute=True)
            event.accept()
    
    def toggle_visibility(self):
        """Toggle overlay visibility (hide/show)"""
        if self.is_visible:
            self.hide()
            self.is_visible = False
        else:
            self.show()
            self.is_visible = True
    
    def toggle_simple_mode(self):
        """Toggle between simple and detailed display modes"""
        self.simple_mode = not self.simple_mode
        
        # Show/hide labels based on mode
        if self.simple_mode:
            # Simple mode: Show only SR, license, incidents, and status
            self.title_label.hide()
            self.corners_label.hide()
            self.cpi_label.hide()
            self.avg_label.hide()
            self.help_label.hide()
        else:
            # Full mode: Show everything
            self.title_label.show()
            self.corners_label.show()
            self.cpi_label.show()
            self.avg_label.show()
            self.help_label.show()
        
        # Adjust window size
        self.adjustSize()
    
    def resize_overlay(self, factor: float, absolute: bool = False):
        """Resize the overlay
        
        Args:
            factor: Scale factor (multiply current size) or absolute scale if absolute=True
            absolute: If True, set scale to factor directly (reset)
        """
        if absolute:
            self.scale_factor = factor
        else:
            self.scale_factor *= factor
        
        # Clamp scale between 0.5x and 2.5x
        self.scale_factor = max(0.5, min(2.5, self.scale_factor))
        
        # Calculate new size
        base_width = 350
        base_height = 250
        new_width = int(base_width * self.scale_factor)
        new_height = int(base_height * self.scale_factor)
        
        # Resize window
        self.resize(new_width, new_height)
        
        # Update font sizes
        self._update_font_sizes()
    
    def _update_font_sizes(self):
        """Update all label font sizes based on scale factor"""
        base_sizes = {
            self.title_label: 16,
            self.license_label: 20,
            self.sr_label: 32,
            self.status_label: 12,
            self.incidents_label: 12,
            self.corners_label: 12,
            self.cpi_label: 12,
            self.avg_label: 10,
            self.help_label: 8
        }
        
        for label, base_size in base_sizes.items():
            font = label.font()
            new_size = max(6, int(base_size * self.scale_factor))  # Minimum 6pt
            font.setPointSize(new_size)
            label.setFont(font)
    
    def wheelEvent(self, event):
        """Handle mouse wheel for resizing (with Ctrl)"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Scroll up = zoom in, scroll down = zoom out
            delta = event.angleDelta().y()
            if delta > 0:
                self.resize_overlay(1.05)
            elif delta < 0:
                self.resize_overlay(0.95)
            event.accept()
        else:
            event.ignore()


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

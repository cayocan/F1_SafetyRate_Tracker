"""
System Tray Icon for F1 Safety Rating Tracker
Provides background running with system tray controls
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt
import webbrowser


class F1TrayIcon:
    """System tray icon with menu for controlling the application"""
    
    def __init__(self, app, tracker, web_port: int = 5000):
        """
        Initialize system tray icon
        
        Args:
            app: QApplication instance
            tracker: F1SafetyRateTracker instance
            web_port: Port where web dashboard is running
        """
        self.app = app
        self.tracker = tracker
        self.web_port = web_port
        self.overlay_visible = True
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(app)
        self.tray_icon.setIcon(self._create_icon())
        self.tray_icon.setToolTip("F1 Safety Rating Tracker")
        
        # Create context menu
        self._create_menu()
        
        # Show tray icon
        self.tray_icon.show()
        
        # Connect double-click to toggle overlay
        self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _create_icon(self) -> QIcon:
        """Create a simple icon for the system tray"""
        # Create a 64x64 pixmap
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw icon
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Red circle background (F1 theme)
        painter.setBrush(QColor("#e10600"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 60, 60)
        
        # White "SR" text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "SR")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_menu(self):
        """Create the system tray context menu"""
        menu = QMenu()
        
        # Show/Hide Overlay action
        self.overlay_action = menu.addAction("🖥️ Hide Overlay")  # type: ignore
        self.overlay_action.triggered.connect(self._toggle_overlay)  # type: ignore
        
        menu.addSeparator()
        
        # Open Web Dashboard action
        dashboard_action = menu.addAction("🌐 Open Dashboard")
        dashboard_action.triggered.connect(self._open_dashboard)  # type: ignore
        
        menu.addSeparator()
        
        # Exit action
        exit_action = menu.addAction("❌ Exit")
        exit_action.triggered.connect(self._exit_application)  # type: ignore
        
        self.tray_icon.setContextMenu(menu)
    
    def _toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.tracker.overlay_window:
            if self.overlay_visible:
                # Hide overlay
                self.tracker.overlay_window.hide()
                self.overlay_visible = False
                if self.overlay_action:
                    self.overlay_action.setText("🖥️ Show Overlay")
                self.tray_icon.showMessage(
                    "F1 SR Tracker",
                    "Overlay hidden. Right-click tray icon to show again.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                # Show overlay
                self.tracker.overlay_window.show()
                self.overlay_visible = True
                if self.overlay_action:
                    self.overlay_action.setText("🖥️ Hide Overlay")
                self.tray_icon.showMessage(
                    "F1 SR Tracker",
                    "Overlay visible. Use Ctrl+Q to toggle.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
    
    def _open_dashboard(self):
        """Open web dashboard in default browser"""
        url = f"http://127.0.0.1:{self.web_port}"
        try:
            webbrowser.open(url)
            self.tray_icon.showMessage(
                "F1 SR Tracker",
                f"Opening dashboard at {url}",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        except Exception as e:
            self.tray_icon.showMessage(
                "F1 SR Tracker",
                f"Failed to open browser: {str(e)}",
                QSystemTrayIcon.MessageIcon.Warning,
                3000
            )
    
    def _exit_application(self):
        """Exit the application completely"""
        # Show confirmation
        self.tray_icon.showMessage(
            "F1 SR Tracker",
            "Closing application...",
            QSystemTrayIcon.MessageIcon.Information,
            1000
        )
        
        # Stop tracker
        self.tracker.stop()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation (clicks)"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double-click toggles overlay
            self._toggle_overlay()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single left-click shows a brief message
            if self.tracker.overlay_window:
                sr = self.tracker.sr_engine.current_sr
                license_class, _ = self.tracker.sr_engine.get_license_class()
                self.tray_icon.showMessage(
                    "F1 SR Tracker",
                    f"SR: {sr:.2f} ({license_class})\nDouble-click to toggle overlay",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
    
    def show_startup_message(self):
        """Show notification when app starts"""
        self.tray_icon.showMessage(
            "F1 SR Tracker Started",
            "Running in background. Right-click icon for options.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def update_tooltip(self, sr: float, license_class: str):
        """Update tray icon tooltip with current SR
        
        Args:
            sr: Current Safety Rating
            license_class: Current license class
        """
        self.tray_icon.setToolTip(
            f"F1 Safety Rating Tracker\nSR: {sr:.2f} ({license_class})"
        )

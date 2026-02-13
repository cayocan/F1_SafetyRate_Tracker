"""
Teste do System Tray Icon
Verifica se o ícone do system tray está funcionando corretamente
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.ui.system_tray import F1TrayIcon
from src.core import Database, SREngine


class MockTracker:
    """Mock tracker for testing"""
    def __init__(self):
        self.db = Database()
        self.sr_engine = SREngine()
        self.sr_engine.set_sr(self.db.get_current_sr())
        self.overlay_window = None
        self.running = True
    
    def stop(self):
        """Stop the tracker"""
        print("[Test] Stopping tracker...")
        self.running = False
        QApplication.quit()


def main():
    print("=" * 70)
    print("TESTE DO SYSTEM TRAY ICON")
    print("=" * 70)
    print()
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when windows close
    
    # Create mock tracker
    tracker = MockTracker()
    
    print(f"Current SR: {tracker.sr_engine.current_sr:.2f}")
    license_class, color = tracker.sr_engine.get_license_class()
    print(f"License Class: {license_class} ({color})")
    print()
    
    # Create system tray icon
    print("Creating system tray icon...")
    tray = F1TrayIcon(app, tracker, web_port=5000)
    tray.show_startup_message()
    
    print()
    print("=" * 70)
    print("System Tray Features:")
    print("  * Left Click: Show current SR info")
    print("  * Double Click: Toggle overlay (not available in test)")
    print("  * Right Click: Context menu with options:")
    print("    - Hide/Show Overlay")
    print("    - Open Dashboard (http://127.0.0.1:5000)")
    print("    - Exit (fecha o app completamente)")
    print("=" * 70)
    print()
    print("O ícone deve aparecer na bandeja do sistema!")
    print("Verifique o ícone vermelho com 'SR' em branco.")
    print()
    print("Pressione Ctrl+C ou clique em 'Exit' no menu para sair.")
    print()
    
    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

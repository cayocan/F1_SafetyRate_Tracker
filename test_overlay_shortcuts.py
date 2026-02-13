"""
Quick test for overlay enhancements
Tests: toggle visibility, simple mode, and resize functionality
"""
import sys
sys.path.insert(0, 'src')

from ui.overlay import SROverlay
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

def get_dummy_stats():
    """Return dummy stats for testing"""
    return {
        'current_sr': 95.3,
        'is_race_active': True,
        'incidents_1x': 1,
        'incidents_2x': 0,
        'incidents_4x': 0,
        'total_incidents': 1,
        'corners_completed': 42,
        'cpi': 42.0,
        'avg_incidents_per_corner': 0.024
    }

def main():
    print("=" * 60)
    print("F1 Safety Rating Overlay - Enhanced Features Test")
    print("=" * 60)
    print()
    print("Testing new features:")
    print("  ✓ Ctrl+Q: Toggle visibility (hide/show)")
    print("  ✓ Ctrl+M: Toggle simple mode")
    print("  ✓ Ctrl++: Increase size")
    print("  ✓ Ctrl+-: Decrease size")
    print("  ✓ Ctrl+0: Reset size")
    print("  ✓ Ctrl+Scroll: Resize with mouse wheel")
    print()
    print("Instructions:")
    print("1. Overlay window will open")
    print("2. Try each keyboard shortcut")
    print("3. Verify functionality works")
    print("4. Close window when done testing")
    print()
    print("=" * 60)
    
    # Create app and overlay
    app = QApplication(sys.argv)
    overlay = SROverlay(update_callback=get_dummy_stats)
    overlay.show()
    
    # Auto-update stats every second for testing
    def update_test():
        overlay.update_display()
    
    timer = QTimer()
    timer.timeout.connect(update_test)
    timer.start(1000)
    
    print("\n[INFO] Overlay displayed. Test the keyboard shortcuts!")
    print("[INFO] Close the overlay window to exit.\n")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

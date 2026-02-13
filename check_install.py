"""
Quick Start Script - F1 Safety Rating Tracker
Run this first to verify installation
"""
import sys
import io

# Fix encoding for Windows terminals
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def check_dependencies():
    """Check if all required packages are installed"""
    required = {
        'PyQt6': 'PyQt6',
        'flask': 'Flask',
        'werkzeug': 'Werkzeug'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"[OK] {package} installed")
        except ImportError:
            print(f"[X] {package} NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n[ERROR] Missing packages: {', '.join(missing)}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    print("\n[OK] All dependencies installed!")
    return True

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("[ERROR] Python 3.8+ required")
        return False
    
    print("[OK] Python version OK")
    return True

def main():
    print("=" * 60)
    print("F1 SAFETY RATING TRACKER - Installation Check")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Ready to start!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Enable UDP telemetry in F1 2019:")
    print("   Settings -> Telemetry -> UDP Telemetry: ON")
    print("   UDP Broadcast Mode: ON")
    print()
    print("2. Run the tracker:")
    print("   python main.py")
    print()
    print("3. Open web dashboard:")
    print("   http://127.0.0.1:5000")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()

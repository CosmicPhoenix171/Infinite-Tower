"""
Build script for Windows desktop (Steam ready)
"""

import subprocess
import sys
import os
import shutil


def build_desktop():
    """Build Windows .exe using PyInstaller."""
    print("="*60)
    print("BUILDING WINDOWS DESKTOP VERSION")
    print("="*60)
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    # Change to infinite-tower-engine directory
    engine_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "infinite-tower-engine")
    os.chdir(engine_dir)
    
    print("\n✓ Building Windows executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=InfiniteTower",
        "--onefile",                          # Single executable
        "--windowed",                         # No console window
        "--add-data=src;src",                 # Include source code
        # Uncomment when you have assets:
        # "--add-data=assets;assets",         # Include assets
        # "--icon=assets/icon.ico",           # App icon
        "demo_16bit_ui.py"                    # Entry point
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Build successful!")
            print(f"\nExecutable location: {os.path.join(engine_dir, 'dist', 'InfiniteTower.exe')}")
            print("\nNext steps for Steam:")
            print("  1. Test the .exe thoroughly")
            print("  2. Create Steam App ID")
            print("  3. Add Steamworks SDK integration")
            print("  4. Package with Steam installer")
            print("  5. Upload to Steam Partner portal")
            
            # Create a release folder
            release_dir = os.path.join(engine_dir, "release")
            os.makedirs(release_dir, exist_ok=True)
            
            exe_path = os.path.join(engine_dir, "dist", "InfiniteTower.exe")
            if os.path.exists(exe_path):
                shutil.copy(exe_path, os.path.join(release_dir, "InfiniteTower.exe"))
                print(f"\n✓ Executable copied to: {release_dir}")
                
        else:
            print("✗ Build failed!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = build_desktop()
    sys.exit(0 if success else 1)

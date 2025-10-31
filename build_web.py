"""
Build script for web deployment (GitHub Pages)
"""

import subprocess
import sys
import os


def build_web():
    """Build web version using Pygbag."""
    print("="*60)
    print("BUILDING WEB VERSION (PYGBAG)")
    print("="*60)
    
    # Check if pygbag is installed
    try:
        import pygbag
        print("✓ Pygbag found")
    except ImportError:
        print("✗ Pygbag not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygbag"])
        print("✓ Pygbag installed")
    
    # Build command
    print("\n✓ Building web version...")
    print("  This will create a build/ directory with WebAssembly files")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Build with pygbag
        result = subprocess.run(
            [sys.executable, "-m", "pygbag", "--build", "infinite-tower-engine"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Build successful!")
            print("\nTo test locally:")
            print("  python -m pygbag infinite-tower-engine")
            print("\nFor GitHub Pages:")
            print("  1. Copy build/web/ contents to docs/ folder")
            print("  2. Push to GitHub")
            print("  3. Enable Pages in repo settings")
            print("  4. Your game will be at: https://username.github.io/repo-name/")
        else:
            print("✗ Build failed!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = build_web()
    sys.exit(0 if success else 1)

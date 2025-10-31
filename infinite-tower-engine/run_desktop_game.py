"""
Convenience launcher for the full desktop game.

Runs the main game loop from src/infinite_tower/main.py using the shared engine code.
"""
import os
import sys

# Ensure the src directory is on the path
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from infinite_tower.main import main

if __name__ == "__main__":
    main()

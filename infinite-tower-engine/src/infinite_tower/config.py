"""
Infinite Tower Engine - Configuration Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
Commercial Product Under Development - Unauthorized Use Prohibited.

This module contains proprietary configuration settings for the Infinite Tower Engine,
a commercial video game product. This code is protected by copyright law and trade 
secret protection. Any unauthorized use, copying, or distribution is strictly 
prohibited and may result in legal action.
"""

# Display Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FRAME_RATE = 60  # Renamed from FPS for clarity
TITLE = "Infinite Tower Engine"
FULLSCREEN = False
DEBUG_MODE = True

# Colors (RGB tuples)
BACKGROUND_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player Settings
PLAYER_START_POSITION = (400, 300)  # Changed to tuple for consistency
PLAYER_HEALTH = 100
PLAYER_SPEED = 5

# Enemy Settings
ENEMY_SPAWN_RATE = 1.0
ENEMY_HEALTH = 50
ENEMY_SPEED = 2

# Loot Settings
LOOT_DROP_RATE = 0.1

# Floor Generation Settings
MAX_FLOORS = 100
FLOOR_HEIGHT = 50
FLOOR_WIDTH = 800

# Audio Settings
MASTER_VOLUME = 0.8
SOUND_EFFECTS_VOLUME = 0.7
MUSIC_VOLUME = 0.5
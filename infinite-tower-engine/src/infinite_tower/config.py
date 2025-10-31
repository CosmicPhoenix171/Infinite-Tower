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
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
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
PLAYER_SPEED = 48  # Doubled again to 48 for ultra-fast movement

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

# Combat Settings
BASE_ATTACK_DAMAGE = 10
BASE_DEFENSE = 0
CRITICAL_HIT_CHANCE = 0.15
CRITICAL_HIT_MULTIPLIER = 1.5
ATTACK_COOLDOWN_FRAMES = 30

# UI Settings
HUD_PADDING = 10
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 20
MINIMAP_SIZE = 150
INVENTORY_SLOTS = 40

# Physics Settings
GRAVITY = 0.5
FRICTION = 0.9
MAX_VELOCITY = 10.0

# AI Settings
AI_UPDATE_FREQUENCY = 1  # Updates per frame
AI_DETECTION_RANGE = 200
AI_ATTACK_RANGE = 50

# Game Settings
STARTING_FLOOR = 1
DIFFICULTY_MULTIPLIER = 1.0
PERMADEATH = False

# Performance Settings
MAX_PARTICLES = 100
MAX_ENEMIES_PER_FLOOR = 20
RENDER_DISTANCE = 1000

# File Paths
ASSETS_PATH = "assets/"
FONTS_PATH = "assets/fonts/"
SOUNDS_PATH = "assets/sounds/"
SPRITES_PATH = "assets/sprites/"
SAVE_PATH = "saves/"

# Additional Colors
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Rarity Colors (matching loot system)
COLOR_COMMON = (200, 200, 200)
COLOR_UNCOMMON = (100, 255, 100)
COLOR_RARE = (100, 100, 255)
COLOR_EPIC = (200, 100, 255)
COLOR_LEGENDARY = (255, 150, 0)


class GameConfig:
    """
    Dynamic configuration manager with save/load support.
    """
    
    def __init__(self):
        self.settings = {
            # Graphics
            'screen_width': SCREEN_WIDTH,
            'screen_height': SCREEN_HEIGHT,
            'fullscreen': FULLSCREEN,
            'frame_rate': FRAME_RATE,
            'vsync': True,
            
            # Audio
            'master_volume': MASTER_VOLUME,
            'sfx_volume': SOUND_EFFECTS_VOLUME,
            'music_volume': MUSIC_VOLUME,
            'audio_enabled': True,
            
            # Gameplay
            'difficulty': 1.0,
            'permadeath': PERMADEATH,
            'auto_save': True,
            
            # Controls
            'move_up': 'w',
            'move_down': 's',
            'move_left': 'a',
            'move_right': 'd',
            'attack': 'space',
            'interact': 'e',
            'inventory': 'i',
            'pause': 'escape',
            
            # Debug
            'debug_mode': DEBUG_MODE,
            'show_fps': False,
            'show_hitboxes': False,
        }
    
    def get(self, key: str, default=None):
        """Get a configuration value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a configuration value."""
        self.settings[key] = value
    
    def save_to_file(self, filepath: str = "config.json"):
        """Save configuration to file."""
        import json
        try:
            with open(filepath, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def load_from_file(self, filepath: str = "config.json"):
        """Load configuration from file."""
        import json
        try:
            with open(filepath, 'r') as f:
                loaded_settings = json.load(f)
                self.settings.update(loaded_settings)
            return True
        except FileNotFoundError:
            print(f"Config file not found: {filepath}")
            return False
        except Exception as e:
            print(f"Failed to load config: {e}")
            return False
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.__init__()
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if all values are valid
        """
        # Validate screen dimensions
        if self.settings['screen_width'] < 640 or self.settings['screen_height'] < 480:
            return False
        
        # Validate volumes (0.0 to 1.0)
        for key in ['master_volume', 'sfx_volume', 'music_volume']:
            if not 0.0 <= self.settings[key] <= 1.0:
                return False
        
        # Validate frame rate
        if not 30 <= self.settings['frame_rate'] <= 240:
            return False
        
        return True


# Global config instance
game_config = GameConfig()
import pygame
import os
import logging
from typing import Optional, Dict, Any


class ResourceLoader:
    """
    Enhanced resource loading and management system.
    
    Handles loading and caching of game assets including sprites, sounds, and fonts
    with error handling and fallback asset support.
    """
    
    def __init__(self, assets_root: str = "assets"):
        self.assets_root = assets_root
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Create placeholder assets
        self._create_placeholder_assets()

    def _create_placeholder_assets(self):
        """Create basic placeholder assets to prevent crashes when assets are missing."""
        # Create a simple colored rectangle as placeholder sprite
        placeholder_sprite = pygame.Surface((32, 32))
        placeholder_sprite.fill((255, 0, 255))  # Magenta to make it obvious
        self.sprites['placeholder'] = placeholder_sprite
        
        # Default font (system font)
        self.fonts['default'] = pygame.font.Font(None, 24)

    def load_sprite(self, name: str, path: str) -> Optional[pygame.Surface]:
        """Load a sprite image with error handling."""
        try:
            full_path = os.path.join(self.assets_root, 'sprites', path)
            sprite = pygame.image.load(full_path).convert_alpha()
            self.sprites[name] = sprite
            self.logger.info(f"Loaded sprite: {name} from {full_path}")
            return sprite
        except (pygame.error, FileNotFoundError) as e:
            self.logger.warning(f"Failed to load sprite '{name}' from '{path}': {e}")
            # Return placeholder sprite
            return self.sprites.get('placeholder')

    def load_sound(self, name: str, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound file with error handling."""
        try:
            full_path = os.path.join(self.assets_root, 'sounds', path)
            sound = pygame.mixer.Sound(full_path)
            self.sounds[name] = sound
            self.logger.info(f"Loaded sound: {name} from {full_path}")
            return sound
        except (pygame.error, FileNotFoundError) as e:
            self.logger.warning(f"Failed to load sound '{name}' from '{path}': {e}")
            return None

    def load_font(self, name: str, path: str, size: int) -> Optional[pygame.font.Font]:
        """Load a font file with error handling."""
        try:
            full_path = os.path.join(self.assets_root, 'fonts', path)
            font = pygame.font.Font(full_path, size)
            self.fonts[name] = font
            self.logger.info(f"Loaded font: {name} from {full_path}")
            return font
        except (pygame.error, FileNotFoundError) as e:
            self.logger.warning(f"Failed to load font '{name}' from '{path}': {e}")
            # Return default system font
            return pygame.font.Font(None, size)

    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a loaded sprite, returning placeholder if not found."""
        return self.sprites.get(name, self.sprites.get('placeholder'))

    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Get a loaded sound."""
        return self.sounds.get(name)

    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Get a loaded font, returning default if not found."""
        return self.fonts.get(name, self.fonts.get('default'))

    def clear_assets(self):
        """Clear all loaded assets to free memory."""
        self.sprites.clear()
        self.sounds.clear()
        self.fonts.clear()
        self._create_placeholder_assets()  # Recreate placeholders
        self.logger.info("Cleared all assets")

    def preload_assets(self):
        """Preload common assets at game startup."""
        # Load placeholder assets that should always be available
        common_assets = {
            'sprites': [],  # Add common sprite files here
            'sounds': [],   # Add common sound files here  
            'fonts': []     # Add common font files here
        }
        
        for sprite_path in common_assets['sprites']:
            self.load_sprite(os.path.basename(sprite_path), sprite_path)
            
        for sound_path in common_assets['sounds']:
            self.load_sound(os.path.basename(sound_path), sound_path)
            
        for font_data in common_assets['fonts']:
            if isinstance(font_data, tuple) and len(font_data) == 3:
                name, path, size = font_data
                self.load_font(name, path, size)
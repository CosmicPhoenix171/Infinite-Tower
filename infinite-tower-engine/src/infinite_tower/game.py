import pygame
import logging
from typing import Optional

from .utils.input_handler import InputHandler
from .resources.loader import ResourceLoader
from . import config


class Game:
    """
    Infinite Tower Engine - Core Game Engine

    Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
    Proprietary Commercial Software - Trade Secret Information.

    This class contains proprietary game engine technology and algorithms for the
    Infinite Tower Engine commercial video game. The code, design patterns, and
    implementation details constitute valuable trade secrets and are protected by
    copyright law. Unauthorized access, use, copying, or distribution is prohibited.
    """
    
    def __init__(self):
        self.is_running = False
        self.screen: Optional[pygame.Surface] = None
        self.clock = pygame.time.Clock()
        
        # Initialize systems
        self.input_handler = InputHandler()
        self.resource_loader = ResourceLoader()
        
        # Game state
        self.current_state = "menu"  # menu, playing, paused, game_over
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize pygame systems
        self._init_pygame()

    def _init_pygame(self):
        """Initialize pygame and create the main screen."""
        try:
            pygame.init()
            
            # Try to initialize audio, but don't fail if it's not available
            try:
                pygame.mixer.init()
                self.logger.info("Audio system initialized")
            except pygame.error as e:
                self.logger.warning(f"Audio initialization failed: {e}. Continuing without audio.")
            
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            pygame.display.set_caption(config.TITLE)
            self.logger.info("Pygame initialized successfully")
        except pygame.error as e:
            self.logger.error(f"Failed to initialize pygame: {e}")
            raise

    def start(self):
        """Start the game and enter the main loop."""
        self.is_running = True
        self.logger.info("Game started")

    def pause(self):
        """Pause the game."""
        if self.current_state == "playing":
            self.current_state = "paused"
            self.logger.info("Game paused")

    def resume(self):
        """Resume the game from pause."""
        if self.current_state == "paused":
            self.current_state = "playing"
            self.logger.info("Game resumed")

    def end(self):
        """End the game and cleanup resources."""
        self.is_running = False
        self.cleanup()
        self.logger.info("Game ended")

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.end()
                return
            
            # Pass event to input handler
            self.input_handler.handle_event(event)
            
            # Handle pause/resume (ESC key)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "playing":
                        self.pause()
                    elif self.current_state == "paused":
                        self.resume()

    def update(self):
        """Update game state."""
        if not self.is_running:
            return
            
        # Update input handler
        self.input_handler.update()
        
        # Update based on current game state
        if self.current_state == "menu":
            self._update_menu()
        elif self.current_state == "playing":
            self._update_gameplay()
        elif self.current_state == "paused":
            self._update_pause()
        elif self.current_state == "game_over":
            self._update_game_over()

    def _update_menu(self):
        """Update menu state."""
        # Simple menu navigation - no complex menu system needed yet
        if self.input_handler.get_key(pygame.K_RETURN):
            self.current_state = "playing"
            self.logger.info("Transitioning to gameplay")
        elif self.input_handler.get_key(pygame.K_q):
            self.end()
            self.logger.info("Quit from main menu")

    def _update_gameplay(self):
        """Update gameplay state."""
        # TODO: Update game entities, systems, etc.
        pass

    def _update_pause(self):
        """Update pause state."""
        # Pause screen is mostly static, just wait for resume
        pass

    def _update_game_over(self):
        """Update game over state."""
        # TODO: Handle game over logic, restart options, etc.
        pass

    def render(self, screen: pygame.Surface):
        """
        Render the current game state to the provided screen.
        
        Args:
            screen: The pygame surface to render to
        """
        if not screen:
            return
            
        # Clear screen
        screen.fill(config.BACKGROUND_COLOR)
        
        # Render based on current game state
        if self.current_state == "menu":
            self._render_menu(screen)
        elif self.current_state == "playing":
            self._render_gameplay(screen)
        elif self.current_state == "paused":
            self._render_pause(screen)
        elif self.current_state == "game_over":
            self._render_game_over(screen)

    def _render_menu(self, screen: pygame.Surface):
        """Render the main menu."""
        font = self.resource_loader.get_font('default')
        big_font = pygame.font.Font(None, 48)
        
        # Background
        screen.fill(config.BLACK)
        
        # Title (bigger and more prominent)
        title_text = big_font.render("INFINITE TOWER", True, config.WHITE)
        title_rect = title_text.get_rect(center=(config.SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = font.render("Engine v0.1.0", True, (150, 150, 150))
        subtitle_rect = subtitle_text.get_rect(center=(config.SCREEN_WIDTH // 2, 190))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Menu options
        start_text = font.render("Press ENTER to Start Game", True, config.GREEN)
        start_rect = start_text.get_rect(center=(config.SCREEN_WIDTH // 2, 280))
        screen.blit(start_text, start_rect)
        
        quit_text = font.render("Press Q to Quit", True, config.RED)
        quit_rect = quit_text.get_rect(center=(config.SCREEN_WIDTH // 2, 320))
        screen.blit(quit_text, quit_rect)
        
        # Copyright notice
        copyright_text = pygame.font.Font(None, 18).render("© 2025 CosmicPhoenix171 - All Rights Reserved", True, (100, 100, 100))
        copyright_rect = copyright_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT - 30))
        screen.blit(copyright_text, copyright_rect)

    def _render_gameplay(self, screen: pygame.Surface):
        """Render the main gameplay."""
        # Simple gameplay placeholder
        screen.fill((20, 20, 40))  # Dark blue background
        
        font = self.resource_loader.get_font('default')
        
        # Game world placeholder (simple floor representation)
        pygame.draw.rect(screen, (100, 50, 0), (50, 50, config.SCREEN_WIDTH - 100, config.SCREEN_HEIGHT - 100))  # Floor
        pygame.draw.rect(screen, (150, 75, 0), (50, 50, config.SCREEN_WIDTH - 100, config.SCREEN_HEIGHT - 100), 3)  # Border
        
        # Player placeholder (simple rectangle)
        pygame.draw.rect(screen, config.GREEN, (400, 300, 20, 20))
        
        # UI Elements
        ui_text = font.render("FLOOR 1", True, config.WHITE)
        screen.blit(ui_text, (10, 10))
        
        health_text = font.render("HEALTH: 100/100", True, config.RED)
        screen.blit(health_text, (10, 40))
        
        controls_text = font.render("Press ESC to pause", True, config.WHITE)
        screen.blit(controls_text, (10, config.SCREEN_HEIGHT - 30))

    def _render_pause(self, screen: pygame.Surface):
        """Render the pause screen."""
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        overlay.fill(config.BLACK)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        font = self.resource_loader.get_font('default')
        pause_text = font.render("PAUSED - Press ESC to resume", True, config.WHITE)
        pause_rect = pause_text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)

    def _render_game_over(self, screen: pygame.Surface):
        """Render the game over screen."""
        font = self.resource_loader.get_font('default')
        text = font.render("Game Over", True, config.RED)
        text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)

    def cleanup(self):
        """Cleanup resources before exiting."""
        if self.resource_loader:
            self.resource_loader.clear_assets()
        
        try:
            # Only quit mixer if it was initialized
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.quit()
            self.logger.info("Pygame cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
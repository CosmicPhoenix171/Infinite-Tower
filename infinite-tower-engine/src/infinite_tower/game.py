import pygame
import logging
from typing import Optional

from .utils.input_handler import InputHandler
from .resources.loader import ResourceLoader
from . import config
from .entities.player import Player
from .entities.enemy import Enemy, EnemyType
from .ui.game_ui import GameUI
from .ui.inventory import InventoryUI
from .systems.combat import CombatSystem
from .systems.physics import Physics
from .items.loot import LootGenerator


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
        self.dt: float = 0.0
        
        # World/systems (initialized on play)
        self.player: Optional[Player] = None
        self.enemies: list[Enemy] = []
        self.game_ui: Optional[GameUI] = None
        self.inventory_ui: Optional[InventoryUI] = None
        self.combat_system: Optional[CombatSystem] = None
        self.physics: Optional[Physics] = None
        self.loot_gen: Optional[LootGenerator] = None
        
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
            
            flags = pygame.SCALED | pygame.RESIZABLE
            self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags)
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
            
            # Inventory overlay consumes input first when visible
            if self.inventory_ui and self.inventory_ui.handle_input(event):
                continue
            
            # Pass event to input handler
            self.input_handler.handle_event(event)
            
            # Handle pause/resume (ESC key)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "playing":
                        self.pause()
                    elif self.current_state == "paused":
                        self.resume()
                elif event.key == pygame.K_e:
                    if self.game_ui:
                        self.game_ui.toggle_equipment()
                elif event.key == pygame.K_TAB or event.key == pygame.K_i:
                    if self.inventory_ui:
                        self.inventory_ui.toggle()
                elif event.key == pygame.K_f:
                    # Optional fullscreen toggle
                    try:
                        pygame.display.toggle_fullscreen()
                    except Exception:
                        pass
                elif event.key == pygame.K_RETURN:
                    # Dismiss dialog if showing
                    if self.game_ui and getattr(self.game_ui, 'current_dialog', None):
                        self.game_ui.hide_dialog()
            elif event.type == pygame.VIDEORESIZE:
                # Recreate surface with new size
                flags = pygame.SCALED | pygame.RESIZABLE
                self.screen = pygame.display.set_mode((event.w, event.h), flags)
                # Update UI surfaces
                if self.game_ui:
                    self.game_ui.screen = self.screen
                if self.inventory_ui:
                    self.inventory_ui.screen = self.screen

    def update(self, dt: float = 0.0):
        """Update game state."""
        if not self.is_running:
            return
            
        # Update input handler
        self.input_handler.update()
        self.dt = dt if dt > 0 else (1.0 / config.FRAME_RATE)
        
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
            self._start_play()
            self.logger.info("Transitioning to gameplay")
        elif self.input_handler.get_key(pygame.K_q):
            self.end()
            self.logger.info("Quit from main menu")

    def _start_play(self):
        """Initialize world, systems, and UI for gameplay."""
        # Systems
        self.combat_system = CombatSystem()
        self.physics = Physics()
        self.loot_gen = LootGenerator(seed=12345)
        
        # Player
        self.player = Player("Hero", health=100, position=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        # UI-related attributes
        self.player.level = 5
        self.player.exp = 350
        self.player.max_exp = 500
        self.player.mana = 75
        self.player.max_mana = 100
        self.player.stamina = 100
        self.player.max_stamina = 100
        self.player.equipment = []
        
        # Starter loot
        for _ in range(5):
            item = self.loot_gen.generate_random_item(floor_level=1)
            self.player.add_to_inventory(item)
        
        # Enemies
        self.enemies = [
            Enemy("Goblin", health=30, damage=5, speed=2, position=(200, 150), enemy_type=EnemyType.FAST),
            Enemy("Orc", health=80, damage=12, speed=1, position=(600, 200), enemy_type=EnemyType.TANK),
            Enemy("Skeleton", health=40, damage=8, speed=2.5, position=(400, 400), enemy_type=EnemyType.RANGER),
        ]
        
        # UI
        self.game_ui = GameUI(self.screen, self.player)
        self.game_ui.set_floor(1, "Entrance Hall")
        self.game_ui.show_equipment = True
        self.inventory_ui = InventoryUI(self.screen, self.player)
        self.game_ui.add_notification("Game Started!", self.game_ui.COLORS['text_green'])
        self.game_ui.add_notification("Welcome to Floor 1", self.game_ui.COLORS['text_yellow'])
        
        self.current_state = "playing"

    def _update_gameplay(self):
        """Update gameplay state."""
        if not (self.player and self.physics and self.combat_system and self.game_ui):
            return
        dt = self.dt
        
        # Player input and update (freeze movement when inventory open)
        if not (self.inventory_ui and self.inventory_ui.is_visible):
            self.player.handle_input(self.input_handler)
        self.player.update(dt)
        
        # Stamina regen/drain
        if getattr(self.player, 'is_sprinting', False) and getattr(self.player, 'is_moving', False):
            self.player.stamina = max(0, self.player.stamina - 0.5)
        else:
            self.player.stamina = min(self.player.max_stamina, self.player.stamina + 0.3)
        
        # Enemies
        for enemy in self.enemies[:]:
            if enemy.is_alive():
                enemy.update(self.player, dt)
            else:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.game_ui.add_notification(f"Defeated {enemy.name}!", self.game_ui.COLORS['text_green'])
                    self.player.exp += 50
                    if self.player.exp >= self.player.max_exp:
                        self.player.level += 1
                        self.player.exp = 0
                        self.game_ui.add_notification(f"Level Up! Now Level {self.player.level}", self.game_ui.COLORS['text_yellow'])
        
        # Combat - player attacks
        if getattr(self.player, 'is_attacking', False):
            attack_rect = self.player.get_attack_rect()
            for enemy in self.enemies:
                if self.physics.check_collision(attack_rect, enemy.rect):
                    result = self.combat_system.perform_attack(self.player, enemy)
                    self.game_ui.add_damage_number(result.damage, enemy.position[0], enemy.position[1] - 20, self.game_ui.COLORS['text_red'])
                    if result.was_critical:
                        self.game_ui.add_notification("Critical Hit!", self.game_ui.COLORS['text_yellow'])
        
        # Combat - enemy attacks
        for enemy in self.enemies:
            if enemy.is_attacking and self.physics.check_collision(enemy.get_attack_rect(), self.player.rect):
                result = self.combat_system.perform_attack(enemy, self.player)
                self.game_ui.add_damage_number(result.damage, self.player.position[0], self.player.position[1] - 20, self.game_ui.COLORS['text_red'])
                if not self.player.is_alive():
                    self.game_ui.show_dialog("You have been defeated!", speaker="Game Over")
                    self.current_state = "game_over"

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
        # Background gradient
        sw, sh = screen.get_size()
        for y in range(sh):
            color_val = int(20 + (y / max(1, sh)) * 30)
            pygame.draw.line(screen, (color_val, color_val // 2, color_val // 3), (0, y), (sw, y))
        
        # Floor area
        floor_rect = pygame.Rect(60, 60, sw - 120, sh - 140)
        pygame.draw.rect(screen, (40, 35, 30), floor_rect)
        pygame.draw.rect(screen, (80, 70, 60), floor_rect, 2)
        
        # Grid
        grid_size = 32
        grid_color = (50, 45, 40)
        for x in range(floor_rect.left, floor_rect.right, grid_size):
            pygame.draw.line(screen, grid_color, (x, floor_rect.top), (x, floor_rect.bottom), 1)
        for y in range(floor_rect.top, floor_rect.bottom, grid_size):
            pygame.draw.line(screen, grid_color, (floor_rect.left, y), (floor_rect.right, y), 1)
        
        # Entities
        if self.enemies:
            for enemy in self.enemies:
                enemy.draw(screen)
        if self.player:
            self.player.draw(screen)
        
        # UI
        if self.game_ui:
            self.game_ui.draw()
        if self.inventory_ui:
            self.inventory_ui.draw()

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
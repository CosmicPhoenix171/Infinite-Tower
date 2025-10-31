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
from . import __version__ as ENGINE_VERSION


class Game:
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

        # Setup logging FIRST
        self.logger = logging.getLogger(__name__)

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

        # Initialize pygame systems
        self._init_pygame()

    def start(self):
        """Start the game and enter the main loop."""
        # Pause/settings UI state
        self.pause_substate = None  # None, 'settings'
        self.settings_tab = 'sound'  # 'sound', 'graphics', 'keybinds'
        self.settings_temp = {}
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
            
            # Pass event to input handler (except when paused and clicking pause menu)
            self.input_handler.handle_event(event)
            
            # Handle pause/resume (ESC key)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.current_state == "playing":
                        self.pause()
                        # avoid processing this same event as 'paused' below
                        continue
                    elif self.current_state == "paused":
                        self.resume()
                        continue
                # When paused, only allow Quit (Q) or Resume (ESC handled above)
                if self.current_state == "paused":
                    if event.key == pygame.K_q:
                        self.end()
                        return
                    # ignore other keys while paused
                    continue
                elif event.key == pygame.K_e:
                    if self.game_ui:
                        self.game_ui.toggle_equipment()
                elif event.key == pygame.K_TAB or event.key == pygame.K_i or event.key == pygame.K_o:
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
            # Remove keyup-based toggling to ensure Tab is a true toggle (no press-and-hold behavior)
            elif event.type == pygame.KEYUP:
                pass
            # Pause menu mouse handling
            if self.current_state == "paused":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = self._compute_pause_buttons()
                    if buttons['resume'].collidepoint(event.pos):
                        self.resume()
                        return
                    if buttons['quit'].collidepoint(event.pos):
                        self.end()
                        return
                # Game over screen mouse handling
                if self.current_state == "game_over":
                    if hasattr(self, '_game_over_restart_rect'):
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if self._game_over_restart_rect.collidepoint(event.pos):
                                self._start_play()
                                return
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
        
        # Prevent player and enemies from overlapping
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                # Simple push-back: move player away from enemy
                dx = self.player.rect.centerx - enemy.rect.centerx
                dy = self.player.rect.centery - enemy.rect.centery
                if abs(dx) > abs(dy):
                    # Push horizontally
                    if dx > 0:
                        self.player.position[0] += 2
                    else:
                        self.player.position[0] -= 2
                else:
                    # Push vertically
                    if dy > 0:
                        self.player.position[1] += 2
                    else:
                        self.player.position[1] -= 2
                # Update player rect after push
                self.player.rect.x = int(self.player.position[0] - self.player.size // 2)
                self.player.rect.y = int(self.player.position[1] - self.player.size // 2)
        
        # Stamina regen/drain
        if getattr(self.player, 'is_sprinting', False) and getattr(self.player, 'is_moving', False):
            self.player.stamina = max(0, self.player.stamina - 0.5)
        else:
            self.player.stamina = min(self.player.max_stamina, self.player.stamina + 0.3)
        
        # Enemies
        for enemy in self.enemies[:]:
            if enemy.is_alive():
                enemy.update(self.player, dt)
                # Enemy attacks player if close enough and not on cooldown
                if enemy.attack_cooldown == 0 and enemy.rect.colliderect(self.player.rect):
                    enemy.is_attacking = True
                    enemy.attack_cooldown = 60  # 1 second at 60 FPS
                    self.player.take_damage(enemy.damage)
                    self.game_ui.add_damage_number(enemy.damage, self.player.position[0], self.player.position[1] - 20, self.game_ui.COLORS['text_red'])
                    if not self.player.is_alive():
                        self.game_ui.show_dialog("You have been defeated!", speaker="Game Over")
                        self.current_state = "game_over"
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
        
        # Subtitle (engine version)
        subtitle_text = font.render(f"Engine v{ENGINE_VERSION}", True, (150, 150, 150))
        subtitle_rect = subtitle_text.get_rect(center=(config.SCREEN_WIDTH // 2, 190))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Menu options
        start_text = font.render("Press ENTER to Start Game", True, config.GREEN)
        start_rect = start_text.get_rect(center=(config.SCREEN_WIDTH // 2, 280))
        screen.blit(start_text, start_rect)
        # Focus hint for web
        hint_text = font.render("Click the game area to focus. I/Tab/O: Inventory (in game)", True, (180, 180, 180))
        hint_rect = hint_text.get_rect(center=(config.SCREEN_WIDTH // 2, 320))
        screen.blit(hint_text, hint_rect)

        quit_text = font.render("Press Q to Quit", True, config.RED)
        quit_rect = quit_text.get_rect(center=(config.SCREEN_WIDTH // 2, 360))
        screen.blit(quit_text, quit_rect)
        
        # Bottom-left version label
        ver_font = pygame.font.Font(None, 28)
        ver_text = ver_font.render(f"v{ENGINE_VERSION}", True, (220, 220, 120))
        # Simple shadow for readability
        screen.blit(ver_font.render(f"v{ENGINE_VERSION}", True, config.BLACK), (12, config.SCREEN_HEIGHT - 34))
        screen.blit(ver_text, (10, config.SCREEN_HEIGHT - 36))

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
        sw, sh = screen.get_size()
        overlay = pygame.Surface((sw, sh))
        overlay.fill(config.BLACK)
        overlay.set_alpha(140)
        screen.blit(overlay, (0, 0))

        # Panel
        panel_w, panel_h = 420, 220
        panel_x = (sw - panel_w) // 2
        panel_y = (sh - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (34, 34, 48), panel_rect)
        pygame.draw.rect(screen, config.WHITE, panel_rect, 2)

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Paused", True, config.WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_w // 2, panel_y + 48))
        screen.blit(title, title_rect)

        # Buttons
        buttons = self._compute_pause_buttons()
        btn_font = pygame.font.Font(None, 36)
        for name, rect in buttons.items():
            label = "Resume" if name == 'resume' else "Quit"
            # Button look
            pygame.draw.rect(screen, (60, 60, 80), rect)
            pygame.draw.rect(screen, config.WHITE, rect, 2)
            txt = btn_font.render(label, True, config.WHITE)
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)

    def _render_game_over(self, screen: pygame.Surface):
        """Render the game over screen."""
    font = self.resource_loader.get_font('default')
    text = font.render("Game Over", True, config.RED)
    text_rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 - 40))
    screen.blit(text, text_rect)

    # Restart button
    btn_font = pygame.font.Font(None, 36)
    restart_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 80, config.SCREEN_HEIGHT // 2 + 20, 160, 48)
    pygame.draw.rect(screen, (60, 60, 80), restart_rect)
    pygame.draw.rect(screen, config.WHITE, restart_rect, 2)
    restart_txt = btn_font.render("Restart", True, config.WHITE)
    restart_txt_rect = restart_txt.get_rect(center=restart_rect.center)
    screen.blit(restart_txt, restart_txt_rect)

    # Store for click detection
    self._game_over_restart_rect = restart_rect

    def _compute_pause_buttons(self):
        """Compute Resume and Quit button rects relative to current screen size."""
        sw, sh = self.screen.get_size() if self.screen else (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        panel_w, panel_h = 420, 220
        panel_x = (sw - panel_w) // 2
        panel_y = (sh - panel_h) // 2
        btn_w, btn_h = 160, 44
        gap = 24
        resume_rect = pygame.Rect(panel_x + (panel_w - (btn_w * 2 + gap)) // 2,
                                  panel_y + panel_h - 80,
                                  btn_w, btn_h)
        quit_rect = pygame.Rect(resume_rect.right + gap,
                                 resume_rect.top,
                                 btn_w, btn_h)
        return {'resume': resume_rect, 'quit': quit_rect}

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
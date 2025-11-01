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
            pygame.font.init()  # Ensure font module is initialized
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
                            if self._game_over_quit_rect.collidepoint(event.pos):
                                self.end()
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
        self.player = Player("Hero", health=10000, position=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        # UI-related attributes
        self.player.max_health = 10000
        self.player.health = 10000
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
        
        # Maintain minimum distance between player and enemies (prevent clipping)
        for enemy in self.enemies:
            # Calculate minimum distance (sum of radii)
            min_distance = (self.player.size // 2) + (enemy.size // 2) + 15  # 15 pixel buffer
            
            # Calculate current distance
            dx = enemy.rect.centerx - self.player.rect.centerx
            dy = enemy.rect.centery - self.player.rect.centery
            current_distance = (dx**2 + dy**2)**0.5
            
            # If too close, push away
            if current_distance < min_distance and current_distance > 0:
                # Normalize and push
                push_distance = min_distance - current_distance
                push_x = (dx / current_distance) * push_distance
                push_y = (dy / current_distance) * push_distance
                
                enemy.position[0] += push_x
                enemy.position[1] += push_y
                
                # Update enemy rect after push
                enemy.rect.x = int(enemy.position[0] - enemy.size // 2)
                enemy.rect.y = int(enemy.position[1] - enemy.size // 2)
        
        # Also prevent enemies from overlapping each other
        for i, enemy1 in enumerate(self.enemies):
            for enemy2 in self.enemies[i + 1:]:
                min_distance = (enemy1.size // 2) + (enemy2.size // 2) + 5
                dx = enemy2.rect.centerx - enemy1.rect.centerx
                dy = enemy2.rect.centery - enemy1.rect.centery
                current_distance = (dx**2 + dy**2)**0.5
                
                if current_distance < min_distance and current_distance > 0:
                    # Push both enemies apart equally
                    push_distance = (min_distance - current_distance) / 2
                    push_x = (dx / current_distance) * push_distance
                    push_y = (dy / current_distance) * push_distance
                    
                    enemy1.position[0] -= push_x
                    enemy1.position[1] -= push_y
                    enemy2.position[0] += push_x
                    enemy2.position[1] += push_y
                    
                    # Update rects
                    enemy1.rect.x = int(enemy1.position[0] - enemy1.size // 2)
                    enemy1.rect.y = int(enemy1.position[1] - enemy1.size // 2)
                    enemy2.rect.x = int(enemy2.position[0] - enemy2.size // 2)
                    enemy2.rect.y = int(enemy2.position[1] - enemy2.size // 2)
        
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
            if not hasattr(self.player, '_attack_processed') or not self.player._attack_processed:
                attack_rect = self.player.get_attack_rect()
                for enemy in self.enemies:
                    if self.physics.check_collision(attack_rect, enemy.rect):
                        result = self.combat_system.perform_attack(self.player, enemy)
                        self.game_ui.add_damage_number(result.damage, enemy.position[0], enemy.position[1] - 20, self.game_ui.COLORS['text_red'])
                        if result.was_critical:
                            self.game_ui.add_notification("Critical Hit!", self.game_ui.COLORS['text_yellow'])
                self.player._attack_processed = True
        else:
            self.player._attack_processed = False
        
        # Combat - enemy attacks (only if player is in attack hitbox)
        for enemy in self.enemies:
            # Check if player is in enemy's attack rect
            player_in_attack_rect = self.physics.check_collision(enemy.get_attack_rect(), self.player.rect)
            
            # Initialize last attack time if not set
            if not hasattr(enemy, '_last_attack_time'):
                enemy._last_attack_time = 0
            
            # Check if cooldown has elapsed since last attack
            current_time = enemy.attack_cooldown  # This counts down, so we check if it reached 0
            
            # If player is in attack rect and cooldown is ready (reached 0)
            if player_in_attack_rect and enemy.attack_cooldown == 0:
                # Attack!
                enemy.is_attacking = True
                result = self.combat_system.perform_attack(enemy, self.player)
                self.game_ui.add_damage_number(result.damage, self.player.position[0], self.player.position[1] - 20, self.game_ui.COLORS['text_red'])
                print(f"Enemy attack: {enemy.name} hits for {result.damage}")
                # Reset cooldown for next attack
                enemy.attack_cooldown = enemy.base_attack_cooldown
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
        sw, sh = screen.get_size()
        
        # Modern gradient background (dark blue to purple)
        for y in range(sh):
            ratio = y / max(1, sh)
            r = int(15 + ratio * 40)
            g = int(10 + ratio * 20)
            b = int(30 + ratio * 60)
            pygame.draw.line(screen, (r, g, b), (0, y), (sw, y))
        
        # Decorative top gradient overlay
        top_overlay = pygame.Surface((sw, 200))
        for y in range(200):
            ratio = y / 200
            alpha = int(255 * (1 - ratio) * 0.3)
            color = (100 + int(ratio * 50), 50 + int(ratio * 30), 150 + int(ratio * 50))
            pygame.draw.line(top_overlay, color, (0, y), (sw, y))
        top_overlay.set_alpha(100)
        screen.blit(top_overlay, (0, 0))
        
        # Title with modern styling
        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render("INFINITE TOWER", True, (255, 200, 100))
        title_rect = title_text.get_rect(center=(sw // 2, 100))
        # Title glow effect (shadow)
        glow_text = title_font.render("INFINITE TOWER", True, (150, 100, 50))
        glow_rect = glow_text.get_rect(center=(sw // 2 + 3, 103))
        screen.blit(glow_text, glow_rect)
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 24)
        subtitle_text = subtitle_font.render(f"Engine v{ENGINE_VERSION}", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(sw // 2, 150))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Modern button boxes
        btn_width, btn_height = 200, 50
        btn_x = sw // 2 - btn_width // 2
        
        # Start button
        start_y = sh // 2 - 30
        start_rect = pygame.Rect(btn_x, start_y, btn_width, btn_height)
        pygame.draw.rect(screen, (70, 150, 200), start_rect)
        pygame.draw.rect(screen, (150, 220, 255), start_rect, 3)
        start_font = pygame.font.Font(None, 32)
        start_text = start_font.render("START GAME", True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=start_rect.center)
        screen.blit(start_text, start_text_rect)
        screen.blit(start_font.render("Press ENTER", True, (100, 200, 255)), (btn_x + 10, start_y + 58))
        
        # Quit button
        quit_y = sh // 2 + 50
        quit_rect = pygame.Rect(btn_x, quit_y, btn_width, btn_height)
        pygame.draw.rect(screen, (150, 70, 70), quit_rect)
        pygame.draw.rect(screen, (255, 150, 150), quit_rect, 3)
        quit_text = start_font.render("QUIT", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        screen.blit(quit_text, quit_text_rect)
        screen.blit(start_font.render("Press Q", True, (255, 100, 100)), (btn_x + 10, quit_y + 58))
        
        # Controls hint
        hint_font = pygame.font.Font(None, 18)
        hint_text = hint_font.render("In-Game: I/Tab/O: Inventory  |  E: Equipment  |  ESC: Pause", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(sw // 2, sh - 60))
        screen.blit(hint_text, hint_rect)
        
        # Bottom info bar
        info_font = pygame.font.Font(None, 16)
        version_text = info_font.render(f"v{ENGINE_VERSION}", True, (180, 180, 120))
        copyright_text = info_font.render("© 2025 CosmicPhoenix171 - All Rights Reserved", True, (100, 100, 100))
        screen.blit(version_text, (15, sh - 25))
        screen.blit(copyright_text, (sw - copyright_text.get_width() - 15, sh - 25))

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
        # Quit button
        quit_rect = pygame.Rect(config.SCREEN_WIDTH // 2 - 80, config.SCREEN_HEIGHT // 2 + 80, 160, 48)
        pygame.draw.rect(screen, (60, 60, 80), quit_rect)
        pygame.draw.rect(screen, config.WHITE, quit_rect, 2)
        quit_txt = btn_font.render("Quit", True, config.WHITE)
        quit_txt_rect = quit_txt.get_rect(center=quit_rect.center)
        screen.blit(quit_txt, quit_txt_rect)
        # Store for click detection
        self._game_over_restart_rect = restart_rect
        self._game_over_quit_rect = quit_rect

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
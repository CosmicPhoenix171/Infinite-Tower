import pygame
import logging
from typing import Optional

from .utils.input_handler import InputHandler
from .resources.loader import ResourceLoader
from . import config
from .entities.player import Player
from .entities.enemy import Enemy, EnemyType
from .entities.wall import Wall
from .ui.game_ui import GameUI
from .ui.inventory import InventoryUI
from .systems.combat import CombatSystem
from .systems.physics import Physics
from .items.loot import LootGenerator
from . import __version__ as ENGINE_VERSION
from .floors.generator import FloorGenerator, RoomType, TileType

# Optional GPU renderer via pygame._sdl2
try:
    from pygame._sdl2.video import Window as SDLWindow, Renderer as SDLRenderer, Texture as SDLTexture
    _SDL2_AVAILABLE = True
except Exception:
    _SDL2_AVAILABLE = False


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
            # Decide on GPU vs CPU rendering
            self.use_gpu = bool(getattr(config, 'USE_GPU_RENDERER', False) and _SDL2_AVAILABLE)
            if self.use_gpu:
                # Initialize display mode first (required for Surface creation)
                pygame.display.set_mode((1, 1))  # Minimal display to enable Surface creation
                # Create SDL2 Window/Renderer; no classic display surface
                self.window = SDLWindow(config.TITLE, size=(config.SCREEN_WIDTH, config.SCREEN_HEIGHT), resizable=True)
                self.window.show()
                self.renderer = SDLRenderer(self.window, vsync=getattr(config, 'GPU_VSYNC', True))
                self.screen = None
                # UI overlay surface (drawn unrotated)
                self._ui_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA).convert_alpha()
            else:
                flags = pygame.SCALED | pygame.RESIZABLE
                self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags)
                pygame.display.set_caption(config.TITLE)
                # UI overlay surface for consistency
                self._ui_surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA).convert_alpha()
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

        # Initialize pygame systems early (needed before loading fonts/resources)
        self._init_pygame()

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
        self.walls: list[Wall] = []

        # Camera system (tracks player position)
        self.camera_x = 0
        self.camera_y = 0
        self.camera_angle = 0  # Rotation angle in degrees (raw/target)
        self.camera_angle_smooth = 0.0  # Smoothed angle for rendering

        # World bounds in pixels (min_x, min_y, max_x, max_y)
        self.world_bounds: Optional[tuple[int, int, int, int]] = None

        # World rendering caches (for rotating camera performance)
        self._world_bg = None           # Static background (floor + grid)
        self._world_surface = None      # Working surface for entities
        self._world_size = 0            # Cached size of world surfaces
        self._last_rotated = None       # Cache last rotated surface
        self._last_rotation_angle = None  # Cache angle of last rotation

        # Debug flags and UI
        self.debug_flags = {
            'show_fps': False,
            'show_collision': False,
            'show_vision': False,
            'show_ai': False,
        }
        self._debug_ui_rects = {}

        # Pause/settings UI state defaults (needed when starting from main menu)
        self.pause_substate = None  # None, 'debug'
        self.settings_tab = 'sound'
        self.settings_temp = {}

    # Pygame already initialized above

    def start(self):
        """Start the game and enter the main loop."""
        # Pause/settings UI state
        self.pause_substate = None  # None, 'settings'
        self.settings_tab = 'sound'  # 'sound', 'graphics', 'keybinds'
        self.settings_temp = {}
        self.current_state = "playing"
        self.is_running = True
        self.logger.info("Game started")

    def _update_camera(self):
        """Update camera position and smoothed rotation to follow the player."""
        if not self.player:
            return

        # Get screen size - from window in GPU mode, from surface in CPU mode
        if getattr(self, 'use_gpu', False):
            sw, sh = self.window.size
        else:
            sw, sh = self.screen.get_size()
        
        # Center camera on player position
        self.camera_x = self.player.position[0] - sw // 2
        self.camera_y = self.player.position[1] - sh // 2
        
        # Debug camera calc
        if not hasattr(self, '_camera_debug'):
            print(f"[CAMERA DEBUG] sw={sw}, sh={sh}, player_pos={self.player.position}, camera=({self.camera_x}, {self.camera_y})")
            self._camera_debug = True

        # Target player's current angle
        target = getattr(self.player, 'direction_angle', 0) % 360

        # Smoothly interpolate angle across wrap-around (shortest arc)
        # Normalize difference to [-180, 180]
        diff = (target - self.camera_angle_smooth + 540) % 360 - 180
        smoothing = 100  # 0..1, lower = smoother/slower, higher = snappier (0.18 for faster turning with smoothness)
        self.camera_angle_smooth = (self.camera_angle_smooth + diff * smoothing) % 360
        self.camera_angle = target

    def pause(self):
        """Pause the game."""
        if self.current_state == "playing":
            self.current_state = "paused"
            self.is_running = False
            self.logger.info("Game paused")

    def resume(self):
        """Resume the game from pause."""
        if self.current_state == "paused":
            self.current_state = "playing"
            self.is_running = True
            self.logger.info("Game resumed")

    def end(self):
        """End the game and cleanup resources."""
        self.is_running = False
        self.current_state = "quit"
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
                elif event.key == pygame.K_RETURN:
                    # Dismiss dialog if showing
                    if self.game_ui and getattr(self.game_ui, 'current_dialog', None):
                        self.game_ui.hide_dialog()
            # Remove keyup-based toggling to ensure Tab is a true toggle (no press-and-hold behavior)
            elif event.type == pygame.KEYUP:
                pass
            # Main menu mouse handling
            if self.current_state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, '_menu_start_rect') and self._menu_start_rect.collidepoint(event.pos):
                        self._start_play()
                        self.logger.info("Transitioning to gameplay")
                        return
                    if hasattr(self, '_menu_quit_rect') and self._menu_quit_rect.collidepoint(event.pos):
                        self.end()
                        self.logger.info("Quit from main menu")
                        return
            
            # Pause menu mouse handling
            if self.current_state == "paused":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # If in debug substate, handle debug toggles
                    if self.pause_substate == 'debug':
                        # Back button
                        if hasattr(self, '_debug_back_rect') and self._debug_back_rect.collidepoint(event.pos):
                            self.pause_substate = None
                            return
                        # Toggle flags
                        for key, rect in self._debug_ui_rects.items():
                            if rect.collidepoint(event.pos):
                                self.debug_flags[key] = not self.debug_flags.get(key, False)
                                return
                    # Base pause menu buttons
                    buttons = self._compute_pause_buttons()
                    if buttons['resume'].collidepoint(event.pos):
                        self.resume()
                        return
                    if buttons['debug'].collidepoint(event.pos):
                        self.pause_substate = 'debug'
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
            if event.type == pygame.VIDEORESIZE:
                if getattr(self, 'use_gpu', False) and getattr(self, 'window', None):
                    # Resize SDL window and UI surface
                    self.window.size = (event.w, event.h)
                    self._ui_surface = pygame.Surface((event.w, event.h), pygame.SRCALPHA).convert_alpha()
                    # Update UI surfaces
                    if self.game_ui:
                        self.game_ui.screen = self._ui_surface
                    if self.inventory_ui:
                        self.inventory_ui.screen = self._ui_surface
                else:
                    flags = pygame.SCALED | pygame.RESIZABLE
                    self.screen = pygame.display.set_mode((event.w, event.h), flags)
                    # Update UI surfaces
                    if self.game_ui:
                        self.game_ui.screen = self.screen
                    if self.inventory_ui:
                        self.inventory_ui.screen = self.screen
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
        # Floor generator
        # Use a time-based seed for variability across runs
        seed_str = f"floor-{pygame.time.get_ticks()}"
        self.floor_gen = FloorGenerator(seed_str)
        
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

        # Enemies will be spawned by the floor generator per-room
        self.enemies = []

        # Generate floor layout and walls from tiles (no blocked-off rooms)
        rooms = self.floor_gen.generate_floor(num_rooms=6, floor_level=1)
        tile_size = self.floor_gen.tile_size

        # Ensure every room has at least one door (avoid enclosed rooms)
        for room in rooms:
            if len(getattr(room, 'doors', [])) == 0:
                # Add a default door on top
                try:
                    room.add_door("top")
                except Exception:
                    pass

    # Pick starting room (SAFE if available), place player at its center
        start_room = next((r for r in rooms if r.room_type == RoomType.SAFE), rooms[0] if rooms else None)
        if start_room:
            # Convert room center (in room grid space) to world pixels
            # World tile coordinates: (room.x*20 + local_col)
            center_col = start_room.width // 2
            center_row = start_room.height // 2
            world_tx = (start_room.x * 20 + center_col)
            world_ty = (start_room.y * 20 + center_row)
            self.player.position = [world_tx * tile_size, world_ty * tile_size]
            self.player.rect.center = (int(self.player.position[0]), int(self.player.position[1]))

        # Spawn enemies from rooms (based on generator population)
        for room in rooms:
            self.enemies.extend(self.floor_gen.spawn_enemies(room))

        # Build Wall entities from room tiles by merging horizontal wall runs; skip DOOR tiles
        self.walls = []
        for room in rooms:
            base_tx = room.x * 20
            base_ty = room.y * 20
            for row_idx, row in enumerate(room.tiles):
                col = 0
                while col < room.width:
                    # Start of a wall run?
                    if row[col] == TileType.WALL:
                        run_start = col
                        # Extend until non-wall or end
                        while col < room.width and row[col] == TileType.WALL:
                            col += 1
                        run_len = col - run_start
                        # Compute world pixel rect for this horizontal wall run
                        tile_x = (base_tx + run_start) * tile_size
                        tile_y = (base_ty + row_idx) * tile_size
                        wall_w = run_len * tile_size
                        wall_h = tile_size
                        # If any tile within the run is a DOOR, split around it
                        has_door = any((row[c] == TileType.DOOR) for c in range(run_start, run_start + run_len))
                        if not has_door:
                            self.walls.append(Wall(tile_x, tile_y, wall_w, wall_h))
                        else:
                            # Emit segments skipping door tiles
                            seg_start = run_start
                            c = run_start
                            while c < run_start + run_len:
                                if row[c] == TileType.DOOR:
                                    if c > seg_start:
                                        seg_len = c - seg_start
                                        seg_x = (base_tx + seg_start) * tile_size
                                        seg_y = tile_y
                                        self.walls.append(Wall(seg_x, seg_y, seg_len * tile_size, tile_size))
                                    seg_start = c + 1
                                c += 1
                            if seg_start < run_start + run_len:
                                seg_len = (run_start + run_len) - seg_start
                                seg_x = (base_tx + seg_start) * tile_size
                                seg_y = tile_y
                                self.walls.append(Wall(seg_x, seg_y, seg_len * tile_size, tile_size))
                    else:
                        col += 1

        # Compute world bounds from generated rooms
        if rooms:
            min_tx = min(r.x * 20 for r in rooms)
            min_ty = min(r.y * 20 for r in rooms)
            max_tx = max(r.x * 20 + r.width for r in rooms)
            max_ty = max(r.y * 20 + r.height for r in rooms)
            pad_tiles = 2
            self.world_bounds = (
                (min_tx - pad_tiles) * tile_size,
                (min_ty - pad_tiles) * tile_size,
                (max_tx + pad_tiles) * tile_size,
                (max_ty + pad_tiles) * tile_size,
            )

            # Add outer border walls around the world bounds
            bx0, by0, bx1, by1 = self.world_bounds
            thickness = tile_size
            # Top
            self.walls.append(Wall(bx0, by0, bx1 - bx0, thickness))
            # Bottom
            self.walls.append(Wall(bx0, by1 - thickness, bx1 - bx0, thickness))
            # Left
            self.walls.append(Wall(bx0, by0, thickness, by1 - by0))
            # Right
            self.walls.append(Wall(bx1 - thickness, by0, thickness, by1 - by0))
        
        # UI
        ui_target = self._ui_surface if getattr(self, 'use_gpu', False) else self.screen
        self.game_ui = GameUI(ui_target, self.player)
        self.game_ui.set_floor(1, "Entrance Hall")
        self.inventory_ui = InventoryUI(ui_target, self.player)
        self.game_ui.add_notification("Game Started!", self.game_ui.COLORS['text_green'])
        self.game_ui.add_notification("Welcome to Floor 1", self.game_ui.COLORS['text_yellow'])
        
        # Initialize camera to center on player (important for first render frame)
        self._update_camera()
        
        self.current_state = "playing"

    def _update_gameplay(self):
        """Update gameplay state."""
        if not (self.player and self.physics and self.combat_system and self.game_ui):
            return
        dt = self.dt
        
        # Update camera to follow player
        self._update_camera()
        
        # Player input and update (freeze movement when inventory open)
        if not (self.inventory_ui and self.inventory_ui.is_visible):
            self.player.handle_input(self.input_handler)
        # Allow player to move within world bounds (not clamped to screen)
        self.player.update(dt, bounds=self.world_bounds)

        # Collide player with walls (AABB resolution based on minimal overlap)
        if self.walls:
            for wall in self.walls:
                if self.player.rect.colliderect(wall.rect):
                    side = self.physics.get_collision_side(self.player.rect, wall.rect, tuple(self.player.velocity))
                    if side == "left":
                        self.player.rect.right = wall.rect.left
                    elif side == "right":
                        self.player.rect.left = wall.rect.right
                    elif side == "top":
                        self.player.rect.bottom = wall.rect.top
                    elif side == "bottom":
                        self.player.rect.top = wall.rect.bottom
                    # Sync position back to center of rect
                    self.player.position[0] = self.player.rect.centerx
                    self.player.position[1] = self.player.rect.centery
        
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
                enemy.update(self.player, dt, obstacles=self.walls, bounds=self.world_bounds)
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

    def render(self, screen: Optional[pygame.Surface]):
        """
        Render the current game state to the provided screen.
        
        Args:
            screen: The pygame surface to render to
        """
        if not screen and not getattr(self, 'use_gpu', False):
            return
            
        # Clear target
        if getattr(self, 'use_gpu', False):
            # In GPU mode, clear UI surface for menu/pause/game_over; gameplay clears inside
            self._ui_surface.fill(config.BACKGROUND_COLOR)
        else:
            screen.fill(config.BACKGROUND_COLOR)
        
        # Render based on current game state
        if self.current_state == "menu":
            target = self._ui_surface if getattr(self, 'use_gpu', False) else screen
            self._render_menu(target)
            if getattr(self, 'use_gpu', False):
                # Present UI texture
                ui_tex = SDLTexture.from_surface(self.renderer, self._ui_surface)
                sw, sh = target.get_size()
                ui_tex.draw(None, (0, 0, sw, sh), 0)
                self.renderer.present()
        elif self.current_state == "playing":
            self._render_gameplay(screen)
        elif self.current_state == "paused":
            target = self._ui_surface if getattr(self, 'use_gpu', False) else screen
            self._render_pause(target)
            if getattr(self, 'use_gpu', False):
                ui_tex = SDLTexture.from_surface(self.renderer, self._ui_surface)
                sw, sh = target.get_size()
                ui_tex.draw(None, (0, 0, sw, sh), 0)
                self.renderer.present()
        elif self.current_state == "game_over":
            target = self._ui_surface if getattr(self, 'use_gpu', False) else screen
            self._render_game_over(target)
            if getattr(self, 'use_gpu', False):
                ui_tex = SDLTexture.from_surface(self.renderer, self._ui_surface)
                sw, sh = target.get_size()
                ui_tex.draw(None, (0, 0, sw, sh), 0)
                self.renderer.present()

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
        
        # Hover effect for Start button
        mouse_pos = pygame.mouse.get_pos()
        start_hover = start_rect.collidepoint(mouse_pos)
        start_color = (90, 170, 220) if start_hover else (70, 150, 200)
        
        pygame.draw.rect(screen, start_color, start_rect)
        pygame.draw.rect(screen, (150, 220, 255), start_rect, 3)
        start_font = pygame.font.Font(None, 32)
        start_text = start_font.render("START GAME", True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=start_rect.center)
        screen.blit(start_text, start_text_rect)
        
        # Store for click detection
        self._menu_start_rect = start_rect
        
        # Quit button
        quit_y = sh // 2 + 50
        quit_rect = pygame.Rect(btn_x, quit_y, btn_width, btn_height)
        
        # Hover effect for Quit button
        quit_hover = quit_rect.collidepoint(mouse_pos)
        quit_color = (170, 90, 90) if quit_hover else (150, 70, 70)
        
        pygame.draw.rect(screen, quit_color, quit_rect)
        pygame.draw.rect(screen, (255, 150, 150), quit_rect, 3)
        quit_text = start_font.render("QUIT", True, (255, 255, 255))
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        screen.blit(quit_text, quit_text_rect)
        
        # Store for click detection
        self._menu_quit_rect = quit_rect
        
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
        """Render gameplay with grid, walls, and entities all rotating together with player perspective."""
        import math

        # Get screen size - from window in GPU mode, from surface in CPU mode
        if getattr(self, 'use_gpu', False):
            sw, sh = self.window.size
        else:
            sw, sh = screen.get_size()
            # Fill screen background
            screen.fill((35, 30, 25))

        # 1) Prepare a world surface for everything (grid, walls, entities - all rotate together)
        # In GPU mode, cap to a conservative texture size to avoid driver limits (e.g., 1024)
        diag = int(math.hypot(sw, sh)) + 64  # minimal square covering screen when rotated
        if getattr(self, 'use_gpu', False):
            max_tex = 1024
            world_size = min(diag, max_tex)
        else:
            world_size = diag
        if self._world_surface is None or self._world_size != world_size:
            self._world_size = world_size
            self._world_surface = pygame.Surface((world_size, world_size))

        world_surface = self._world_surface
        world_surface.fill((35, 30, 25))  # Fill with background color

        # 2) Draw grid on world surface (world-space, will rotate with everything)
        grid_size = 32
        grid_color = (50, 45, 40)
        world_center_x = world_size // 2
        world_center_y = world_size // 2
        
        # Grid centered around player position in world
        # Calculate grid offset so lines align with world coordinates
        grid_offset_x = int((-self.camera_x) % grid_size)
        grid_offset_y = int((-self.camera_y) % grid_size)
        
        # Draw grid lines across the entire world surface
        for x in range(grid_offset_x - world_size // 2, world_size, grid_size):
            pygame.draw.line(world_surface, grid_color, (x + world_size // 2, 0), (x + world_size // 2, world_size), 1)
        for y in range(grid_offset_y - world_size // 2, world_size, grid_size):
            pygame.draw.line(world_surface, grid_color, (0, y + world_size // 2), (world_size, y + world_size // 2), 1)

        # 3) Draw walls on world surface (world-space, will rotate with grid)
        if getattr(self, 'walls', None):
            for wall in self.walls:
                # Position relative to camera (centered on player)
                rel_x = wall.rect.x - int(self.camera_x) + world_center_x - sw // 2
                rel_y = wall.rect.y - int(self.camera_y) + world_center_y - sh // 2
                temp = pygame.Rect(rel_x, rel_y, wall.rect.width, wall.rect.height)
                wall.draw(world_surface, rect_override=temp)
        
        # 4) Draw enemies on world surface with camera offset
        if self.enemies:
            for enemy in self.enemies:
                # Position relative to camera (centered on player)
                rel_x = enemy.rect.x - int(self.camera_x) + world_center_x - sw // 2
                rel_y = enemy.rect.y - int(self.camera_y) + world_center_y - sh // 2
                
                # Temporarily adjust enemy position for drawing
                original_x = enemy.rect.x
                original_y = enemy.rect.y
                enemy.rect.x = rel_x
                enemy.rect.y = rel_y
                enemy.draw(world_surface)
                enemy.rect.x = original_x
                enemy.rect.y = original_y
        
        # 4b) Draw player's attack rect on world surface so it rotates with the world
        if self.player and getattr(self.player, 'is_attacking', False):
            attack_rect = self.player.get_attack_rect()
            arx = attack_rect.x - int(self.camera_x) + world_center_x - sw // 2
            ary = attack_rect.y - int(self.camera_y) + world_center_y - sh // 2
            pygame.draw.rect(world_surface, (255, 80, 80), pygame.Rect(arx, ary, attack_rect.width, attack_rect.height), 2)

        # 4c) Debug overlays drawn on world surface (rotate with world)
        if getattr(self, 'debug_flags', None):
            # Collision boxes
            if self.debug_flags.get('show_collision', False):
                # Walls
                for wall in getattr(self, 'walls', []) or []:
                    rel_x = wall.rect.x - int(self.camera_x) + world_center_x - sw // 2
                    rel_y = wall.rect.y - int(self.camera_y) + world_center_y - sh // 2
                    pygame.draw.rect(world_surface, (0, 200, 255), pygame.Rect(rel_x, rel_y, wall.rect.width, wall.rect.height), 1)
                # Player
                if self.player:
                    prx = self.player.rect.x - int(self.camera_x) + world_center_x - sw // 2
                    pry = self.player.rect.y - int(self.camera_y) + world_center_y - sh // 2
                    pygame.draw.rect(world_surface, (0, 255, 150), pygame.Rect(prx, pry, self.player.rect.width, self.player.rect.height), 1)
                # Enemies
                for enemy in self.enemies:
                    erx = enemy.rect.x - int(self.camera_x) + world_center_x - sw // 2
                    ery = enemy.rect.y - int(self.camera_y) + world_center_y - sh // 2
                    pygame.draw.rect(world_surface, (255, 220, 0), pygame.Rect(erx, ery, enemy.rect.width, enemy.rect.height), 1)

            # Vision cones
            if self.debug_flags.get('show_vision', False):
                try:
                    import math
                    for enemy in self.enemies:
                        cx = enemy.rect.centerx - int(self.camera_x) + world_center_x - sw // 2
                        cy = enemy.rect.centery - int(self.camera_y) + world_center_y - sh // 2
                        facing = getattr(enemy, 'direction_angle', 0.0)
                        # Get AI FOV/range via enemy.ai
                        fov = getattr(enemy.ai, 'fov_degrees', 90)
                        rng = getattr(enemy.ai, 'vision_range', 300)
                        # Build cone polygon
                        steps = 12
                        half = fov / 2.0
                        points = [(cx, cy)]
                        for i in range(steps + 1):
                            a = (facing - half) + (fov * i / steps)
                            rad = math.radians(a)
                            px = cx + math.cos(rad) * rng
                            py = cy + math.sin(rad) * rng
                            points.append((px, py))
                        pygame.draw.polygon(world_surface, (255, 255, 0), points, 1)
                except Exception:
                    pass

            # AI state labels
            if self.debug_flags.get('show_ai', False):
                try:
                    label_font = pygame.font.Font(None, 18)
                    for enemy in self.enemies:
                        ex = enemy.rect.centerx - int(self.camera_x) + world_center_x - sw // 2
                        ey = enemy.rect.top - int(self.camera_y) + world_center_y - sh // 2 - 12
                        state = None
                        if hasattr(enemy, 'ai') and hasattr(enemy.ai, 'state'):
                            s = enemy.ai.state
                            state = s.name if hasattr(s, 'name') else str(s)
                        if state is None and hasattr(enemy, 'state'):
                            state = str(enemy.state)
                        if state:
                            txt = label_font.render(state, True, (255, 255, 0))
                            world_surface.blit(txt, (ex - txt.get_width() // 2, ey))
                except Exception:
                    pass
        
        # 5) Draw player on world surface (centered)
        if self.player:
            # Player is always at the center of the world surface in player-relative coordinates
            player_x = world_center_x - self.player.size // 2
            player_y = world_center_y - self.player.size // 2
            
            # Temporarily adjust player position for drawing
            original_x = self.player.rect.x
            original_y = self.player.rect.y
            self.player.rect.x = player_x
            self.player.rect.y = player_y
            self.player.draw(world_surface)
            self.player.rect.x = original_x
            self.player.rect.y = original_y
        
        # 6) Present using GPU renderer if enabled, else CPU rotate+blit
        if getattr(self, 'use_gpu', False):
            # Clear renderer background
            self.renderer.draw_color = (35, 30, 25, 255)
            self.renderer.clear()

            # Draw a tiny sanity quad (red square) to ensure renderer output is visible (one-time)
            if not hasattr(self, '_gpu_sanity_drawn'):
                try:
                    test_surf = pygame.Surface((128, 128))
                    test_surf.fill((220, 40, 40))
                    test_tex = SDLTexture.from_surface(self.renderer, test_surf)
                    test_tex.draw(None, (20, 20, 128, 128), 0)
                    print("[GPU DEBUG] sanity quad drawn")
                except Exception as _:
                    print("[GPU DEBUG] sanity quad FAILED")
                self._gpu_sanity_drawn = True

            # Upload world and draw rotated with 1.5x zoom (draw world BEFORE UI)
            angle_gpu = self.camera_angle_smooth - 270
            
            # Debug: print world surface info
            if not hasattr(self, '_debug_printed'):
                print(f"[GPU DEBUG] World surface size: {world_surface.get_size()}")
                print(f"[GPU DEBUG] Screen size: {sw}x{sh}")
                print(f"[GPU DEBUG] Player position: {self.player.position if self.player else 'None'}")
                print(f"[GPU DEBUG] Camera: ({self.camera_x}, {self.camera_y})")
                print(f"[GPU DEBUG] Enemies count: {len(self.enemies)}")
                print(f"[GPU DEBUG] Walls count: {len(self.walls) if self.walls else 0}")
                # Save world surface to file for inspection
                try:
                    pygame.image.save(world_surface, "debug_world_surface.png")
                    print("[GPU DEBUG] Saved world surface to debug_world_surface.png")
                except:
                    pass
                self._debug_printed = True
            
            world_tex = SDLTexture.from_surface(self.renderer, world_surface)
            world_tex.blend_mode = 1  # Enable alpha blending for world texture
            # Scale up by 1.5x and center
            zoomed_w, zoomed_h = int(sw * 1.5), int(sh * 1.5)
            offset_x, offset_y = (sw - zoomed_w) // 2, (sh - zoomed_h) // 2
            # draw(srcrect, dstrect, angle, origin, flip_x, flip_y)
            world_tex.draw(None, (offset_x, offset_y, zoomed_w, zoomed_h), angle_gpu)

            # Draw UI (onto UI surface first)
            if self.game_ui:
                self.game_ui.draw()
            if self.inventory_ui:
                self.inventory_ui.draw()
            # Upload UI (unrotated) with alpha blending and present
            ui_tex = SDLTexture.from_surface(self.renderer, self._ui_surface)
            ui_tex.blend_mode = 1  # SDL_BLENDMODE_BLEND for alpha transparency
            ui_tex.draw(None, (0, 0, sw, sh), 0)
            self.renderer.present()
            # Clear UI for next frame
            self._ui_surface.fill((0, 0, 0, 0))
            return
        else:
            # CPU path: rotate entire world surface and blit to screen
            # 1.5 = 50% zoom in (closer camera)
            angle = self.camera_angle_smooth - 270
            
            # Always rotate (no caching) to ensure enemies/player movement is visible
            rotated_surface = pygame.transform.rotozoom(world_surface, angle, 1.5)
            
            rotated_rect = rotated_surface.get_rect(center=(sw // 2, sh // 2))
            screen.blit(rotated_surface, rotated_rect)

            # UI (not rotated, stays on screen)
            if self.game_ui:
                self.game_ui.draw()
            if self.inventory_ui:
                self.inventory_ui.draw()

        # Debug: on-screen overlays (not rotated)
        if getattr(self, 'debug_flags', None) and self.debug_flags.get('show_fps', False):
            try:
                fps = self.clock.get_fps()
                info = f"FPS: {fps:.1f}  Angle: {self.camera_angle_smooth:.1f}"
                font = pygame.font.Font(None, 22)
                txt = font.render(info, True, (230, 230, 230))
                screen.blit(txt, (10, 6))
            except Exception:
                pass

    def _render_pause(self, screen: pygame.Surface):
        """Render the pause screen, with optional Debug submenu."""
        sw, sh = screen.get_size()
        # Dark overlay
        overlay = pygame.Surface((sw, sh))
        overlay.fill(config.BLACK)
        overlay.set_alpha(140)
        screen.blit(overlay, (0, 0))

        # Base panel
        panel_w, panel_h = 520, 300
        panel_x = (sw - panel_w) // 2
        panel_y = (sh - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, (34, 34, 48), panel_rect)
        pygame.draw.rect(screen, config.WHITE, panel_rect, 2)

        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Paused", True, config.WHITE)
        title_rect = title.get_rect(center=(panel_x + panel_w // 2, panel_y + 40))
        screen.blit(title, title_rect)

        if self.pause_substate == 'debug':
            self._render_debug_menu(screen, panel_rect)
            return

        # Buttons
        buttons = self._compute_pause_buttons()
        btn_font = pygame.font.Font(None, 32)
        labels = {
            'resume': 'Resume',
            'debug': 'Debug',
            'quit': 'Quit',
        }
        for name, rect in buttons.items():
            pygame.draw.rect(screen, (60, 60, 80), rect)
            pygame.draw.rect(screen, config.WHITE, rect, 2)
            txt = btn_font.render(labels.get(name, name.title()), True, config.WHITE)
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)

    def _render_debug_menu(self, screen: pygame.Surface, panel_rect: pygame.Rect):
        """Render a simple debug toggles panel inside pause."""
        self._debug_ui_rects = {}
        sw, sh = screen.get_size()
        px, py, pw, ph = panel_rect
        font = pygame.font.Font(None, 28)
        title = font.render("Debug Options", True, config.WHITE)
        screen.blit(title, (px + 20, py + 80))

        options = [
            ('show_fps', 'Show FPS'),
            ('show_collision', 'Show Collision Boxes'),
            ('show_vision', 'Show Enemy Vision Cones'),
            ('show_ai', 'Show Enemy AI State'),
        ]
        y = py + 120
        for key, label in options:
            box = pygame.Rect(px + 24, y, 22, 22)
            pygame.draw.rect(screen, config.WHITE, box, 2)
            if self.debug_flags.get(key, False):
                pygame.draw.line(screen, config.WHITE, (box.left + 4, box.centery), (box.centerx, box.bottom - 4), 2)
                pygame.draw.line(screen, config.WHITE, (box.centerx, box.bottom - 4), (box.right - 4, box.top + 4), 2)
            text = font.render(label, True, config.WHITE)
            screen.blit(text, (box.right + 10, y - 2))
            self._debug_ui_rects[key] = box
            y += 36

        # Back button
        back_rect = pygame.Rect(px + pw - 140, py + ph - 60, 120, 36)
        pygame.draw.rect(screen, (60, 60, 80), back_rect)
        pygame.draw.rect(screen, config.WHITE, back_rect, 2)
        back_txt = pygame.font.Font(None, 28).render("Back", True, config.WHITE)
        back_txt_rect = back_txt.get_rect(center=back_rect.center)
        screen.blit(back_txt, back_txt_rect)
        self._debug_back_rect = back_rect

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
        """Compute pause menu buttons (Resume, Debug, Quit) based on screen size."""
        # Get screen size - from window in GPU mode, from surface in CPU mode
        if getattr(self, 'use_gpu', False) and hasattr(self, 'window'):
            sw, sh = self.window.size
        elif self.screen:
            sw, sh = self.screen.get_size()
        else:
            sw, sh = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        panel_w, panel_h = 520, 300
        panel_x = (sw - panel_w) // 2
        panel_y = (sh - panel_h) // 2
        btn_w, btn_h = 150, 44
        gap = 20
        total_w = btn_w * 3 + gap * 2
        start_x = panel_x + (panel_w - total_w) // 2
        y = panel_y + panel_h - 80
        resume_rect = pygame.Rect(start_x, y, btn_w, btn_h)
        debug_rect = pygame.Rect(start_x + btn_w + gap, y, btn_w, btn_h)
        quit_rect = pygame.Rect(start_x + (btn_w + gap) * 2, y, btn_w, btn_h)
        return {'resume': resume_rect, 'debug': debug_rect, 'quit': quit_rect}

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

    def _draw_player_overlay(self, screen: pygame.Surface):
        """Draw the player on a separate surface, rotate it, and blit centered on screen."""
        if not self.player:
            return
        sw, sh = screen.get_size()

        # Create a temporary surface to render the player body
        pad = 8
        ps = max(self.player.size + pad * 2, 64)
        player_surf = pygame.Surface((ps, ps), pygame.SRCALPHA)

        # Temporarily center the player's rect on this surface, draw, then restore
        old_center = self.player.rect.center
        self.player.rect.center = (ps // 2, ps // 2)
        self.player.draw(player_surf)
        self.player.rect.center = old_center

        # Do NOT rotate the player overlay. Player should always face up relative to screen.
        rrect = player_surf.get_rect(center=(sw // 2, sh // 2))
        screen.blit(player_surf, rrect)
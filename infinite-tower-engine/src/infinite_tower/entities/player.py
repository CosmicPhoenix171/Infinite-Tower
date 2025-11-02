"""
Infinite Tower Engine - Player Entity Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
import os
from typing import Tuple, List, Optional
from ..config import (
    PLAYER_HEALTH, PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT,
    GREEN, WHITE, RED, SPRITES_PATH
)


class Player:
    """
    Player entity with movement, combat, and inventory systems.
    
    Attributes:
        name: Player's name
        health: Current health points
        max_health: Maximum health points
        position: Current (x, y) position
        velocity: Current (vx, vy) velocity
        speed: Movement speed
        size: Player hitbox size
        inventory: List of collected items
        attack_power: Base attack damage
        defense: Damage reduction
        rect: Pygame rect for collision detection
    """
    
    def __init__(self, name: str, health: int = None, position: Tuple[float, float] = None):
        self.name = name
        self.max_health = health if health else PLAYER_HEALTH
        self.health = self.max_health
        self.position = list(position) if position else [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
        self.velocity = [0.0, 0.0]
        self.speed = PLAYER_SPEED
        self.sprint_multiplier = 3.5  # Sprint is 3.5x normal speed
        self.is_sprinting = False
        self.size = 48  # Player sprite size (increased from 32 for better visibility with zoom)
        self.inventory = []
        
        # Sprite animation
        self.sprite_sheet = None
        self.sprite_frames = []  # [idle1, idle2, walk1, walk2]
        self.frame_width = 268  # Width of each frame (536/2 columns)
        self.frame_height = 317  # Height of each frame (635/2 rows)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 8  # Frames between sprite changes
        self._load_sprites()
        
        # Stamina system
        self.stamina = 100
        self.max_stamina = 100
        
        # Combat stats
        self.attack_power = 10
        self.defense = 0
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_cooldown_time = 30  # frames
        
        # Animation and state
        self.direction = "down"  # up, down, left, right (cardinal)
        self.direction_angle = 0  # 360-degree angle (0-360)
        self.is_moving = False
        
        # Collision rectangle
        self.rect = pygame.Rect(
            self.position[0] - self.size // 2,
            self.position[1] - self.size // 2,
            self.size,
            self.size
        )
    
    def _load_sprites(self):
        """Load and split the player sprite sheet into individual frames."""
        try:
            # Get the absolute path to the sprites directory
            # Go up from entities -> infinite_tower -> src -> infinite-tower-engine -> assets/sprites
            current_dir = os.path.dirname(os.path.abspath(__file__))
            engine_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            sprite_path = os.path.join(engine_root, "assets", "sprites", "player_spritesheet.png")
            
            print(f"[DEBUG] Looking for sprite at: {sprite_path}")
            print(f"[DEBUG] File exists: {os.path.exists(sprite_path)}")
            
            if os.path.exists(sprite_path):
                self.sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                print(f"[DEBUG] Sprite sheet loaded, size: {self.sprite_sheet.get_size()}")
                
                # Extract 4 frames from 2x2 grid
                # Top row (y=0): idle1 (x=0), idle2 (x=268)
                # Bottom row (y=317): walk1 (x=0), walk2 (x=268)
                positions = [
                    (0, 0),          # Frame 0: idle1 (top-left)
                    (268, 0),        # Frame 1: idle2 (top-right)
                    (0, 317),        # Frame 2: walk1 (bottom-left)
                    (268, 317),      # Frame 3: walk2 (bottom-right)
                ]
                
                for x, y in positions:
                    frame = self.sprite_sheet.subsurface(
                        pygame.Rect(x, y, self.frame_width, self.frame_height)
                    )
                    # Scale to match player size
                    scaled_frame = pygame.transform.scale(frame, (self.size, self.size))
                    self.sprite_frames.append(scaled_frame)
                print(f"[DEBUG] Loaded {len(self.sprite_frames)} sprite frames")
            else:
                print(f"[DEBUG] Sprite file not found at {sprite_path}")
        except (pygame.error, FileNotFoundError) as e:
            # Sprite sheet not found or invalid, will use fallback rendering
            print(f"[DEBUG] Error loading sprite: {e}")
            self.sprite_frames = []

    def handle_input(self, input_handler):
        """
        Handle player input for 360-degree movement using WASD or Arrow keys.
        
        Args:
            input_handler: InputHandler instance for checking key states
        """
        import math
        
        self.velocity = [0.0, 0.0]
        self.is_moving = False
        
        # Check if sprinting (Shift key) - only if stamina available
        player_stamina = getattr(self, 'stamina', 100)
        self.is_sprinting = ((input_handler.get_key(pygame.K_LSHIFT) or 
                             input_handler.get_key(pygame.K_RSHIFT)) and 
                            player_stamina > 0)
        
        # Apply sprint multiplier
        current_speed = self.speed * self.sprint_multiplier if self.is_sprinting else self.speed
        
        # Get current facing angle (default to 0 if never set)
        if not hasattr(self, 'direction_angle'):
            self.direction_angle = 0
        
        # Determine forward/backward first so we can flip rotation when moving backward
        is_forward = (input_handler.get_key(pygame.K_w) or input_handler.get_key(pygame.K_UP))
        is_backward = (input_handler.get_key(pygame.K_s) or input_handler.get_key(pygame.K_DOWN))
        forward_tmp = 1 if is_forward else (-1 if is_backward else 0)

        # ROTATION INPUT: A/Left = Rotate Left, D/Right = Rotate Right
        # When moving backward (S), flip A/D so steering reverses (tank controls)
        rotation_speed = 5  # degrees per frame
        rot_sign = -1 if forward_tmp == -1 else 1
        
        if input_handler.get_key(pygame.K_a) or input_handler.get_key(pygame.K_LEFT):
            self.direction_angle -= rotation_speed * rot_sign
        if input_handler.get_key(pygame.K_d) or input_handler.get_key(pygame.K_RIGHT):
            self.direction_angle += rotation_speed * rot_sign
        
        # Keep angle in 0-360 range
        self.direction_angle = self.direction_angle % 360
        
        # Update cardinal direction based on angle (for visual facing)
        angle = self.direction_angle
        if angle < 22.5 or angle >= 337.5:
            self.direction = "right"
        elif 22.5 <= angle < 67.5:
            self.direction = "down-right"
        elif 67.5 <= angle < 112.5:
            self.direction = "down"
        elif 112.5 <= angle < 157.5:
            self.direction = "down-left"
        elif 157.5 <= angle < 202.5:
            self.direction = "left"
        elif 202.5 <= angle < 247.5:
            self.direction = "up-left"
        elif 247.5 <= angle < 292.5:
            self.direction = "up"
        else:  # 292.5 <= angle < 337.5
            self.direction = "up-right"
        
        # MOVEMENT INPUT: W/Up = Forward, S/Down = Backward
        forward = forward_tmp
        
        # Calculate velocity based on facing angle and forward input
        if forward != 0:
            angle_rad = math.radians(self.direction_angle)
            
            # Move in direction player is facing (or opposite if backward)
            self.velocity[0] = math.cos(angle_rad) * forward * current_speed
            self.velocity[1] = math.sin(angle_rad) * forward * current_speed
            self.is_moving = True
        else:
            self.velocity = [0.0, 0.0]
            self.is_moving = False
        
        # Attack input (Left Mouse Button). get_mouse_button(0) == left in pygame.get_pressed()
        if input_handler.get_mouse_button(0) and self.attack_cooldown == 0:
            self.is_attacking = True
            self.attack_cooldown = self.attack_cooldown_time

    def update(self, dt: float = 1.0, bounds: Optional[Tuple[int, int, int, int]] = None):
        """
        Update player position and state.
        
        Args:
            dt: Delta time for frame-rate independent movement
            bounds: (min_x, min_y, max_x, max_y) boundary constraints
        """
        # Update sprite animation
        self._update_animation()
        
        # Update position
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # Apply boundary constraints
        if bounds:
            min_x, min_y, max_x, max_y = bounds
            half_size = self.size // 2
            self.position[0] = max(min_x + half_size, min(self.position[0], max_x - half_size))
            self.position[1] = max(min_y + half_size, min(self.position[1], max_y - half_size))
        else:
            # Default screen boundaries
            half_size = self.size // 2
            self.position[0] = max(half_size, min(self.position[0], SCREEN_WIDTH - half_size))
            self.position[1] = max(half_size, min(self.position[1], SCREEN_HEIGHT - half_size))
        
        # Update collision rect
        self.rect.x = int(self.position[0] - self.size // 2)
        self.rect.y = int(self.position[1] - self.size // 2)
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.attack_cooldown == 0:
            self.is_attacking = False

    def move(self, direction: str, dt: float = 1.0):
        """
        Legacy move method for backward compatibility.
        
        Args:
            direction: 'up', 'down', 'left', or 'right'
            dt: Delta time multiplier
        """
        if direction == 'up':
            self.position[1] -= self.speed * dt
        elif direction == 'down':
            self.position[1] += self.speed * dt
        elif direction == 'left':
            self.position[0] -= self.speed * dt
        elif direction == 'right':
            self.position[0] += self.speed * dt
        
        self.direction = direction
        self.update(dt)

    def take_damage(self, amount: int) -> bool:
        """
        Apply damage to the player, accounting for defense.
        
        Args:
            amount: Raw damage amount
            
        Returns:
            True if player is still alive, False otherwise
        """
        actual_damage = max(1, amount - self.defense)  # Minimum 1 damage
        self.health -= actual_damage
        if self.health < 0:
            self.health = 0
        return self.health > 0

    def heal(self, amount: int):
        """
        Heal the player, not exceeding max health.
        
        Args:
            amount: Amount of health to restore
        """
        self.health = min(self.max_health, self.health + amount)

    def add_to_inventory(self, item):
        """
        Add an item to the player's inventory.
        
        Args:
            item: Item object to add
        """
        self.inventory.append(item)
        
    def remove_from_inventory(self, item):
        """
        Remove an item from the player's inventory.
        
        Args:
            item: Item object to remove
        """
        if item in self.inventory:
            self.inventory.remove(item)

    def is_alive(self) -> bool:
        """Check if player is still alive."""
        return self.health > 0
    
    def get_attack_rect(self) -> pygame.Rect:
        """
        Get the attack hitbox based on current direction (8 directions).
        
        Returns:
            Pygame Rect representing the attack range
        """
        import math
        
        attack_range = 40
        attack_width = 30
        
        # Use direction_angle if available, otherwise use cardinal direction
        angle = getattr(self, 'direction_angle', 0)
        
        # Normalize angle to 0-360
        angle = angle % 360
        
        # Determine direction from angle (8 directions)
        # Each direction covers 45 degrees
        # 0° = right, 45° = down-right, 90° = down, etc.
        
        if angle < 22.5 or angle >= 337.5:
            # Right (0°)
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - attack_width // 2,
                attack_range,
                attack_width
            )
        elif 22.5 <= angle < 67.5:
            # Down-Right (45°)
            return pygame.Rect(
                self.rect.right - attack_width // 2,
                self.rect.bottom - attack_width // 2,
                attack_range,
                attack_range
            )
        elif 67.5 <= angle < 112.5:
            # Down (90°)
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.bottom,
                attack_width,
                attack_range
            )
        elif 112.5 <= angle < 157.5:
            # Down-Left (135°)
            return pygame.Rect(
                self.rect.left - attack_range + attack_width // 2,
                self.rect.bottom - attack_width // 2,
                attack_range,
                attack_range
            )
        elif 157.5 <= angle < 202.5:
            # Left (180°)
            return pygame.Rect(
                self.rect.left - attack_range,
                self.rect.centery - attack_width // 2,
                attack_range,
                attack_width
            )
        elif 202.5 <= angle < 247.5:
            # Up-Left (225°)
            return pygame.Rect(
                self.rect.left - attack_range + attack_width // 2,
                self.rect.top - attack_range + attack_width // 2,
                attack_range,
                attack_range
            )
        elif 247.5 <= angle < 292.5:
            # Up (270°)
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.top - attack_range,
                attack_width,
                attack_range
            )
        else:  # 292.5 <= angle < 337.5
            # Up-Right (315°)
            return pygame.Rect(
                self.rect.right - attack_width // 2,
                self.rect.top - attack_range + attack_width // 2,
                attack_range,
                attack_range
            )

    def _update_animation(self):
        """Update sprite animation frames."""
        if not self.sprite_frames:
            return
        
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            if self.is_moving:
                # Alternate between walk frames (frames 2 and 3)
                if self.current_frame in [0, 1]:
                    self.current_frame = 2
                elif self.current_frame == 2:
                    self.current_frame = 3
                else:  # current_frame == 3
                    self.current_frame = 2
            else:
                # Alternate between idle frames (frames 0 and 1)
                if self.current_frame in [2, 3]:
                    self.current_frame = 0
                elif self.current_frame == 0:
                    self.current_frame = 1
                else:  # current_frame == 1
                    self.current_frame = 0

    def draw(self, surface: pygame.Surface):
        """
        Draw the player on the screen with sprite animation.
        Player always faces upward in screen space while world rotates.
        
        Args:
            surface: Pygame surface to draw on
        """
        import math
        
        center_x, center_y = self.rect.center
        
        # Draw sprite if loaded, otherwise fallback to colored shapes
        if self.sprite_frames:
            # Get current animation frame
            sprite = self.sprite_frames[self.current_frame]
            # Center the sprite on player position
            sprite_rect = sprite.get_rect(center=(center_x, center_y))
            surface.blit(sprite, sprite_rect)
        else:
            # Fallback: Draw player body (green square)
            pygame.draw.rect(surface, GREEN, self.rect)
            
            # Draw a triangle pointing upward (player's facing direction in screen space)
            half_size = self.size // 2
            points = [
                (center_x, center_y - half_size),  # Top point (forward)
                (center_x - half_size // 2, center_y + half_size // 2),  # Bottom left
                (center_x + half_size // 2, center_y + half_size // 2),  # Bottom right
            ]
            pygame.draw.polygon(surface, (0, 200, 0), points)
            pygame.draw.polygon(surface, WHITE, points, 2)
            
            # Draw a small dot at center
            pygame.draw.circle(surface, WHITE, (center_x, center_y), 3)
        
        # Note: attack hitbox visualization is drawn by the Game renderer on the world surface
        # so it aligns with world rotation. We don't draw it here to avoid mismatch.
        
        # Draw health bar above player
        health_bar_width = self.size
        health_bar_height = 4
        health_bar_x = self.rect.x
        health_bar_y = self.rect.y - 8
        
        # Background (red)
        pygame.draw.rect(surface, RED, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health (green)
        health_ratio = self.health / self.max_health
        current_health_width = int(health_bar_width * health_ratio)
        pygame.draw.rect(surface, GREEN,
                        (health_bar_x, health_bar_y, current_health_width, health_bar_height))

    def __str__(self):
        return (f"Player {self.name}: Health={self.health}/{self.max_health}, "
                f"Position={tuple(self.position)}, Items={len(self.inventory)}")
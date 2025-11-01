"""
Infinite Tower Engine - Player Entity Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
from typing import Tuple, List, Optional
from ..config import (
    PLAYER_HEALTH, PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT,
    GREEN, WHITE, RED
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
        self.size = 32  # Player sprite size
        self.inventory = []
        
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
        
        # ROTATION INPUT: A/Left = Rotate Left, D/Right = Rotate Right
        # Rotation speed in degrees per frame
        rotation_speed = 5  # degrees per frame
        
        if input_handler.get_key(pygame.K_a) or input_handler.get_key(pygame.K_LEFT):
            self.direction_angle -= rotation_speed  # Rotate left (counter-clockwise)
        if input_handler.get_key(pygame.K_d) or input_handler.get_key(pygame.K_RIGHT):
            self.direction_angle += rotation_speed  # Rotate right (clockwise)
        
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
        forward = 0
        
        if input_handler.get_key(pygame.K_w) or input_handler.get_key(pygame.K_UP):
            forward = 1  # Move forward
        if input_handler.get_key(pygame.K_s) or input_handler.get_key(pygame.K_DOWN):
            forward = -1  # Move backward
        
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
        
        # Attack input (Left Mouse Button)
        if input_handler.get_mouse_button(1) and self.attack_cooldown == 0:
            self.is_attacking = True
            self.attack_cooldown = self.attack_cooldown_time

    def update(self, dt: float = 1.0, bounds: Optional[Tuple[int, int, int, int]] = None):
        """
        Update player position and state.
        
        Args:
            dt: Delta time for frame-rate independent movement
            bounds: (min_x, min_y, max_x, max_y) boundary constraints
        """
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

    def draw(self, surface: pygame.Surface):
        """
        Draw the player on the screen with rotation based on direction_angle.
        
        Args:
            surface: Pygame surface to draw on
        """
        import math
        
        # Draw player body (green square for now - will be replaced with sprite)
        pygame.draw.rect(surface, GREEN, self.rect)
        
        # Since the world rotates around the player, the player always faces "up" on screen
        # Draw a simple arrow/triangle shape pointing up to show this
        center_x, center_y = self.rect.center
        
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
        
        # Draw attack hitbox when attacking (debug visualization)
        if self.is_attacking:
            attack_rect = self.get_attack_rect()
            pygame.draw.rect(surface, RED, attack_rect, 2)
        
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
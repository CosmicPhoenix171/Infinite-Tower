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
        self.sprint_multiplier = 2.0  # Sprint is 2x normal speed
        self.is_sprinting = False
        self.size = 32  # Player sprite size
        self.inventory = []
        
        # Combat stats
        self.attack_power = 10
        self.defense = 0
        self.is_attacking = False
        self.attack_cooldown = 0
        self.attack_cooldown_time = 30  # frames
        
        # Animation and state
        self.direction = "down"  # up, down, left, right
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
        Handle player input for movement using WASD or Arrow keys.
        
        Args:
            input_handler: InputHandler instance for checking key states
        """
        self.velocity = [0.0, 0.0]
        self.is_moving = False
        
        # Check if sprinting (Shift key)
        self.is_sprinting = (input_handler.get_key(pygame.K_LSHIFT) or 
                            input_handler.get_key(pygame.K_RSHIFT))
        
        # Apply sprint multiplier
        current_speed = self.speed * self.sprint_multiplier if self.is_sprinting else self.speed
        
        # Movement input (WASD and Arrow keys)
        if input_handler.get_key(pygame.K_w) or input_handler.get_key(pygame.K_UP):
            self.velocity[1] = -current_speed
            self.direction = "up"
            self.is_moving = True
        if input_handler.get_key(pygame.K_s) or input_handler.get_key(pygame.K_DOWN):
            self.velocity[1] = current_speed
            self.direction = "down"
            self.is_moving = True
        if input_handler.get_key(pygame.K_a) or input_handler.get_key(pygame.K_LEFT):
            self.velocity[0] = -current_speed
            self.direction = "left"
            self.is_moving = True
        if input_handler.get_key(pygame.K_d) or input_handler.get_key(pygame.K_RIGHT):
            self.velocity[0] = current_speed
            self.direction = "right"
            self.is_moving = True
            
        # Normalize diagonal movement
        if self.velocity[0] != 0 and self.velocity[1] != 0:
            self.velocity[0] *= 0.707  # 1/sqrt(2)
            self.velocity[1] *= 0.707
        
        # Attack input (Space key)
        if input_handler.get_key(pygame.K_SPACE) and self.attack_cooldown == 0:
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
        Get the attack hitbox based on current direction.
        
        Returns:
            Pygame Rect representing the attack range
        """
        attack_range = 40
        attack_width = 30
        
        if self.direction == "up":
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.top - attack_range,
                attack_width,
                attack_range
            )
        elif self.direction == "down":
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.bottom,
                attack_width,
                attack_range
            )
        elif self.direction == "left":
            return pygame.Rect(
                self.rect.left - attack_range,
                self.rect.centery - attack_width // 2,
                attack_range,
                attack_width
            )
        else:  # right
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - attack_width // 2,
                attack_range,
                attack_width
            )

    def draw(self, surface: pygame.Surface):
        """
        Draw the player on the screen.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw player (green square for now - will be replaced with sprite)
        pygame.draw.rect(surface, GREEN, self.rect)
        
        # Draw direction indicator
        center_x, center_y = self.rect.center
        indicator_length = 15
        
        if self.direction == "up":
            end_pos = (center_x, center_y - indicator_length)
        elif self.direction == "down":
            end_pos = (center_x, center_y + indicator_length)
        elif self.direction == "left":
            end_pos = (center_x - indicator_length, center_y)
        else:  # right
            end_pos = (center_x + indicator_length, center_y)
        
        pygame.draw.line(surface, WHITE, (center_x, center_y), end_pos, 2)
        
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
"""
Infinite Tower Engine - Enemy Entity Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
import random
import math
from typing import Tuple, Optional, List
from enum import Enum
from ..systems.ai import AI, AIBehaviorType
from ..config import RED, WHITE, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT
from ..systems.physics import Physics


class EnemyType(Enum):
    """Types of enemies with different characteristics."""
    BASIC = "basic"
    TANK = "tank"
    RANGER = "ranger"
    FAST = "fast"
    BOSS = "boss"


class Enemy:
    """
    Enemy entity with AI, combat, and rendering capabilities.
    
    Attributes:
        name: Enemy name
        enemy_type: Type of enemy (affects stats and behavior)
        health: Current health
        max_health: Maximum health
        damage: Attack damage (attack_power)
        defense: Damage reduction
        speed: Movement speed
        position: (x, y) position
        size: Sprite size
        ai: AI controller
        rect: Collision rectangle
    """
    
    def __init__(self, name: str, health: int, damage: int, speed: float,
                 position: Tuple[float, float] = None, 
                 enemy_type: EnemyType = EnemyType.BASIC):
        self.name = name
        self.enemy_type = enemy_type
        self.max_health = health
        self.health = health
        self.attack_power = damage  # Using attack_power for consistency with combat system
        self.damage = damage  # Keep for backward compatibility
        self.defense = 0
        self.speed = speed
        
        # Position and rendering
        self.position = list(position) if position else [100, 100]
        self.size = 28
        self.color = self._get_color_for_type()
        self.direction = "down"
        # 360° facing and movement like the player
        self.direction_angle = 0.0  # degrees, 0=right, 90=down, 180=left, 270=up
        self.velocity = [0.0, 0.0]
        self.rotation_speed = 5.0  # degrees per frame
        # Intent set by AI each frame
        self._desired_angle = 0.0
        self._move_intent = 0  # -1 back, 0 idle, +1 forward
        self.is_attacking = False
        
        # Combat stats
        self.attack_range = 50
        self.attack_cooldown = 0
        self.base_attack_cooldown = 90  # Base cooldown in frames (~1.5 seconds at 60 FPS)
        self.crit_chance = 0.05  # 5% crit chance
        self.block_chance = 0.0
        # ...existing code...
        
        # Collision
        self.rect = pygame.Rect(
            self.position[0] - self.size // 2,
            self.position[1] - self.size // 2,
            self.size,
            self.size
        )
        
        # AI Controller
        ai_behavior = self._get_ai_behavior_for_type()
        self.ai = AI(self, ai_behavior)
        
        # Configure stats based on type
        self._configure_by_type()
    
    def _get_color_for_type(self) -> Tuple[int, int, int]:
        """Get display color based on enemy type."""
        colors = {
            EnemyType.BASIC: (200, 50, 50),      # Red
            EnemyType.TANK: (100, 100, 150),     # Blue-gray
            EnemyType.RANGER: (150, 100, 200),   # Purple
            EnemyType.FAST: (200, 150, 50),      # Orange
            EnemyType.BOSS: (150, 0, 0),         # Dark red
        }
        return colors.get(self.enemy_type, RED)
    
    def _get_ai_behavior_for_type(self) -> AIBehaviorType:
        """Get AI behavior based on enemy type."""
        behaviors = {
            EnemyType.BASIC: AIBehaviorType.AGGRESSIVE,
            EnemyType.TANK: AIBehaviorType.TANK,
            EnemyType.RANGER: AIBehaviorType.RANGER,
            EnemyType.FAST: AIBehaviorType.AGGRESSIVE,
            EnemyType.BOSS: AIBehaviorType.AGGRESSIVE,
        }
        return behaviors.get(self.enemy_type, AIBehaviorType.AGGRESSIVE)
    
    def _configure_by_type(self):
        """Configure enemy stats based on type."""
        if self.enemy_type == EnemyType.TANK:
            self.max_health = int(self.max_health * 2)
            self.health = self.max_health
            self.defense = 5
            self.speed *= 0.6
            self.size = 36
            self.block_chance = 0.15
            self.base_attack_cooldown = 120  # Slower attack (2 seconds)
            
        elif self.enemy_type == EnemyType.RANGER:
            self.attack_range = 150
            self.speed *= 0.8
            self.defense = 1
            self.base_attack_cooldown = 100  # Medium attack (1.67 seconds)
            
        elif self.enemy_type == EnemyType.FAST:
            self.speed *= 1.5
            self.health = int(self.health * 0.7)
            self.max_health = self.health
            self.size = 24
            self.base_attack_cooldown = 75  # Faster attack (1.25 seconds)
            
        elif self.enemy_type == EnemyType.BOSS:
            self.max_health = int(self.max_health * 5)
            self.health = self.max_health
            self.attack_power = int(self.attack_power * 2)
            self.damage = self.attack_power
            self.defense = 10
            self.speed *= 0.7
            self.size = 48
            self.crit_chance = 0.15
            self.block_chance = 0.1
            self.base_attack_cooldown = 100  # Boss attack (1.67 seconds)
        
        # Update rect size
        self.rect.width = self.size
        self.rect.height = self.size
    
    def update(self, player, dt: float = 1.0, obstacles: Optional[list] = None, bounds: Optional[tuple[int,int,int,int]] = None):
        """
        Update enemy state and AI.
        
        Args:
            player: Player entity
            dt: Delta time
            obstacles: List of obstacle rects
        """
        if not self.is_alive():
            return
        
        # Update AI (sets desired angle and move intent)
        self.ai.update(player, obstacles)

        # Rotate toward desired angle (shortest arc)
        diff = (self._desired_angle - self.direction_angle + 540) % 360 - 180
        if diff > 0:
            self.direction_angle += min(self.rotation_speed, diff)
        else:
            self.direction_angle += max(-self.rotation_speed, diff)
        self.direction_angle %= 360

        # Update movement based on facing and intent
        if self._move_intent != 0:
            ang = math.radians(self.direction_angle)
            self.velocity[0] = math.cos(ang) * self.speed * self._move_intent
            self.velocity[1] = math.sin(ang) * self.speed * self._move_intent
        else:
            self.velocity[0] = 0.0
            self.velocity[1] = 0.0
        
        # Apply movement
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        
        # Update collision rect
        self.rect.x = int(self.position[0] - self.size // 2)
        self.rect.y = int(self.position[1] - self.size // 2)
        
        # Keep within bounds (world bounds preferred, screen as fallback)
        half_size = self.size // 2
        if bounds:
            min_x, min_y, max_x, max_y = bounds
            self.position[0] = max(min_x + half_size, min(self.position[0], max_x - half_size))
            self.position[1] = max(min_y + half_size, min(self.position[1], max_y - half_size))
        else:
            self.position[0] = max(half_size, min(self.position[0], SCREEN_WIDTH - half_size))
            self.position[1] = max(half_size, min(self.position[1], SCREEN_HEIGHT - half_size))
        # Sync rect after bounds clamp
        self.rect.x = int(self.position[0] - self.size // 2)
        self.rect.y = int(self.position[1] - self.size // 2)
        
        # Resolve collisions against static obstacles (e.g., walls)
        if obstacles:
            self._resolve_wall_collisions(obstacles)
            # Sync logical position to rect center after resolution
            self.position[0] = self.rect.centerx
            self.position[1] = self.rect.centery
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Reset attack flag
        if self.attack_cooldown == 0:
            self.is_attacking = False

    def _resolve_wall_collisions(self, obstacles: Optional[List]):
        """
        Push the enemy out of any overlapping wall/obstacle using minimal overlap.
        Accepts a list of Wall objects or pygame.Rects.
        """
        if not obstacles:
            return
        for obj in obstacles:
            wall_rect = getattr(obj, 'rect', obj)
            if not isinstance(wall_rect, pygame.Rect):
                continue
            if self.rect.colliderect(wall_rect):
                side = Physics.get_collision_side(self.rect, wall_rect, (0, 0))
                if side == "left":
                    self.rect.right = wall_rect.left
                elif side == "right":
                    self.rect.left = wall_rect.right
                elif side == "top":
                    self.rect.bottom = wall_rect.top
                elif side == "bottom":
                    self.rect.top = wall_rect.bottom
    
    def move(self, direction: str):
        """
        Legacy move method for backward compatibility.
        
        Args:
            direction: "up", "down", "left", or "right"
        """
        if direction == "up":
            self.position[1] -= self.speed
        elif direction == "down":
            self.position[1] += self.speed
        elif direction == "left":
            self.position[0] -= self.speed
        elif direction == "right":
            self.position[0] += self.speed
        
        self.direction = direction
        self.rect.x = int(self.position[0] - self.size // 2)
        self.rect.y = int(self.position[1] - self.size // 2)
    
    def attack(self, target):
        """
        Legacy attack method for backward compatibility.
        
        Args:
            target: Target entity to attack
        """
        if self.attack_cooldown == 0:
            target.health -= self.damage
            self.is_attacking = True
            self.attack_cooldown = 60
    
    def take_damage(self, amount: int) -> bool:
        """
        Take damage, accounting for defense.
        
        Args:
            amount: Damage amount
            
        Returns:
            True if still alive
        """
        actual_damage = max(1, amount - self.defense)
        self.health -= actual_damage
        if self.health < 0:
            self.health = 0
        return self.is_alive()
    
    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self.health > 0
    
    def get_attack_rect(self) -> pygame.Rect:
        """Get attack hitbox using 8-direction logic based on direction_angle."""
        attack_range = 40
        attack_width = 30
        angle = self.direction_angle % 360
        
        if angle < 22.5 or angle >= 337.5:
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - attack_width // 2,
                attack_range,
                attack_width,
            )
        elif 22.5 <= angle < 67.5:
            return pygame.Rect(
                self.rect.right - attack_width // 2,
                self.rect.bottom - attack_width // 2,
                attack_range,
                attack_range,
            )
        elif 67.5 <= angle < 112.5:
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.bottom,
                attack_width,
                attack_range,
            )
        elif 112.5 <= angle < 157.5:
            return pygame.Rect(
                self.rect.left - attack_range + attack_width // 2,
                self.rect.bottom - attack_width // 2,
                attack_range,
                attack_range,
            )
        elif 157.5 <= angle < 202.5:
            return pygame.Rect(
                self.rect.left - attack_range,
                self.rect.centery - attack_width // 2,
                attack_range,
                attack_width,
            )
        elif 202.5 <= angle < 247.5:
            return pygame.Rect(
                self.rect.left - attack_range + attack_width // 2,
                self.rect.top - attack_range + attack_width // 2,
                attack_range,
                attack_range,
            )
        elif 247.5 <= angle < 292.5:
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.top - attack_range,
                attack_width,
                attack_range,
            )
        else:
            return pygame.Rect(
                self.rect.right - attack_width // 2,
                self.rect.top - attack_range + attack_width // 2,
                attack_range,
                attack_range,
            )
    
    def draw(self, surface: pygame.Surface):
        """
        Draw the enemy on screen.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw enemy (colored square based on type)
        pygame.draw.rect(surface, self.color, self.rect)
        
        # Draw border
        border_color = WHITE if not self.is_attacking else RED
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Draw direction indicator using direction_angle
        center_x, center_y = self.rect.center
        indicator_length = 12
        end_pos = (
            int(center_x + math.cos(math.radians(self.direction_angle)) * indicator_length),
            int(center_y + math.sin(math.radians(self.direction_angle)) * indicator_length),
        )
        
        pygame.draw.line(surface, BLACK, (center_x, center_y), end_pos, 2)
        
        # Draw health bar above enemy
        health_bar_width = self.size
        health_bar_height = 4
        health_bar_x = self.rect.x
        health_bar_y = self.rect.y - 8
        
        # Background (red)
        pygame.draw.rect(surface, RED,
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health (varies by enemy type color)
        health_ratio = self.health / self.max_health
        current_health_width = int(health_bar_width * health_ratio)
        health_color = (50, 200, 50)  # Green
        pygame.draw.rect(surface, health_color,
                        (health_bar_x, health_bar_y, current_health_width, health_bar_height))
        
        # Floating name above enemy
        font = pygame.font.Font(None, 20)
        name_text = font.render(self.name, True, WHITE)
        name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.y - 18))
        surface.blit(name_text, name_rect)
        
        # Draw attack range indicator when attacking (debug)
        if self.is_attacking:
            attack_rect = self.get_attack_rect()
            pygame.draw.rect(surface, (255, 100, 100), attack_rect, 1)
    
    def set_patrol_points(self, points: list):
        """
        Set patrol points for this enemy's AI.
        
        Args:
            points: List of (x, y) patrol coordinates
        """
        self.ai.set_patrol_points(points)
    
    def get_drops(self) -> list:
        """
        Get loot drops when enemy is defeated.
        
        Returns:
            List of loot items (to be implemented with loot system)
        """
        drops = []
        drop_chance = 0.3  # 30% base drop chance
        
        # Boss enemies always drop loot
        if self.enemy_type == EnemyType.BOSS:
            drop_chance = 1.0
        
        if random.random() < drop_chance:
            # Placeholder loot (will be replaced with actual loot system)
            drops.append({
                'type': 'health_potion',
                'value': 20,
                'position': tuple(self.position)
            })
        
        return drops
    
    def __str__(self):
        return (f"{self.name} ({self.enemy_type.value}): "
                f"Health={self.health}/{self.max_health}, "
                f"Damage={self.damage}, Position={tuple(self.position)}")
"""
Infinite Tower Engine - Enemy Entity Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
import random
from typing import Tuple, Optional
from enum import Enum
from ..systems.ai import AI, AIBehaviorType
from ..config import RED, WHITE, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT


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
        self.is_attacking = False
        
        # Combat stats
        self.attack_range = 50
        self.attack_cooldown = 0
        self.crit_chance = 0.05  # 5% crit chance
        self.block_chance = 0.0
        
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
            
        elif self.enemy_type == EnemyType.RANGER:
            self.attack_range = 150
            self.speed *= 0.8
            self.defense = 1
            
        elif self.enemy_type == EnemyType.FAST:
            self.speed *= 1.5
            self.health = int(self.health * 0.7)
            self.max_health = self.health
            self.size = 24
            
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
        
        # Update rect size
        self.rect.width = self.size
        self.rect.height = self.size
    
    def update(self, player, dt: float = 1.0, obstacles: Optional[list] = None):
        """
        Update enemy state and AI.
        
        Args:
            player: Player entity
            dt: Delta time
            obstacles: List of obstacle rects
        """
        if not self.is_alive():
            return
        
        # Update AI
        self.ai.update(player, obstacles)
        
        # Update collision rect
        self.rect.x = int(self.position[0] - self.size // 2)
        self.rect.y = int(self.position[1] - self.size // 2)
        
        # Keep within bounds
        half_size = self.size // 2
        self.position[0] = max(half_size, min(self.position[0], SCREEN_WIDTH - half_size))
        self.position[1] = max(half_size, min(self.position[1], SCREEN_HEIGHT - half_size))
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Reset attack flag
        if self.attack_cooldown == 0:
            self.is_attacking = False
    
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
        """
        Get attack hitbox based on direction.
        
        Returns:
            Attack rectangle
        """
        attack_width = 30
        
        if self.direction == "up":
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.top - self.attack_range,
                attack_width,
                self.attack_range
            )
        elif self.direction == "down":
            return pygame.Rect(
                self.rect.centerx - attack_width // 2,
                self.rect.bottom,
                attack_width,
                self.attack_range
            )
        elif self.direction == "left":
            return pygame.Rect(
                self.rect.left - self.attack_range,
                self.rect.centery - attack_width // 2,
                self.attack_range,
                attack_width
            )
        else:  # right
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - attack_width // 2,
                self.attack_range,
                attack_width
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
        
        # Draw direction indicator
        center_x, center_y = self.rect.center
        indicator_length = 12
        
        if self.direction == "up":
            end_pos = (center_x, center_y - indicator_length)
        elif self.direction == "down":
            end_pos = (center_x, center_y + indicator_length)
        elif self.direction == "left":
            end_pos = (center_x - indicator_length, center_y)
        else:  # right
            end_pos = (center_x + indicator_length, center_y)
        
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
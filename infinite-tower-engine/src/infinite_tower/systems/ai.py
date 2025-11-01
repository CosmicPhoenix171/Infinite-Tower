"""
Infinite Tower Engine - AI System Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import random
import math
from enum import Enum
from typing import Tuple, List, Optional


class AIState(Enum):
    """AI behavior states."""
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    WANDER = "wander"
    DEAD = "dead"


class AIBehaviorType(Enum):
    """AI personality types."""
    AGGRESSIVE = "aggressive"  # Always attacks on sight
    DEFENSIVE = "defensive"    # Attacks when provoked
    COWARD = "coward"         # Flees when health is low
    TANK = "tank"             # Slow but strong
    RANGER = "ranger"         # Keeps distance and attacks from range


class AI:
    """
    Advanced AI system for enemy behavior and decision-making.
    
    Features:
    - State machine for behavior management
    - Pathfinding and movement
    - Combat decision-making
    - Multiple AI personality types
    """
    
    def __init__(self, entity, behavior_type: AIBehaviorType = AIBehaviorType.AGGRESSIVE):
        self.entity = entity
        self.behavior_type = behavior_type
        self.state = AIState.IDLE
        self.target = None
        
        # Detection and awareness
        self.detection_range = 200
        self.attack_range = 50
        self.flee_health_threshold = 0.25  # Flee when below 25% health
        
        # Patrol settings
        self.patrol_points = []
        self.current_patrol_index = 0
        self.patrol_wait_time = 60  # frames
        self.patrol_wait_counter = 0
        
        # Wander settings
        self.wander_target = None
        self.wander_cooldown = 0
        self.wander_cooldown_max = 120  # frames
        
        # Attack cooldown
        self.attack_cooldown = 0
        self.attack_cooldown_max = 60  # frames
        
        # Memory and decision-making
        self.last_known_target_position = None
        self.search_timer = 0
        self.search_duration = 180  # frames to search before giving up
        
        # Configure based on behavior type
        self._configure_behavior()
    
    def _configure_behavior(self):
        """Configure AI parameters based on behavior type."""
        if self.behavior_type == AIBehaviorType.AGGRESSIVE:
            self.detection_range = 250
            self.attack_range = 50
            self.flee_health_threshold = 0.0  # Never flees
            
        elif self.behavior_type == AIBehaviorType.DEFENSIVE:
            self.detection_range = 150
            self.attack_range = 60
            self.flee_health_threshold = 0.15
            
        elif self.behavior_type == AIBehaviorType.COWARD:
            self.detection_range = 200
            self.attack_range = 40
            self.flee_health_threshold = 0.5  # Flees early
            
        elif self.behavior_type == AIBehaviorType.TANK:
            self.detection_range = 150
            self.attack_range = 70
            self.flee_health_threshold = 0.0
            if hasattr(self.entity, 'speed'):
                self.entity.speed *= 0.7  # Slower movement
            
        elif self.behavior_type == AIBehaviorType.RANGER:
            self.detection_range = 300
            self.attack_range = 150
            self.flee_health_threshold = 0.3
    
    def update(self, player, obstacles: Optional[List] = None):
        """
        Update AI logic and decide actions.
        
        Args:
            player: Player entity
            obstacles: List of obstacle rects (for pathfinding)
        """
        if not self.entity.is_alive():
            self.state = AIState.DEAD
            return
        
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.wander_cooldown > 0:
            self.wander_cooldown -= 1
        
        # Decide next action based on current state
        self.decide_action(player)
        
        # Execute current state behavior
        if self.state == AIState.IDLE:
            self.idle_behavior()
        elif self.state == AIState.PATROL:
            self.patrol()
        elif self.state == AIState.CHASE:
            self.chase_target(obstacles)
        elif self.state == AIState.ATTACK:
            self.attack_target(player)
        elif self.state == AIState.FLEE:
            self.flee_from_target(player, obstacles)
        elif self.state == AIState.WANDER:
            self.wander()
    
    def decide_action(self, player):
        """
        Main decision-making logic.
        
        Args:
            player: Player entity
        """
        if not hasattr(self.entity, 'position') or not hasattr(player, 'position'):
            return
        
        # Calculate distance to player
        distance = self._calculate_distance(self.entity.position, player.position)
        
        # Check if should flee
        if self._should_flee():
            self.state = AIState.FLEE
            self.target = player
            return
        
        # Check if player is in detection range
        if distance <= self.detection_range:
            self.target = player
            self.last_known_target_position = tuple(player.position) if isinstance(player.position, list) else player.position
            
            # Get actual attack hitbox range (use entity's attack_range for better positioning)
            attack_hitbox_range = self.entity.attack_range if hasattr(self.entity, 'attack_range') else self.attack_range
            optimal_distance = attack_hitbox_range + self.entity.size + 20  # Stay at edge of hitbox + buffer
            
            # Decide between attack, chase, and positioning
            if distance <= optimal_distance:
                # Already in optimal range, attack if cooldown ready
                if distance <= attack_hitbox_range and self.attack_cooldown == 0:
                    self.state = AIState.ATTACK
                else:
                    # In range but not in attack rect, hold position or reposition
                    self.state = AIState.CHASE  # Will move to stay in optimal range
            else:
                # Too far, chase to get closer
                self.state = AIState.CHASE
        else:
            # Lost sight of player
            if self.target is not None:
                # Search for player at last known position
                if self.search_timer < self.search_duration:
                    self.state = AIState.CHASE
                    self.search_timer += 1
                else:
                    # Give up searching
                    self.target = None
                    self.last_known_target_position = None
                    self.search_timer = 0
                    self.state = AIState.WANDER
            else:
                # No target, patrol or wander
                if len(self.patrol_points) > 0:
                    self.state = AIState.PATROL
                else:
                    self.state = AIState.WANDER
    
    def idle_behavior(self):
        """Idle state - do nothing or look around."""
        # Occasionally switch to wander if no patrol points
        if len(self.patrol_points) == 0 and random.random() < 0.01:
            self.state = AIState.WANDER
    
    def move_towards_player(self, player_position: Tuple[float, float]):
        """
        Move entity towards player position.
        
        Args:
            player_position: (x, y) player coordinates
        """
        self.move_towards_position(player_position)
    
    def move_towards_position(self, target_pos: Tuple[float, float]):
        """
        Move entity towards a target position.
        
        Args:
            target_pos: (x, y) target coordinates
        """
        if not hasattr(self.entity, 'position') or not hasattr(self.entity, 'speed'):
            return
        
        entity_pos = self.entity.position if isinstance(self.entity.position, tuple) else tuple(self.entity.position)
        
        # Calculate direction
        dx = target_pos[0] - entity_pos[0]
        dy = target_pos[1] - entity_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize and apply speed
            dx = (dx / distance) * self.entity.speed
            dy = (dy / distance) * self.entity.speed
            
            # Update position
            if isinstance(self.entity.position, list):
                self.entity.position[0] += dx
                self.entity.position[1] += dy
            else:
                self.entity.position = (entity_pos[0] + dx, entity_pos[1] + dy)
            
            # Update direction for rendering
            if abs(dx) > abs(dy):
                self.entity.direction = "right" if dx > 0 else "left"
            else:
                self.entity.direction = "down" if dy > 0 else "up"
    
    def chase_target(self, obstacles: Optional[List] = None):
        """
        Chase the current target while maintaining optimal attack range.
        
        Args:
            obstacles: List of obstacle rects
        """
        if not self.target:
            if self.last_known_target_position:
                self.move_towards_position(self.last_known_target_position)
            return
        
        target_pos = self.target.position if isinstance(self.target.position, tuple) else tuple(self.target.position)
        entity_pos = self.entity.position if isinstance(self.entity.position, tuple) else tuple(self.entity.position)
        
        # Calculate current distance
        distance = self._calculate_distance(entity_pos, target_pos)
        
        # Get optimal range based on attack hitbox
        attack_hitbox_range = self.entity.attack_range if hasattr(self.entity, 'attack_range') else self.attack_range
        optimal_distance = attack_hitbox_range + self.entity.size + 20
        
        # If too far, move closer
        if distance > optimal_distance:
            self.move_towards_position(target_pos)
        # If too close, move back
        elif distance < optimal_distance - 30:
            # Move away from target
            dx = entity_pos[0] - target_pos[0]
            dy = entity_pos[1] - target_pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                move_dist = min(self.entity.speed, 5)  # Small steps backward
                move_x = (dx / dist) * move_dist
                move_y = (dy / dist) * move_dist
                if isinstance(self.entity.position, list):
                    self.entity.position[0] += move_x
                    self.entity.position[1] += move_y
                
                # Update direction
                if abs(dx) > abs(dy):
                    self.entity.direction = "right" if dx > 0 else "left"
                else:
                    self.entity.direction = "down" if dy > 0 else "up"
        # Otherwise maintain position (don't move)
    
    def attack_target(self, player):
        """
        Attack the player.
        
        Args:
            player: Player entity
        """
        if self.attack_cooldown == 0:
            # Perform attack (will be handled by combat system)
            self.entity.is_attacking = True
            self.attack_cooldown = self.attack_cooldown_max
            
            # Face the player
            if hasattr(self.entity, 'position') and hasattr(player, 'position'):
                entity_pos = self.entity.position if isinstance(self.entity.position, tuple) else tuple(self.entity.position)
                player_pos = player.position if isinstance(player.position, tuple) else tuple(player.position)
                
                dx = player_pos[0] - entity_pos[0]
                dy = player_pos[1] - entity_pos[1]
                
                if abs(dx) > abs(dy):
                    self.entity.direction = "right" if dx > 0 else "left"
                else:
                    self.entity.direction = "down" if dy > 0 else "up"
    
    def flee_from_target(self, player, obstacles: Optional[List] = None):
        """
        Flee away from the target.
        
        Args:
            player: Player entity
            obstacles: List of obstacle rects
        """
        if not hasattr(self.entity, 'position') or not hasattr(player, 'position'):
            return
        
        entity_pos = self.entity.position if isinstance(self.entity.position, tuple) else tuple(self.entity.position)
        player_pos = player.position if isinstance(player.position, tuple) else tuple(player.position)
        
        # Calculate direction away from player
        dx = entity_pos[0] - player_pos[0]
        dy = entity_pos[1] - player_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Move away
            flee_target = (
                entity_pos[0] + (dx / distance) * 100,
                entity_pos[1] + (dy / distance) * 100
            )
            self.move_towards_position(flee_target)
    
    def patrol(self):
        """Execute patrol behavior."""
        if len(self.patrol_points) == 0:
            return
        
        if self.patrol_wait_counter > 0:
            self.patrol_wait_counter -= 1
            return
        
        target_point = self.patrol_points[self.current_patrol_index]
        entity_pos = self.entity.position if isinstance(self.entity.position, tuple) else tuple(self.entity.position)
        
        distance = self._calculate_distance(entity_pos, target_point)
        
        if distance < 10:  # Reached patrol point
            self.patrol_wait_counter = self.patrol_wait_time
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            self.move_towards_position(target_point)
    
    def wander(self):
        """Execute random wandering behavior."""
        if self.wander_target is None or self.wander_cooldown == 0:
            # Pick a new random target nearby
            entity_pos = self.entity.position if isinstance(self.entity.position, tuple) else tuple(self.entity.position)
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 150)
            
            self.wander_target = (
                entity_pos[0] + math.cos(angle) * distance,
                entity_pos[1] + math.sin(angle) * distance
            )
            self.wander_cooldown = self.wander_cooldown_max
        
        entity_pos = self.entity.position if isinstance(self.entity.position, tuple) else tuple(self.entity.position)
        distance = self._calculate_distance(entity_pos, self.wander_target)
        
        if distance < 10:  # Reached wander target
            self.wander_target = None
        else:
            self.move_towards_position(self.wander_target)
    
    def set_patrol_points(self, points: List[Tuple[float, float]]):
        """
        Set patrol points for patrol behavior.
        
        Args:
            points: List of (x, y) coordinates
        """
        self.patrol_points = points
        self.current_patrol_index = 0
    
    def _should_flee(self) -> bool:
        """
        Check if AI should flee based on health and behavior.
        
        Returns:
            True if should flee
        """
        if not hasattr(self.entity, 'health') or not hasattr(self.entity, 'max_health'):
            return False
        
        health_ratio = self.entity.health / self.entity.max_health
        return health_ratio < self.flee_health_threshold
    
    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            pos1: (x, y) first point
            pos2: (x, y) second point
            
        Returns:
            Distance
        """
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def get_state(self) -> AIState:
        """Get current AI state."""
        return self.state
    
    def set_state(self, state: AIState):
        """Set AI state."""
        self.state = state
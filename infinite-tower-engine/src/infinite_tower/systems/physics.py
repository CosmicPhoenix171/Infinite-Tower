"""
Infinite Tower Engine - Physics System Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
import math
from typing import List, Tuple, Optional, Set


class Physics:
    """
    Comprehensive physics system for collision detection, movement, and spatial queries.
    """
    
    def __init__(self):
        self.spatial_grid = {}
        self.cell_size = 64  # Grid cell size for spatial partitioning
    
    # ===== Collision Detection =====
    
    @staticmethod
    def check_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """
        Check AABB (Axis-Aligned Bounding Box) collision between two rectangles.
        
        Args:
            rect1: First rectangle
            rect2: Second rectangle
            
        Returns:
            True if rectangles overlap
        """
        return rect1.colliderect(rect2)
    
    @staticmethod
    def check_circle_collision(pos1: Tuple[float, float], radius1: float,
                              pos2: Tuple[float, float], radius2: float) -> bool:
        """
        Check circle-to-circle collision.
        
        Args:
            pos1: (x, y) center of first circle
            radius1: Radius of first circle
            pos2: (x, y) center of second circle
            radius2: Radius of second circle
            
        Returns:
            True if circles overlap
        """
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < (radius1 + radius2)
    
    @staticmethod
    def check_point_in_rect(point: Tuple[float, float], rect: pygame.Rect) -> bool:
        """
        Check if a point is inside a rectangle.
        
        Args:
            point: (x, y) coordinates
            rect: Rectangle to check
            
        Returns:
            True if point is inside rectangle
        """
        return rect.collidepoint(point)
    
    @staticmethod
    def get_collision_side(moving_rect: pygame.Rect, static_rect: pygame.Rect,
                          velocity: Tuple[float, float]) -> Optional[str]:
        """
        Determine which side of the static rect the moving rect hit.
        
        Args:
            moving_rect: The moving object's rectangle
            static_rect: The stationary object's rectangle
            velocity: (vx, vy) velocity vector
            
        Returns:
            "top", "bottom", "left", "right", or None
        """
        if not moving_rect.colliderect(static_rect):
            return None
        
        # Calculate overlap on each axis
        overlap_left = moving_rect.right - static_rect.left
        overlap_right = static_rect.right - moving_rect.left
        overlap_top = moving_rect.bottom - static_rect.top
        overlap_bottom = static_rect.bottom - moving_rect.top
        
        # Find minimum overlap
        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
        
        if min_overlap == overlap_left:
            return "left"
        elif min_overlap == overlap_right:
            return "right"
        elif min_overlap == overlap_top:
            return "top"
        else:
            return "bottom"
    
    # ===== Movement and Position =====
    
    @staticmethod
    def move(rect: pygame.Rect, dx: float, dy: float) -> pygame.Rect:
        """
        Move a rectangle by the given delta values.
        
        Args:
            rect: Rectangle to move
            dx: X displacement
            dy: Y displacement
            
        Returns:
            Updated rectangle
        """
        rect.x += int(dx)
        rect.y += int(dy)
        return rect
    
    @staticmethod
    def move_with_collision(rect: pygame.Rect, dx: float, dy: float,
                           obstacles: List[pygame.Rect]) -> Tuple[pygame.Rect, bool, bool]:
        """
        Move a rectangle while checking for collisions with obstacles.
        
        Args:
            rect: Rectangle to move
            dx: X displacement
            dy: Y displacement
            obstacles: List of obstacle rectangles
            
        Returns:
            (updated_rect, collided_x, collided_y)
        """
        collided_x = False
        collided_y = False
        
        # Try X movement
        rect.x += int(dx)
        for obstacle in obstacles:
            if rect.colliderect(obstacle):
                # Revert X movement
                rect.x -= int(dx)
                collided_x = True
                break
        
        # Try Y movement
        rect.y += int(dy)
        for obstacle in obstacles:
            if rect.colliderect(obstacle):
                # Revert Y movement
                rect.y -= int(dy)
                collided_y = True
                break
        
        return rect, collided_x, collided_y
    
    @staticmethod
    def apply_gravity(rect: pygame.Rect, gravity: float, ground_level: int) -> pygame.Rect:
        """
        Apply gravity to a rectangle until it reaches ground level.
        
        Args:
            rect: Rectangle to apply gravity to
            gravity: Gravity force (pixels per frame)
            ground_level: Y coordinate of ground
            
        Returns:
            Updated rectangle
        """
        if rect.y < ground_level:
            rect.y += int(gravity)
        else:
            rect.y = ground_level
        return rect
    
    @staticmethod
    def clamp_to_bounds(rect: pygame.Rect, min_x: int, min_y: int,
                       max_x: int, max_y: int) -> pygame.Rect:
        """
        Clamp a rectangle to stay within specified bounds.
        
        Args:
            rect: Rectangle to clamp
            min_x, min_y: Minimum coordinates
            max_x, max_y: Maximum coordinates
            
        Returns:
            Clamped rectangle
        """
        rect.x = max(min_x, min(rect.x, max_x - rect.width))
        rect.y = max(min_y, min(rect.y, max_y - rect.height))
        return rect
    
    # ===== Distance and Direction =====
    
    @staticmethod
    def distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            pos1: (x, y) first point
            pos2: (x, y) second point
            
        Returns:
            Distance between points
        """
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def manhattan_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        Calculate Manhattan distance (grid-based) between two points.
        
        Args:
            pos1: (x, y) first point
            pos2: (x, y) second point
            
        Returns:
            Manhattan distance
        """
        return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])
    
    @staticmethod
    def direction_to(from_pos: Tuple[float, float], to_pos: Tuple[float, float]) -> Tuple[float, float]:
        """
        Get normalized direction vector from one point to another.
        
        Args:
            from_pos: Starting (x, y) position
            to_pos: Target (x, y) position
            
        Returns:
            (dx, dy) normalized direction vector
        """
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return (0, 0)
        
        return (dx / distance, dy / distance)
    
    @staticmethod
    def angle_between(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        Calculate angle in radians from pos1 to pos2.
        
        Args:
            pos1: Starting (x, y) position
            pos2: Target (x, y) position
            
        Returns:
            Angle in radians
        """
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return math.atan2(dy, dx)
    
    # ===== Spatial Partitioning =====
    
    def update_spatial_grid(self, entities: List) -> None:
        """
        Update spatial partitioning grid for efficient collision queries.
        
        Args:
            entities: List of entities with 'rect' attribute
        """
        self.spatial_grid.clear()
        
        for entity in entities:
            if not hasattr(entity, 'rect'):
                continue
            
            # Get grid cells this entity occupies
            cells = self._get_occupied_cells(entity.rect)
            
            for cell in cells:
                if cell not in self.spatial_grid:
                    self.spatial_grid[cell] = []
                self.spatial_grid[cell].append(entity)
    
    def _get_occupied_cells(self, rect: pygame.Rect) -> Set[Tuple[int, int]]:
        """
        Get all grid cells occupied by a rectangle.
        
        Args:
            rect: Rectangle to check
            
        Returns:
            Set of (grid_x, grid_y) tuples
        """
        cells = set()
        
        min_cell_x = rect.left // self.cell_size
        max_cell_x = rect.right // self.cell_size
        min_cell_y = rect.top // self.cell_size
        max_cell_y = rect.bottom // self.cell_size
        
        for cx in range(min_cell_x, max_cell_x + 1):
            for cy in range(min_cell_y, max_cell_y + 1):
                cells.add((cx, cy))
        
        return cells
    
    def get_nearby_entities(self, rect: pygame.Rect) -> List:
        """
        Get entities near the given rectangle using spatial partitioning.
        
        Args:
            rect: Query rectangle
            
        Returns:
            List of nearby entities
        """
        cells = self._get_occupied_cells(rect)
        nearby = set()
        
        for cell in cells:
            if cell in self.spatial_grid:
                nearby.update(self.spatial_grid[cell])
        
        return list(nearby)
    
    # ===== Raycasting =====
    
    @staticmethod
    def raycast(start: Tuple[float, float], end: Tuple[float, float],
               obstacles: List[pygame.Rect]) -> Optional[Tuple[float, float]]:
        """
        Simple raycast to check line of sight.
        
        Args:
            start: (x, y) starting point
            end: (x, y) ending point
            obstacles: List of obstacle rectangles
            
        Returns:
            Hit point (x, y) or None if no collision
        """
        steps = 100
        dx = (end[0] - start[0]) / steps
        dy = (end[1] - start[1]) / steps
        
        x, y = start
        for _ in range(steps):
            x += dx
            y += dy
            point = (int(x), int(y))
            
            for obstacle in obstacles:
                if obstacle.collidepoint(point):
                    return (x, y)
        
        return None
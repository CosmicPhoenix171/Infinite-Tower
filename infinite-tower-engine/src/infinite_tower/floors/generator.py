"""
Infinite Tower Engine - Procedural Floor Generator Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import random
import pygame
from typing import List, Tuple, Dict, Optional
from enum import Enum
from ..entities.enemy import Enemy, EnemyType
from ..items.loot import LootGenerator
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK


class RoomType(Enum):
    """Types of rooms in the floor."""
    NORMAL = "normal"
    TREASURE = "treasure"
    BOSS = "boss"
    SAFE = "safe"
    CHALLENGE = "challenge"


class TileType(Enum):
    """Types of tiles."""
    FLOOR = 0
    WALL = 1
    DOOR = 2
    SPAWN = 3
    EXIT = 4


class Room:
    """
    Individual room in a floor.
    
    Attributes:
        x, y: Room position in grid
        width, height: Room dimensions (in tiles)
        room_type: Type of room
        tiles: 2D array of tile types
        enemies: List of enemy spawn positions
        loot: List of loot spawn positions
        doors: List of door positions
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 room_type: RoomType = RoomType.NORMAL):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type
        self.tiles = []
        self.enemies = []
        self.loot = []
        self.doors = []
        self.visited = False
        
        self._generate_tiles()
    
    def _generate_tiles(self):
        """Generate the tile layout for this room."""
        self.tiles = []
        for row in range(self.height):
            tile_row = []
            for col in range(self.width):
                # Walls on edges, floor inside
                if row == 0 or row == self.height - 1 or col == 0 or col == self.width - 1:
                    tile_row.append(TileType.WALL)
                else:
                    tile_row.append(TileType.FLOOR)
            self.tiles.append(tile_row)
    
    def add_door(self, side: str):
        """
        Add a door on the specified side.
        
        Args:
            side: "top", "bottom", "left", or "right"
        """
        mid_w = self.width // 2
        mid_h = self.height // 2
        
        if side == "top" and mid_w < self.width:
            self.tiles[0][mid_w] = TileType.DOOR
            self.doors.append(("top", mid_w, 0))
        elif side == "bottom" and mid_w < self.width:
            self.tiles[self.height - 1][mid_w] = TileType.DOOR
            self.doors.append(("bottom", mid_w, self.height - 1))
        elif side == "left" and mid_h < self.height:
            self.tiles[mid_h][0] = TileType.DOOR
            self.doors.append(("left", 0, mid_h))
        elif side == "right" and mid_h < self.height:
            self.tiles[mid_h][self.width - 1] = TileType.DOOR
            self.doors.append(("right", self.width - 1, mid_h))
    
    def add_enemy_spawn(self, x: int, y: int):
        """Add an enemy spawn point."""
        if 0 < x < self.width - 1 and 0 < y < self.height - 1:
            self.enemies.append((x, y))
    
    def add_loot_spawn(self, x: int, y: int):
        """Add a loot spawn point."""
        if 0 < x < self.width - 1 and 0 < y < self.height - 1:
            self.loot.append((x, y))
    
    def get_center(self) -> Tuple[int, int]:
        """Get center position of room."""
        return (self.x + self.width // 2, self.y + self.height // 2)


class FloorGenerator:
    """
    Procedural floor generator using seed-based random generation.
    
    Creates interconnected rooms with enemies, loot, and paths.
    """
    
    def __init__(self, seed: str):
        self.seed = seed
        random.seed(seed)
        self.rooms = []
        self.floor_level = 1
        self.loot_generator = LootGenerator(hash(seed))
        
        # Generation parameters
        self.tile_size = 32  # Size of each tile in pixels
        self.room_grid_size = 5  # 5x5 grid of possible room positions
    
    def generate_floor(self, num_rooms: int = 5, floor_level: int = 1) -> List[Room]:
        """
        Generate a complete floor with interconnected rooms.
        
        Args:
            num_rooms: Number of rooms to generate
            floor_level: Current floor number (affects difficulty)
            
        Returns:
            List of Room objects
        """
        self.floor_level = floor_level
        self.rooms = []
        
        # Reset random seed for consistent generation
        random.seed(self.seed + str(floor_level))
        
        # Generate rooms in a grid pattern
        self._generate_room_layout(num_rooms)
        
        # Connect rooms with doors
        self._connect_rooms()
        
        # Populate rooms with enemies and loot
        self._populate_rooms()
        
        return self.rooms
    
    def _generate_room_layout(self, num_rooms: int):
        """Generate the layout of rooms."""
        grid = {}  # {(grid_x, grid_y): Room}
        
        # Start with first room in center
        center = self.room_grid_size // 2
        current_pos = (center, center)
        
        for i in range(num_rooms):
            # Determine room type
            if i == 0:
                room_type = RoomType.SAFE  # Starting room
            elif i == num_rooms - 1:
                room_type = RoomType.BOSS  # Final room
            elif random.random() < 0.15:
                room_type = RoomType.TREASURE
            elif random.random() < 0.1:
                room_type = RoomType.CHALLENGE
            else:
                room_type = RoomType.NORMAL
            
            # Create room
            width = random.randint(8, 15)
            height = random.randint(8, 15)
            room = Room(current_pos[0], current_pos[1], width, height, room_type)
            
            grid[current_pos] = room
            self.rooms.append(room)
            
            # Find next position (adjacent to existing room)
            if i < num_rooms - 1:
                current_pos = self._find_next_room_position(grid)
        
        return grid
    
    def _find_next_room_position(self, grid: Dict) -> Tuple[int, int]:
        """Find a valid position for the next room adjacent to existing rooms."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # down, up, right, left
        
        # Get all occupied positions
        occupied = list(grid.keys())
        random.shuffle(occupied)
        
        # Try to find empty adjacent position
        for pos in occupied:
            random.shuffle(directions)
            for dx, dy in directions:
                new_pos = (pos[0] + dx, pos[1] + dy)
                
                # Check if position is valid and empty
                if (0 <= new_pos[0] < self.room_grid_size and 
                    0 <= new_pos[1] < self.room_grid_size and
                    new_pos not in grid):
                    return new_pos
        
        # Fallback: find any empty spot
        for x in range(self.room_grid_size):
            for y in range(self.room_grid_size):
                if (x, y) not in grid:
                    return (x, y)
        
        return (0, 0)
    
    def _connect_rooms(self):
        """Connect adjacent rooms with doors."""
        for i, room1 in enumerate(self.rooms):
            for room2 in self.rooms[i+1:]:
                # Check if rooms are adjacent
                dx = abs(room1.x - room2.x)
                dy = abs(room1.y - room2.y)
                
                if dx == 1 and dy == 0:
                    # Horizontally adjacent
                    if room1.x < room2.x:
                        room1.add_door("right")
                        room2.add_door("left")
                    else:
                        room1.add_door("left")
                        room2.add_door("right")
                
                elif dx == 0 and dy == 1:
                    # Vertically adjacent
                    if room1.y < room2.y:
                        room1.add_door("bottom")
                        room2.add_door("top")
                    else:
                        room1.add_door("top")
                        room2.add_door("bottom")
    
    def _populate_rooms(self):
        """Populate rooms with enemies and loot."""
        for room in self.rooms:
            if room.room_type == RoomType.SAFE:
                # Safe rooms have no enemies
                self._add_loot_to_room(room, 1)
            
            elif room.room_type == RoomType.BOSS:
                # Boss room has one boss enemy
                center = room.get_center()
                room.add_enemy_spawn(center[0], center[1])
                self._add_loot_to_room(room, 3)
            
            elif room.room_type == RoomType.TREASURE:
                # Treasure rooms have extra loot, few enemies
                self._add_enemies_to_room(room, 1)
                self._add_loot_to_room(room, 5)
            
            elif room.room_type == RoomType.CHALLENGE:
                # Challenge rooms have many enemies, good loot
                self._add_enemies_to_room(room, 5)
                self._add_loot_to_room(room, 3)
            
            else:  # NORMAL
                # Normal rooms have moderate enemies and loot
                num_enemies = random.randint(2, 4)
                self._add_enemies_to_room(room, num_enemies)
                self._add_loot_to_room(room, random.randint(1, 2))
    
    def _add_enemies_to_room(self, room: Room, count: int):
        """Add enemy spawn points to a room."""
        for _ in range(count):
            # Random position in room (not on walls)
            x = random.randint(2, room.width - 3)
            y = random.randint(2, room.height - 3)
            room.add_enemy_spawn(x, y)
    
    def _add_loot_to_room(self, room: Room, count: int):
        """Add loot spawn points to a room."""
        for _ in range(count):
            x = random.randint(2, room.width - 3)
            y = random.randint(2, room.height - 3)
            room.add_loot_spawn(x, y)
    
    def create_room(self) -> Dict:
        """
        Legacy method for backward compatibility.
        
        Returns:
            Dictionary with room data
        """
        width = random.randint(5, 15)
        height = random.randint(5, 15)
        return {
            'width': width,
            'height': height,
            'enemies': self.generate_enemies(),
            'loot': self.generate_loot()
        }
    
    def generate_enemies(self) -> List[Dict]:
        """Legacy method for backward compatibility."""
        num_enemies = random.randint(0, 5)
        return [{'type': 'enemy', 'strength': random.randint(1, 10)} 
                for _ in range(num_enemies)]
    
    def generate_loot(self) -> List[Dict]:
        """Legacy method for backward compatibility."""
        num_loot = random.randint(0, 3)
        return [{'type': 'loot', 'value': random.randint(1, 100)} 
                for _ in range(num_loot)]
    
    def spawn_enemies(self, room: Room) -> List[Enemy]:
        """
        Create Enemy entities from room spawn points.
        
        Args:
            room: Room to spawn enemies in
            
        Returns:
            List of Enemy instances
        """
        enemies = []
        
        for spawn_x, spawn_y in room.enemies:
            # Convert grid position to pixel position
            pixel_x = (room.x * 20 + spawn_x) * self.tile_size
            pixel_y = (room.y * 20 + spawn_y) * self.tile_size
            
            # Determine enemy type based on room and floor level
            if room.room_type == RoomType.BOSS:
                enemy_type = EnemyType.BOSS
                health = 100 + self.floor_level * 50
                damage = 15 + self.floor_level * 3
                speed = 2
            else:
                # Random enemy type
                type_roll = random.random()
                if type_roll < 0.1:
                    enemy_type = EnemyType.TANK
                elif type_roll < 0.2:
                    enemy_type = EnemyType.RANGER
                elif type_roll < 0.3:
                    enemy_type = EnemyType.FAST
                else:
                    enemy_type = EnemyType.BASIC
                
                health = 30 + self.floor_level * 10
                damage = 5 + self.floor_level * 2
                speed = 2
            
            name = f"{enemy_type.value.capitalize()} Enemy"
            enemy = Enemy(name, health, damage, speed, (pixel_x, pixel_y), enemy_type)
            enemies.append(enemy)
        
        return enemies
    
    def spawn_loot(self, room: Room) -> List:
        """
        Create loot items from room spawn points.
        
        Args:
            room: Room to spawn loot in
            
        Returns:
            List of Item instances
        """
        loot_items = []
        
        for spawn_x, spawn_y in room.loot:
            # Convert grid position to pixel position
            pixel_x = (room.x * 20 + spawn_x) * self.tile_size
            pixel_y = (room.y * 20 + spawn_y) * self.tile_size
            
            # Generate loot item
            item = self.loot_generator.generate_random_item(self.floor_level)
            item.set_position(pixel_x, pixel_y)
            loot_items.append(item)
        
        return loot_items
    
    def draw_floor_map(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """
        Draw the floor map (for minimap or debug view).
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: (x, y) camera offset
        """
        for room in self.rooms:
            # Calculate screen position
            screen_x = room.x * 20 * self.tile_size - camera_offset[0]
            screen_y = room.y * 20 * self.tile_size - camera_offset[1]
            
            # Draw room tiles
            for row_idx, row in enumerate(room.tiles):
                for col_idx, tile in enumerate(row):
                    tile_x = screen_x + col_idx * self.tile_size
                    tile_y = screen_y + row_idx * self.tile_size
                    tile_rect = pygame.Rect(tile_x, tile_y, self.tile_size, self.tile_size)
                    
                    if tile == TileType.WALL:
                        pygame.draw.rect(surface, (100, 100, 100), tile_rect)
                    elif tile == TileType.FLOOR:
                        pygame.draw.rect(surface, (60, 60, 60), tile_rect)
                    elif tile == TileType.DOOR:
                        pygame.draw.rect(surface, (150, 100, 50), tile_rect)
                    
                    # Draw tile border
                    pygame.draw.rect(surface, BLACK, tile_rect, 1)
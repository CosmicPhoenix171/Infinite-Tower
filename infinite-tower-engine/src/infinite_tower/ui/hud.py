"""
Infinite Tower Engine - HUD (Heads-Up Display) Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
from typing import Optional, List
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, 
    BLUE, BACKGROUND_COLOR
)


class HUD:
    """
    Comprehensive HUD system displaying player stats, inventory, and game info.
    
    Features:
    - Health and stats bars
    - Minimap (placeholder)
    - Inventory quick-slots
    - Damage numbers
    - Status effects
    - Floor information
    """
    
    def __init__(self, screen: pygame.Surface, player):
        self.screen = screen
        self.player = player
        
        # Fonts
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
        except:
            self.font_large = pygame.font.SysFont('arial', 48)
            self.font_medium = pygame.font.SysFont('arial', 36)
            self.font_small = pygame.font.SysFont('arial', 24)
        
        # HUD State
        self.current_floor = 1
        self.show_inventory = False
        self.damage_numbers = []  # [(text, x, y, lifetime, color)]
        self.notifications = []   # [(text, lifetime)]
        
        # HUD Layout
        self.hud_padding = 10
        self.bar_height = 20
        self.bar_width = 200
    
    def update(self, dt: float = 1.0):
        """
        Update HUD animations and temporary elements.
        
        Args:
            dt: Delta time
        """
        # Update damage numbers
        expired_damage = []
        for i, damage_num in enumerate(self.damage_numbers):
            text, x, y, lifetime, color = damage_num
            lifetime -= 1
            if lifetime <= 0:
                expired_damage.append(i)
            else:
                # Float upward
                y -= 1
                self.damage_numbers[i] = (text, x, y, lifetime, color)
        
        # Remove expired damage numbers
        for i in reversed(expired_damage):
            self.damage_numbers.pop(i)
        
        # Update notifications
        expired_notifs = []
        for i, notif in enumerate(self.notifications):
            text, lifetime = notif
            lifetime -= 1
            if lifetime <= 0:
                expired_notifs.append(i)
            else:
                self.notifications[i] = (text, lifetime)
        
        for i in reversed(expired_notifs):
            self.notifications.pop(i)
    
    def draw(self):
        """Draw all HUD elements."""
        self.draw_player_stats()
        self.draw_floor_info()
        self.draw_inventory_quickslots()
        self.draw_minimap()
        self.draw_damage_numbers()
        self.draw_notifications()
        
        if self.show_inventory:
            self.draw_inventory_panel()
    
    def draw_player_stats(self):
        """Draw player health, mana, and stats bars."""
        x = self.hud_padding
        y = self.hud_padding
        
        # Health Bar
        self._draw_stat_bar(
            x, y,
            self.player.health, self.player.max_health,
            "Health", RED, GREEN
        )
        
        # Mana/Stamina Bar (if exists)
        if hasattr(self.player, 'mana') and hasattr(self.player, 'max_mana'):
            self._draw_stat_bar(
                x, y + 30,
                self.player.mana, self.player.max_mana,
                "Mana", (50, 50, 150), BLUE
            )
        
        # Experience/Level (if exists)
        if hasattr(self.player, 'experience'):
            xp_text = f"Level {getattr(self.player, 'level', 1)} - XP: {self.player.experience}"
            xp_surface = self.font_small.render(xp_text, True, WHITE)
            self.screen.blit(xp_surface, (x, y + 60))
    
    def _draw_stat_bar(self, x: int, y: int, current: float, maximum: float,
                       label: str, bg_color: tuple, fg_color: tuple):
        """
        Draw a stat bar (health, mana, etc.).
        
        Args:
            x, y: Position
            current: Current value
            maximum: Maximum value
            label: Label text
            bg_color: Background color
            fg_color: Foreground (fill) color
        """
        # Background
        bg_rect = pygame.Rect(x, y, self.bar_width, self.bar_height)
        pygame.draw.rect(self.screen, bg_color, bg_rect)
        
        # Foreground (current value)
        if maximum > 0:
            fill_ratio = max(0, min(1, current / maximum))
            fill_width = int(self.bar_width * fill_ratio)
            fill_rect = pygame.Rect(x, y, fill_width, self.bar_height)
            pygame.draw.rect(self.screen, fg_color, fill_rect)
        
        # Border
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
        
        # Text label and values
        text = f"{label}: {int(current)}/{int(maximum)}"
        text_surface = self.font_small.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x + self.bar_width // 2, y + self.bar_height // 2))
        self.screen.blit(text_surface, text_rect)
    
    def draw_floor_info(self):
        """Draw current floor and game info."""
        x = SCREEN_WIDTH - 200
        y = self.hud_padding
        
        floor_text = f"FLOOR {self.current_floor}"
        floor_surface = self.font_medium.render(floor_text, True, WHITE)
        floor_rect = floor_surface.get_rect(topright=(SCREEN_WIDTH - self.hud_padding, y))
        
        # Background
        bg_rect = floor_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
        
        self.screen.blit(floor_surface, floor_rect)
    
    def draw_inventory_quickslots(self):
        """Draw quick-access inventory slots."""
        slot_size = 50
        slot_padding = 5
        num_slots = 5
        
        start_x = (SCREEN_WIDTH - (slot_size + slot_padding) * num_slots) // 2
        y = SCREEN_HEIGHT - slot_size - self.hud_padding
        
        for i in range(num_slots):
            x = start_x + i * (slot_size + slot_padding)
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)
            
            # Draw slot background
            pygame.draw.rect(self.screen, (50, 50, 50), slot_rect)
            pygame.draw.rect(self.screen, WHITE, slot_rect, 2)
            
            # Draw item if exists
            if hasattr(self.player, 'inventory') and i < len(self.player.inventory):
                item = self.player.inventory[i]
                # Draw item (placeholder - will use item sprites)
                item_color = getattr(item, 'rarity', None)
                if hasattr(item_color, 'color'):
                    pygame.draw.rect(self.screen, item_color.color, 
                                   slot_rect.inflate(-10, -10))
            
            # Draw slot number
            num_text = str(i + 1)
            num_surface = self.font_small.render(num_text, True, WHITE)
            self.screen.blit(num_surface, (x + 2, y + 2))
    
    def draw_minimap(self):
        """Draw minimap (placeholder for future implementation)."""
        minimap_size = 150
        x = SCREEN_WIDTH - minimap_size - self.hud_padding
        y = SCREEN_HEIGHT - minimap_size - 80
        
        minimap_rect = pygame.Rect(x, y, minimap_size, minimap_size)
        
        # Background
        pygame.draw.rect(self.screen, (20, 20, 40), minimap_rect)
        pygame.draw.rect(self.screen, WHITE, minimap_rect, 2)
        
        # Player position (center)
        player_x = x + minimap_size // 2
        player_y = y + minimap_size // 2
        pygame.draw.circle(self.screen, GREEN, (player_x, player_y), 3)
        
        # Label
        label = self.font_small.render("Map", True, WHITE)
        self.screen.blit(label, (x + 5, y + 5))
    
    def draw_damage_numbers(self):
        """Draw floating damage numbers."""
        for text, x, y, lifetime, color in self.damage_numbers:
            # Fade out based on lifetime
            alpha = min(255, lifetime * 5)
            damage_surface = self.font_medium.render(text, True, color)
            
            # Draw with outline for visibility
            outline_color = BLACK
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                outline_surface = self.font_medium.render(text, True, outline_color)
                self.screen.blit(outline_surface, (x + dx, y + dy))
            
            self.screen.blit(damage_surface, (x, y))
    
    def draw_notifications(self):
        """Draw notification messages."""
        x = SCREEN_WIDTH // 2
        y = 100
        
        for i, (text, lifetime) in enumerate(self.notifications):
            notif_surface = self.font_medium.render(text, True, WHITE)
            notif_rect = notif_surface.get_rect(center=(x, y + i * 40))
            
            # Background
            bg_rect = notif_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
            
            self.screen.blit(notif_surface, notif_rect)
    
    def draw_inventory_panel(self):
        """Draw full inventory panel overlay."""
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Inventory panel
        panel_width = 600
        panel_height = 500
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Title
        title = self.font_large.render("INVENTORY", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 30))
        self.screen.blit(title, title_rect)
        
        # Draw inventory grid
        slot_size = 60
        slots_per_row = 8
        start_x = panel_x + 20
        start_y = panel_y + 80
        
        if hasattr(self.player, 'inventory'):
            for i, item in enumerate(self.player.inventory):
                row = i // slots_per_row
                col = i % slots_per_row
                x = start_x + col * (slot_size + 5)
                y = start_y + row * (slot_size + 5)
                
                slot_rect = pygame.Rect(x, y, slot_size, slot_size)
                pygame.draw.rect(self.screen, (60, 60, 80), slot_rect)
                pygame.draw.rect(self.screen, WHITE, slot_rect, 2)
                
                # Draw item info
                if hasattr(item, 'name'):
                    item_name = self.font_small.render(item.name[:8], True, WHITE)
                    self.screen.blit(item_name, (x + 2, y + 2))
        
        # Instructions
        instructions = self.font_small.render("Press I to close", True, WHITE)
        instr_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 20))
        self.screen.blit(instructions, instr_rect)
    
    def add_damage_number(self, damage: int, x: float, y: float, 
                         color: tuple = (255, 255, 255)):
        """
        Add a floating damage number.
        
        Args:
            damage: Damage amount
            x, y: World position
            color: Text color
        """
        text = str(int(damage))
        lifetime = 60  # frames
        self.damage_numbers.append((text, x, y - 20, lifetime, color))
    
    def add_notification(self, message: str, duration: int = 180):
        """
        Add a notification message.
        
        Args:
            message: Notification text
            duration: Display duration in frames
        """
        self.notifications.append((message, duration))
    
    def set_floor(self, floor_number: int):
        """
        Set the current floor number.
        
        Args:
            floor_number: Floor number to display
        """
        self.current_floor = floor_number
        self.add_notification(f"FLOOR {floor_number}", 120)
    
    def toggle_inventory(self):
        """Toggle inventory panel visibility."""
        self.show_inventory = not self.show_inventory
    
    def handle_input(self, event):
        """
        Handle HUD input events (for inventory toggle, etc).
        
        Args:
            event: Pygame event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB or event.key == pygame.K_i:
                self.toggle_inventory()
                return True
        return False
    
    def draw_health(self):
        """Legacy method for backward compatibility."""
        health_text = f"Health: {self.player.health}"
        health_surface = self.font_medium.render(health_text, True, RED)
        self.screen.blit(health_surface, (10, 10))
    
    def draw_experience(self):
        """Legacy method for backward compatibility."""
        if hasattr(self.player, 'experience'):
            experience_text = f"XP: {self.player.experience}"
            experience_surface = self.font_medium.render(experience_text, True, GREEN)
            self.screen.blit(experience_surface, (10, 50))
    
    def draw_loot(self):
        """Legacy method for backward compatibility."""
        if hasattr(self.player, 'loot_count'):
            loot_text = f"Loot: {self.player.loot_count}"
        else:
            loot_text = f"Items: {len(getattr(self.player, 'inventory', []))}"
        loot_surface = self.font_medium.render(loot_text, True, BLUE)
        self.screen.blit(loot_surface, (10, 90))
"""
Infinite Tower Engine - Inventory UI Module

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
from typing import Optional, List, Tuple
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY


class InventoryUI:
    """
    Advanced inventory management interface.
    
    Features:
    - Grid-based item display
    - Item tooltips
    - Drag and drop (future)
    - Item filtering/sorting
    - Equipment slots
    """
    
    def __init__(self, screen: pygame.Surface, player):
        self.screen = screen
        self.player = player
        self.is_visible = False
        
        # Fonts
        try:
            self.font_large = pygame.font.Font(None, 56)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 28)
            self.font_tiny = pygame.font.Font(None, 20)
        except:
            self.font_large = pygame.font.SysFont('arial', 56)
            self.font_medium = pygame.font.SysFont('arial', 36)
            self.font_small = pygame.font.SysFont('arial', 28)
            self.font_tiny = pygame.font.SysFont('arial', 20)
        
        # Layout
        self.panel_width = 700
        self.panel_height = 550
        self.panel_x = (SCREEN_WIDTH - self.panel_width) // 2
        self.panel_y = (SCREEN_HEIGHT - self.panel_height) // 2
        
        # Grid settings
        self.slot_size = 64
        self.slot_padding = 4
        self.slots_per_row = 8
        self.grid_start_x = self.panel_x + 20
        self.grid_start_y = self.panel_y + 80
        
        # Selection
        self.selected_slot = None
        self.hovered_slot = None
        
        # Categories
        self.current_category = "all"  # all, weapons, armor, consumables
        self.categories = ["all", "weapons", "armor", "consumables", "materials"]
    
    def toggle(self):
        """Toggle inventory visibility."""
        self.is_visible = not self.is_visible
    
    def show(self):
        """Show the inventory."""
        self.is_visible = True
    
    def hide(self):
        """Hide the inventory."""
        self.is_visible = False
    
    def handle_input(self, event) -> bool:
        """
        Handle inventory input.
        
        Args:
            event: Pygame event
            
        Returns:
            True if event was handled
        """
        if not self.is_visible:
            return False
        
        if event.type == pygame.KEYDOWN:
            # Close inventory
            if event.key == pygame.K_TAB or event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                self.hide()
                return True
            
            # Category switching
            elif event.key == pygame.K_1:
                self.current_category = "all"
                return True
            elif event.key == pygame.K_2:
                self.current_category = "weapons"
                return True
            elif event.key == pygame.K_3:
                self.current_category = "armor"
                return True
            elif event.key == pygame.K_4:
                self.current_category = "consumables"
                return True
            elif event.key == pygame.K_5:
                self.current_category = "materials"
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on a slot
            mouse_pos = pygame.mouse.get_pos()
            slot_index = self._get_slot_at_position(mouse_pos)
            
            if slot_index is not None:
                filtered_items = self._get_filtered_items()
                if slot_index < len(filtered_items):
                    self.selected_slot = slot_index
                    # Use item if it's a consumable and right-click
                    if event.button == 3:  # Right click
                        item = filtered_items[slot_index]
                        if hasattr(item, 'use'):
                            item.use(self.player)
                            if item.quantity <= 0:
                                self.player.inventory.remove(item)
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            # Update hovered slot
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_slot = self._get_slot_at_position(mouse_pos)
        
        return False
    
    def _get_slot_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """
        Get the inventory slot index at the given mouse position.
        
        Args:
            pos: (x, y) mouse position
            
        Returns:
            Slot index or None
        """
        x, y = pos
        
        # Check if within grid area
        if (self.grid_start_x <= x <= self.grid_start_x + self.slots_per_row * (self.slot_size + self.slot_padding) and
            self.grid_start_y <= y <= self.grid_start_y + 6 * (self.slot_size + self.slot_padding)):
            
            # Calculate grid position
            grid_x = (x - self.grid_start_x) // (self.slot_size + self.slot_padding)
            grid_y = (y - self.grid_start_y) // (self.slot_size + self.slot_padding)
            
            if 0 <= grid_x < self.slots_per_row:
                slot_index = grid_y * self.slots_per_row + grid_x
                return slot_index
        
        return None
    
    def _get_filtered_items(self) -> List:
        """Get items filtered by current category."""
        if not hasattr(self.player, 'inventory'):
            return []
        
        items = self.player.inventory
        
        if self.current_category == "all":
            return items
        
        # Filter by item type
        filtered = []
        for item in items:
            if not hasattr(item, 'item_type'):
                continue
            
            item_type = item.item_type.value.lower() if hasattr(item.item_type, 'value') else str(item.item_type).lower()
            
            if self.current_category == "weapons" and item_type == "weapon":
                filtered.append(item)
            elif self.current_category == "armor" and item_type == "armor":
                filtered.append(item)
            elif self.current_category == "consumables" and item_type == "consumable":
                filtered.append(item)
            elif self.current_category == "materials" and item_type == "material":
                filtered.append(item)
        
        return filtered
    
    def draw(self):
        """Draw the inventory UI."""
        if not self.is_visible:
            return
        
        # Recompute layout based on current screen size (responsive)
        sw, sh = self.screen.get_size()
        self.panel_x = (sw - self.panel_width) // 2
        self.panel_y = (sh - self.panel_height) // 2
        self.grid_start_x = self.panel_x + 20
        self.grid_start_y = self.panel_y + 80
        
        # Semi-transparent background overlay
        overlay = pygame.Surface((sw, sh))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(self.screen, (40, 40, 60), panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)
        
        # Title
        title = self.font_large.render("INVENTORY", True, WHITE)
        title_rect = title.get_rect(center=(sw // 2, self.panel_y + 35))
        self.screen.blit(title, title_rect)
        
        # Category tabs
        self._draw_category_tabs()
        
        # Item grid
        self._draw_item_grid()
        
        # Item tooltip (if hovering)
        if self.hovered_slot is not None:
            self._draw_item_tooltip()
        
        # Stats panel
        self._draw_stats_panel()
        
        # Instructions
        instructions = [
            "TAB/I/ESC: Close",
            "1-5: Switch Category",
            "Left Click: Select",
            "Right Click: Use Item"
        ]
        y_offset = self.panel_y + self.panel_height - 80
        for instr in instructions:
            text = self.font_tiny.render(instr, True, GRAY)
            self.screen.blit(text, (self.panel_x + 20, y_offset))
            y_offset += 18
    
    def _draw_category_tabs(self):
        """Draw category filter tabs."""
        tab_width = 120
        tab_height = 30
        start_x = self.panel_x + 20
        y = self.panel_y + 60
        
        for i, category in enumerate(self.categories):
            x = start_x + i * (tab_width + 5)
            tab_rect = pygame.Rect(x, y, tab_width, tab_height)
            
            # Highlight active category
            if category == self.current_category:
                pygame.draw.rect(self.screen, (100, 150, 200), tab_rect)
                pygame.draw.rect(self.screen, WHITE, tab_rect, 2)
            else:
                pygame.draw.rect(self.screen, DARK_GRAY, tab_rect)
                pygame.draw.rect(self.screen, GRAY, tab_rect, 1)
            
            # Category label
            label = self.font_small.render(category.capitalize(), True, WHITE)
            label_rect = label.get_rect(center=tab_rect.center)
            self.screen.blit(label, label_rect)
            
            # Hotkey number
            hotkey = self.font_tiny.render(f"({i+1})", True, GRAY)
            self.screen.blit(hotkey, (x + 5, y + 5))
    
    def _draw_item_grid(self):
        """Draw the inventory item grid."""
        filtered_items = self._get_filtered_items()
        
        for i in range(48):  # 6 rows x 8 columns
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            x = self.grid_start_x + col * (self.slot_size + self.slot_padding)
            y = self.grid_start_y + row * (self.slot_size + self.slot_padding)
            
            slot_rect = pygame.Rect(x, y, self.slot_size, self.slot_size)
            
            # Slot background
            if i == self.selected_slot:
                pygame.draw.rect(self.screen, (100, 100, 150), slot_rect)
            elif i == self.hovered_slot:
                pygame.draw.rect(self.screen, (80, 80, 100), slot_rect)
            else:
                pygame.draw.rect(self.screen, (60, 60, 80), slot_rect)
            
            pygame.draw.rect(self.screen, GRAY, slot_rect, 2)
            
            # Draw item if slot has one
            if i < len(filtered_items):
                item = filtered_items[i]
                self._draw_item_in_slot(item, slot_rect)
    
    def _draw_item_in_slot(self, item, slot_rect: pygame.Rect):
        """Draw an item within a slot."""
        # Item color based on rarity
        if hasattr(item, 'rarity'):
            if hasattr(item.rarity, 'color'):
                color = item.rarity.color
            else:
                color = WHITE
        else:
            color = WHITE
        
        # Draw item as colored square (will be replaced with icon)
        item_rect = slot_rect.inflate(-16, -16)
        pygame.draw.rect(self.screen, color, item_rect)
        pygame.draw.rect(self.screen, WHITE, item_rect, 1)
        
        # Draw quantity if stackable
        if hasattr(item, 'stackable') and item.stackable and hasattr(item, 'quantity'):
            qty_text = self.font_tiny.render(str(item.quantity), True, WHITE)
            qty_pos = (slot_rect.right - 18, slot_rect.bottom - 18)
            
            # Background for quantity
            qty_bg = pygame.Rect(qty_pos[0] - 2, qty_pos[1] - 2, 20, 16)
            pygame.draw.rect(self.screen, BLACK, qty_bg)
            
            self.screen.blit(qty_text, qty_pos)
    
    def _draw_item_tooltip(self):
        """Draw tooltip for hovered item."""
        filtered_items = self._get_filtered_items()
        
        if self.hovered_slot is None or self.hovered_slot >= len(filtered_items):
            return
        
        item = filtered_items[self.hovered_slot]
        mouse_pos = pygame.mouse.get_pos()
        
        # Tooltip dimensions
        tooltip_width = 250
        tooltip_height = 150
        tooltip_x = min(mouse_pos[0] + 15, SCREEN_WIDTH - tooltip_width - 10)
        tooltip_y = min(mouse_pos[1] + 15, SCREEN_HEIGHT - tooltip_height - 10)
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        # Tooltip background
        pygame.draw.rect(self.screen, (20, 20, 40), tooltip_rect)
        pygame.draw.rect(self.screen, WHITE, tooltip_rect, 2)
        
        # Item name with rarity color
        name_color = item.rarity.color if hasattr(item, 'rarity') and hasattr(item.rarity, 'color') else WHITE
        name_text = self.font_small.render(item.name, True, name_color)
        self.screen.blit(name_text, (tooltip_x + 10, tooltip_y + 10))
        
        y_offset = tooltip_y + 40
        
        # Item type and rarity
        if hasattr(item, 'item_type'):
            type_str = item.item_type.value.capitalize() if hasattr(item.item_type, 'value') else str(item.item_type)
            rarity_str = item.rarity.rarity_name.capitalize() if hasattr(item, 'rarity') else ""
            info_text = self.font_tiny.render(f"{type_str} - {rarity_str}", True, GRAY)
            self.screen.blit(info_text, (tooltip_x + 10, y_offset))
            y_offset += 20
        
        # Item stats
        if hasattr(item, 'stats'):
            for stat_name, stat_value in item.stats.items():
                stat_text = self.font_tiny.render(f"{stat_name}: {stat_value}", True, WHITE)
                self.screen.blit(stat_text, (tooltip_x + 10, y_offset))
                y_offset += 18
        
        # Item description
        if hasattr(item, 'description') and item.description:
            # Word wrap description
            words = item.description.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.font_tiny.size(test_line)[0] < tooltip_width - 20:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            if current_line:
                lines.append(current_line)
            
            for line in lines[:3]:  # Max 3 lines
                desc_text = self.font_tiny.render(line.strip(), True, GRAY)
                self.screen.blit(desc_text, (tooltip_x + 10, y_offset))
                y_offset += 16
    
    def _draw_stats_panel(self):
        """Draw player stats summary."""
        stats_x = self.panel_x + self.panel_width - 180
        stats_y = self.panel_y + 100
        
        # Total items
        total_items = len(self.player.inventory) if hasattr(self.player, 'inventory') else 0
        stats = [
            f"Total Items: {total_items}",
            f"Attack: {self.player.attack_power}",
            f"Defense: {self.player.defense}",
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_small.render(stat, True, WHITE)
            self.screen.blit(stat_text, (stats_x, stats_y + i * 30))

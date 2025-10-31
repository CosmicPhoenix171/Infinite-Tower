"""
Infinite Tower Engine - Full Game UI Module (16-bit Style)

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.

Complete game UI with 16-bit SNES-style aesthetic using placeholder boxes.
"""

import pygame
from typing import Optional, List, Tuple
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, RED, BLUE


class GameUI:
    """
    Complete 16-bit style game UI system.
    
    Features:
    - Health/Mana bars with pixel art style
    - Mini-map in corner
    - Equipment slots
    - Quick inventory slots
    - Experience bar
    - Status effects display
    - Damage numbers
    - Dialog boxes
    - Menu overlays
    """
    
    # 16-bit color palette (SNES-inspired)
    COLORS = {
        # UI Frame colors
        'frame_dark': (40, 40, 48),
        'frame_light': (80, 80, 96),
        'frame_border': (160, 160, 176),
        'frame_highlight': (200, 200, 216),
        
        # Bar colors
        'health_full': (224, 64, 64),
        'health_mid': (224, 128, 64),
        'health_low': (224, 192, 64),
        'mana_full': (64, 128, 224),
        'exp_full': (224, 224, 64),
        'stamina_full': (64, 224, 128),
        
        # Background
        'bg_dark': (16, 16, 24),
        'bg_panel': (32, 32, 40),
        
        # Text
        'text_white': (248, 248, 248),
        'text_gray': (160, 160, 176),
        'text_yellow': (248, 224, 64),
        'text_green': (64, 248, 128),
        'text_red': (248, 64, 64),
        
        # Rarity colors (from loot system)
        'common': (200, 200, 200),
        'uncommon': (100, 255, 100),
        'rare': (100, 100, 255),
        'epic': (200, 100, 255),
        'legendary': (255, 150, 0),
    }
    
    def __init__(self, screen: pygame.Surface, player):
        self.screen = screen
        self.player = player
        # Width/height are recomputed every frame to support resize/fullscreen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        
        # Dynamic layout (updated each frame for responsive UI)
        self.scale = 1.0
        self.ui_margin = 8
        self.ui_padding = 4
        self.bar_height = 12
        self.slot_size = 32

        # Fonts (scaled per frame)
        self.font_large = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)
        
        # UI State
        self.show_minimap = True
        self.show_stats = True
        self.show_quickbar = True
        self.show_equipment = False
        
        # Damage numbers
        self.damage_numbers = []
        
        # Notifications
        self.notifications = []
        
        # Dialog state
        self.current_dialog = None
        
        # Floor info
        self.current_floor = 1
        self.floor_name = "Tower Entrance"
        
    def _update_layout(self):
        """Recompute sizing/scale based on current screen size."""
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()
        # Reference 1280x720; clamp scale between 0.75 and 2.0
        ref_w, ref_h = 1280, 720
        self.scale = max(0.75, min(2.0, min(self.width / ref_w, self.height / ref_h)))

        self.ui_margin = int(12 * self.scale)
        self.ui_padding = int(6 * self.scale)
        self.bar_height = int(14 * self.scale)
        self.slot_size = int(48 * self.scale)

        # Update fonts if size changed significantly
        base_large = max(22, int(24 * self.scale))
        base_medium = max(18, int(20 * self.scale))
        base_small = max(14, int(16 * self.scale))
        self.font_large = pygame.font.Font(None, base_large)
        self.font_medium = pygame.font.Font(None, base_medium)
        self.font_small = pygame.font.Font(None, base_small)

    def draw(self):
        """Draw the complete UI."""
        # Ensure responsive sizes before drawing
        self._update_layout()
        # Draw in layers (back to front)
        if self.show_stats:
            self._draw_player_stats_panel()
        
        if self.show_quickbar:
            self._draw_quickbar()
        
        if self.show_minimap:
            self._draw_minimap()
        
        if self.show_equipment:
            self._draw_equipment_panel()
        
        self._draw_floor_info()
        self._draw_experience_bar()
        self._draw_damage_numbers()
        self._draw_notifications()
        
        if self.current_dialog:
            self._draw_dialog_box()
    
    def _draw_frame(self, rect: pygame.Rect, style: str = 'modern'):
        """Draw a modern translucent panel with rounded corners."""
        # Create translucent surface for nice blending
        panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        # Background with 78% opacity
        bg = (*self.COLORS['bg_panel'], 200)
        pygame.draw.rect(panel_surf, bg, panel_surf.get_rect(), border_radius=int(8 * self.scale))
        # Subtle border
        border_col = (*self.COLORS['frame_border'], 220)
        pygame.draw.rect(panel_surf, border_col, panel_surf.get_rect(), width=2, border_radius=int(8 * self.scale))
        # Soft inner highlight
        hi_rect = panel_surf.get_rect().inflate(-8, -8)
        hi = (*self.COLORS['frame_light'], 90)
        pygame.draw.rect(panel_surf, hi, hi_rect, width=1, border_radius=int(6 * self.scale))
        self.screen.blit(panel_surf, rect)
    
    def _draw_bar(self, x: int, y: int, width: int, current: float, maximum: float, 
                  color: Tuple[int, int, int], label: str = ""):
        """Draw a 16-bit style stat bar."""
        # Background (empty part of bar)
        bg_rect = pygame.Rect(x, y, width, self.bar_height)
        pygame.draw.rect(self.screen, self.COLORS['frame_dark'], bg_rect)
        
        # Fill amount
        if maximum > 0:
            fill_width = int((current / maximum) * width)
            fill_rect = pygame.Rect(x, y, fill_width, self.bar_height)
            pygame.draw.rect(self.screen, color, fill_rect)
        
        # Border
        pygame.draw.rect(self.screen, self.COLORS['frame_border'], bg_rect, 1)
        
        # Inner highlight (16-bit effect)
        if current > 0:
            highlight_rect = pygame.Rect(x + 1, y + 1, max(0, int((current / maximum) * width) - 2), 2)
            highlight_color = tuple(min(255, c + 40) for c in color)
            pygame.draw.rect(self.screen, highlight_color, highlight_rect)
        
        # Text overlay
        text = f"{int(current)}/{int(maximum)}"
        text_surface = self.font_small.render(text, True, self.COLORS['text_white'])
        text_rect = text_surface.get_rect(center=(x + width // 2, y + self.bar_height // 2))
        
        # Text shadow for readability
        shadow_surface = self.font_small.render(text, True, BLACK)
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)
        
        # Label above bar
        if label:
            label_surface = self.font_small.render(label, True, self.COLORS['text_gray'])
            self.screen.blit(label_surface, (x, y - 14))
    
    def _draw_player_stats_panel(self):
        """Draw main player stats panel (top-left)."""
        panel_width = int(260 * self.scale)
        panel_height = int(130 * self.scale)
        panel_x = self.ui_margin
        panel_y = self.ui_margin
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self._draw_frame(panel_rect)
        
        # Content area
        content_x = panel_x + self.ui_padding + int(6 * self.scale)
        content_y = panel_y + self.ui_padding + int(6 * self.scale)
        bar_width = panel_width - (self.ui_padding * 2) - int(12 * self.scale)
        
        # Player name/level
        name_text = f"{self.player.name} - Lv.{getattr(self.player, 'level', 1)}"
        name_surface = self.font_medium.render(name_text, True, self.COLORS['text_yellow'])
        self.screen.blit(name_surface, (content_x, content_y))
        
        # Health bar
        self._draw_bar(content_x, content_y + int(26 * self.scale), bar_width, 
                      self.player.health, self.player.max_health, 
                      self.COLORS['health_full'], "HP")
        
        # Mana bar (placeholder - add mana to player later)
        max_mana = getattr(self.player, 'max_mana', 100)
        current_mana = getattr(self.player, 'mana', max_mana)
        self._draw_bar(content_x, content_y + int(54 * self.scale), bar_width, 
                      current_mana, max_mana, 
                      self.COLORS['mana_full'], "MP")
        
        # Stamina bar (for sprint)
        max_stamina = getattr(self.player, 'max_stamina', 100)
        current_stamina = getattr(self.player, 'stamina', max_stamina)
        self._draw_bar(content_x, content_y + int(82 * self.scale), bar_width, 
                      current_stamina, max_stamina, 
                      self.COLORS['stamina_full'], "ST")
    
    def _draw_quickbar(self):
        """Draw quick inventory slots (bottom-center)."""
        num_slots = 8
        slot_spacing = int(6 * self.scale)
        total_width = (self.slot_size * num_slots) + (slot_spacing * (num_slots - 1))
        start_x = (self.width - total_width) // 2
        start_y = self.height - self.slot_size - self.ui_margin - int(10 * self.scale)
        
        # Background panel
        panel_rect = pygame.Rect(start_x - int(10 * self.scale), start_y - int(10 * self.scale), 
                                 total_width + int(20 * self.scale), self.slot_size + int(20 * self.scale))
        self._draw_frame(panel_rect)
        
        # Draw slots
        for i in range(num_slots):
            slot_x = start_x + (i * (self.slot_size + slot_spacing))
            slot_rect = pygame.Rect(slot_x, start_y, self.slot_size, self.slot_size)
            
            # Slot background
            pygame.draw.rect(self.screen, self.COLORS['frame_dark'], slot_rect)
            pygame.draw.rect(self.screen, self.COLORS['frame_border'], slot_rect, 1)
            
            # Slot number
            num_surface = self.font_small.render(str(i + 1), True, self.COLORS['text_gray'])
            self.screen.blit(num_surface, (slot_x + int(3 * self.scale), start_y + int(3 * self.scale)))
            
            # Item placeholder (if player has items in inventory)
            if hasattr(self.player, 'inventory') and i < len(self.player.inventory):
                item = self.player.inventory[i]
                # Draw colored box representing item rarity
                item_color = self._get_item_color(item)
                item_box = pygame.Rect(slot_x + int(10 * self.scale), start_y + int(12 * self.scale), int(16 * self.scale), int(16 * self.scale))
                pygame.draw.rect(self.screen, item_color, item_box)
                pygame.draw.rect(self.screen, WHITE, item_box, 1)
    
    def _draw_minimap(self):
        """Draw minimap (top-right corner)."""
        map_size = int(180 * self.scale)
        map_x = self.width - map_size - self.ui_margin
        map_y = self.ui_margin
        
        map_rect = pygame.Rect(map_x, map_y, map_size, map_size)
        self._draw_frame(map_rect)
        
        # Map content area
        content_x = map_x + int(10 * self.scale)
        content_y = map_y + int(10 * self.scale)
        content_size = map_size - int(20 * self.scale)
        
        # Map background
        map_bg = pygame.Rect(content_x, content_y, content_size, content_size)
        pygame.draw.rect(self.screen, self.COLORS['bg_dark'], map_bg)
        
        # Grid overlay (16-bit style)
        grid_color = (40, 40, 48)
        grid_spacing = content_size // 8
        for i in range(1, 8):
            # Vertical lines
            pygame.draw.line(self.screen, grid_color,
                           (content_x + i * grid_spacing, content_y),
                           (content_x + i * grid_spacing, content_y + content_size), 1)
            # Horizontal lines
            pygame.draw.line(self.screen, grid_color,
                           (content_x, content_y + i * grid_spacing),
                           (content_x + content_size, content_y + i * grid_spacing), 1)
        
        # Player position (center)
        player_x = content_x + content_size // 2
        player_y = content_y + content_size // 2
        pygame.draw.circle(self.screen, self.COLORS['text_green'], (player_x, player_y), 3)
        pygame.draw.circle(self.screen, WHITE, (player_x, player_y), 3, 1)
        
        # Label
        label = self.font_small.render("MAP", True, self.COLORS['text_gray'])
        self.screen.blit(label, (map_x + int(6 * self.scale), map_y + map_size - int(18 * self.scale)))
    
    def _draw_equipment_panel(self):
        """Draw equipment slots panel (right side)."""
        panel_width = int(200 * self.scale)
        panel_height = int(360 * self.scale)
        panel_x = self.width - panel_width - self.ui_margin
        panel_y = int(160 * self.scale)  # Below minimap
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self._draw_frame(panel_rect)
        
        # Equipment slots
        slots = [
            ("Weapon", 0),
            ("Helmet", 1),
            ("Chest", 2),
            ("Gloves", 3),
            ("Boots", 4),
            ("Ring", 5),
        ]
        
        content_x = panel_x + int(14 * self.scale)
        content_y = panel_y + int(28 * self.scale)
        
        # Title
        title = self.font_medium.render("Equipment", True, self.COLORS['text_yellow'])
        self.screen.blit(title, (panel_x + 8, panel_y + 4))
        
        for idx, (slot_name, slot_idx) in enumerate(slots):
            slot_y = content_y + int(idx * 48 * self.scale)
            
            # Slot box
            slot_rect = pygame.Rect(content_x, slot_y, self.slot_size, self.slot_size)
            pygame.draw.rect(self.screen, self.COLORS['frame_dark'], slot_rect)
            pygame.draw.rect(self.screen, self.COLORS['frame_border'], slot_rect, 1)
            
            # Slot label
            label = self.font_small.render(slot_name, True, self.COLORS['text_gray'])
            self.screen.blit(label, (content_x + self.slot_size + 8, slot_y + 8))
            
            # Equipped item placeholder (colored box)
            # This would check player.equipment[slot_idx] in real implementation
            if hasattr(self.player, 'equipment') and slot_idx < len(self.player.equipment):
                item_box = pygame.Rect(content_x + int(8 * self.scale), slot_y + int(8 * self.scale), int(16 * self.scale), int(16 * self.scale))
                pygame.draw.rect(self.screen, self.COLORS['uncommon'], item_box)
                pygame.draw.rect(self.screen, WHITE, item_box, 1)
    
    def _draw_floor_info(self):
        """Draw current floor information (top-center)."""
        floor_text = f"Floor {self.current_floor}: {self.floor_name}"
        text_surface = self.font_medium.render(floor_text, True, self.COLORS['text_yellow'])
        text_rect = text_surface.get_rect(centerx=self.width // 2, top=self.ui_margin + 4)
        
        # Background panel
        bg_width = text_surface.get_width() + 24
        bg_rect = pygame.Rect(text_rect.centerx - bg_width // 2, self.ui_margin, 
                             bg_width, 28)
        self._draw_frame(bg_rect)
        
        # Text
        self.screen.blit(text_surface, text_rect)
    
    def _draw_experience_bar(self):
        """Draw experience bar (bottom of screen)."""
        bar_width = self.width - (self.ui_margin * 2)
        bar_x = self.ui_margin
        bar_y = self.height - self.ui_margin - int(6 * self.scale)
        
        # Get player exp (or use placeholder)
        current_exp = getattr(self.player, 'exp', 50)
        max_exp = getattr(self.player, 'max_exp', 100)
        
        # Thin experience bar
        exp_height = max(4, int(6 * self.scale))
        bg_rect = pygame.Rect(bar_x, bar_y, bar_width, exp_height)
        pygame.draw.rect(self.screen, self.COLORS['frame_dark'], bg_rect)
        
        # Fill
        if max_exp > 0:
            fill_width = int((current_exp / max_exp) * bar_width)
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, exp_height)
            pygame.draw.rect(self.screen, self.COLORS['exp_full'], fill_rect)
        
        # Border
        pygame.draw.rect(self.screen, self.COLORS['frame_border'], bg_rect, 1)
    
    def _draw_damage_numbers(self):
        """Draw floating damage numbers (16-bit style)."""
        for dmg_num in self.damage_numbers[:]:
            # Update position (float upward)
            dmg_num['y'] -= 1
            dmg_num['life'] -= 1
            
            # Remove if expired
            if dmg_num['life'] <= 0:
                self.damage_numbers.remove(dmg_num)
                continue
            
            # Fade out
            alpha = int(255 * (dmg_num['life'] / 60))
            
            # Draw with pixel-perfect positioning
            text = str(int(dmg_num['damage']))
            color = dmg_num['color']
            
            # Make damage text larger and bold-looking
            text_surface = self.font_large.render(text, True, color)
            
            # Shadow for depth
            shadow_surface = self.font_large.render(text, True, BLACK)
            self.screen.blit(shadow_surface, (dmg_num['x'] + 1, dmg_num['y'] + 1))
            self.screen.blit(text_surface, (dmg_num['x'], dmg_num['y']))
    
    def _draw_notifications(self):
        """Draw notification messages (right side, below equipment)."""
        if not self.notifications:
            return
        
        notif_x = self.width - 260
        notif_y = self.height - 120
        
        for idx, notif in enumerate(self.notifications[-3:]):  # Show last 3
            text = notif['text']
            life = notif['life']
            
            # Fade out
            alpha = int(255 * (life / 180))
            color = notif.get('color', self.COLORS['text_white'])
            
            # Background
            text_surface = self.font_small.render(text, True, color)
            bg_width = text_surface.get_width() + 16
            bg_rect = pygame.Rect(notif_x, notif_y - (idx * 24), bg_width, 20)
            
            # Semi-transparent background
            bg_surface = pygame.Surface((bg_width, 20))
            bg_surface.fill(self.COLORS['bg_panel'])
            bg_surface.set_alpha(min(200, alpha))
            self.screen.blit(bg_surface, bg_rect)
            
            # Border
            pygame.draw.rect(self.screen, self.COLORS['frame_border'], bg_rect, 1)
            
            # Text
            self.screen.blit(text_surface, (notif_x + 8, notif_y - (idx * 24) + 4))
            
            # Update life
            notif['life'] -= 1
            if notif['life'] <= 0:
                self.notifications.remove(notif)
    
    def _draw_dialog_box(self):
        """Draw dialog/message box (center screen, 16-bit RPG style)."""
        if not self.current_dialog:
            return
        
        # Dialog box dimensions
        box_width = self.width - 80
        box_height = 120
        box_x = (self.width - box_width) // 2
        box_y = self.height - box_height - 40
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        self._draw_frame(box_rect)
        
        # Dialog text
        text = self.current_dialog.get('text', '')
        speaker = self.current_dialog.get('speaker', None)
        
        content_x = box_x + 16
        content_y = box_y + 16
        
        # Speaker name (if any)
        if speaker:
            speaker_surface = self.font_medium.render(speaker, True, self.COLORS['text_yellow'])
            self.screen.blit(speaker_surface, (content_x, content_y))
            content_y += 24
        
        # Dialog text (word wrap)
        self._draw_wrapped_text(text, content_x, content_y, box_width - 32, 
                               self.font_small, self.COLORS['text_white'])
        
        # Continue indicator (blinking arrow)
        arrow = "▼"
        arrow_surface = self.font_medium.render(arrow, True, self.COLORS['text_yellow'])
        arrow_x = box_x + box_width - 24
        arrow_y = box_y + box_height - 24
        self.screen.blit(arrow_surface, (arrow_x, arrow_y))
    
    def _draw_wrapped_text(self, text: str, x: int, y: int, max_width: int, 
                          font: pygame.font.Font, color: Tuple[int, int, int]):
        """Draw text with word wrapping."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        for idx, line in enumerate(lines):
            line_surface = font.render(line, True, color)
            self.screen.blit(line_surface, (x, y + (idx * 18)))
    
    def _get_item_color(self, item) -> Tuple[int, int, int]:
        """Get color for item based on rarity."""
        if hasattr(item, 'rarity'):
            # Get rarity name safely
            if hasattr(item.rarity, 'value'):
                rarity_name = item.rarity.value
            elif hasattr(item.rarity, 'name'):
                rarity_name = item.rarity.name
            else:
                rarity_name = str(item.rarity)
            
            # Ensure it's a string and lowercase it
            if isinstance(rarity_name, str):
                return self.COLORS.get(rarity_name.lower(), self.COLORS['common'])
        
        return self.COLORS['common']
    
    # Public methods for updating UI
    
    def add_damage_number(self, damage: float, x: float, y: float, 
                         color: Tuple[int, int, int] = None):
        """Add a damage number to display."""
        if color is None:
            color = self.COLORS['text_red']
        
        self.damage_numbers.append({
            'damage': damage,
            'x': x,
            'y': y,
            'color': color,
            'life': 60  # frames
        })
    
    def add_notification(self, text: str, color: Tuple[int, int, int] = None):
        """Add a notification message."""
        if color is None:
            color = self.COLORS['text_white']
        
        self.notifications.append({
            'text': text,
            'color': color,
            'life': 180  # frames (3 seconds at 60 FPS)
        })
    
    def show_dialog(self, text: str, speaker: str = None):
        """Show a dialog box."""
        self.current_dialog = {
            'text': text,
            'speaker': speaker
        }
    
    def hide_dialog(self):
        """Hide the dialog box."""
        self.current_dialog = None
    
    def set_floor(self, floor_number: int, floor_name: str = None):
        """Update floor information."""
        self.current_floor = floor_number
        if floor_name:
            self.floor_name = floor_name
        else:
            self.floor_name = f"Tower Level {floor_number}"
    
    def toggle_equipment(self):
        """Toggle equipment panel visibility."""
        self.show_equipment = not self.show_equipment
    
    def update(self, dt: float = 1.0):
        """Update UI animations and states."""
        # Update any animated elements
        pass

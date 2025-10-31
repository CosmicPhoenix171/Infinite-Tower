"""
Infinite Tower Engine - Scene Management System

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
"""

import pygame
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, RED


class Scene(ABC):
    """
    Abstract base class for all game scenes.
    
    Scenes represent different game states like menu, gameplay, pause, etc.
    Each scene handles its own events, updates, and rendering.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = False
        self.manager = None  # Reference to SceneManager
        self.transition_to = None  # Scene to transition to
    
    def activate(self):
        """Activate this scene."""
        self.is_active = True
        self.on_enter()
    
    def deactivate(self):
        """Deactivate this scene."""
        self.is_active = False
        self.on_exit()
    
    @abstractmethod
    def on_enter(self):
        """Called when scene becomes active."""
        pass
    
    @abstractmethod
    def on_exit(self):
        """Called when scene becomes inactive."""
        pass
    
    @abstractmethod
    def handle_events(self, events: list):
        """
        Handle pygame events.
        
        Args:
            events: List of pygame events
        """
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """
        Update scene logic.
        
        Args:
            dt: Delta time
        """
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface):
        """
        Render scene.
        
        Args:
            surface: Pygame surface to draw on
        """
        pass
    
    def request_transition(self, scene_name: str):
        """
        Request transition to another scene.
        
        Args:
            scene_name: Name of scene to transition to
        """
        self.transition_to = scene_name


class MenuScene(Scene):
    """Main menu scene."""
    
    def __init__(self):
        super().__init__("menu")
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.selected_option = 0
        self.menu_options = ["Start Game", "Settings", "Quit"]
    
    def on_enter(self):
        """Initialize menu."""
        self.selected_option = 0
    
    def on_exit(self):
        """Clean up menu."""
        pass
    
    def handle_events(self, events: list):
        """Handle menu input."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._select_option()
    
    def _select_option(self):
        """Handle menu option selection."""
        option = self.menu_options[self.selected_option]
        
        if option == "Start Game":
            self.request_transition("game")
        elif option == "Settings":
            self.request_transition("settings")
        elif option == "Quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def update(self, dt: float):
        """Update menu (animations, etc)."""
        pass
    
    def draw(self, surface: pygame.Surface):
        """Render menu."""
        surface.fill(BLACK)
        
        # Title
        title = self.font_large.render("INFINITE TOWER", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font_small.render("Engine v0.1.0", True, (150, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 210))
        surface.blit(subtitle, subtitle_rect)
        
        # Menu options
        start_y = 300
        spacing = 60
        
        for i, option in enumerate(self.menu_options):
            color = GREEN if i == self.selected_option else WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
            
            # Highlight selected option
            if i == self.selected_option:
                highlight_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(surface, color, highlight_rect, 2)
            
            surface.blit(text, text_rect)
        
        # Instructions
        instr = self.font_small.render("Use Arrow Keys and ENTER", True, (100, 100, 100))
        instr_rect = instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        surface.blit(instr, instr_rect)


class GameScene(Scene):
    """Main gameplay scene."""
    
    def __init__(self, game_instance):
        super().__init__("game")
        self.game = game_instance
        self.paused = False
    
    def on_enter(self):
        """Start gameplay."""
        # Initialize game elements here
        pass
    
    def on_exit(self):
        """Clean up gameplay."""
        pass
    
    def handle_events(self, events: list):
        """Handle gameplay input."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.request_transition("pause")
    
    def update(self, dt: float):
        """Update gameplay."""
        if not self.paused:
            # Update game logic
            pass
    
    def draw(self, surface: pygame.Surface):
        """Render gameplay."""
        # Game rendering happens here
        surface.fill((20, 30, 50))


class PauseScene(Scene):
    """Pause menu scene."""
    
    def __init__(self):
        super().__init__("pause")
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.selected_option = 0
        self.menu_options = ["Resume", "Settings", "Main Menu"]
        self.background_surface = None
    
    def on_enter(self):
        """Capture game screen for background."""
        self.selected_option = 0
    
    def on_exit(self):
        """Resume game."""
        self.background_surface = None
    
    def handle_events(self, events: list):
        """Handle pause menu input."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.request_transition("game")
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._select_option()
    
    def _select_option(self):
        """Handle pause menu option selection."""
        option = self.menu_options[self.selected_option]
        
        if option == "Resume":
            self.request_transition("game")
        elif option == "Settings":
            self.request_transition("settings")
        elif option == "Main Menu":
            self.request_transition("menu")
    
    def update(self, dt: float):
        """Update pause menu."""
        pass
    
    def draw(self, surface: pygame.Surface):
        """Render pause menu."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("PAUSED", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title, title_rect)
        
        # Menu options
        start_y = 300
        spacing = 60
        
        for i, option in enumerate(self.menu_options):
            color = GREEN if i == self.selected_option else WHITE
            text = self.font_medium.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
            
            if i == self.selected_option:
                highlight_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(surface, color, highlight_rect, 2)
            
            surface.blit(text, text_rect)


class SettingsScene(Scene):
    """Settings menu scene."""
    
    def __init__(self):
        super().__init__("settings")
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 42)
        self.font_small = pygame.font.Font(None, 32)
    
    def on_enter(self):
        """Initialize settings."""
        pass
    
    def on_exit(self):
        """Save settings."""
        pass
    
    def handle_events(self, events: list):
        """Handle settings input."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.request_transition("menu")
    
    def update(self, dt: float):
        """Update settings."""
        pass
    
    def draw(self, surface: pygame.Surface):
        """Render settings."""
        surface.fill(BLACK)
        
        title = self.font_large.render("SETTINGS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)
        
        # Placeholder text
        text = self.font_medium.render("Settings Coming Soon...", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(text, text_rect)
        
        # Instructions
        instr = self.font_small.render("Press ESC to go back", True, (100, 100, 100))
        instr_rect = instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        surface.blit(instr, instr_rect)


class SceneManager:
    """
    Manages scene transitions and updates.
    
    Handles scene stack for overlay scenes (like pause over game).
    """
    
    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        self.scene_stack = []  # Stack for overlay scenes
    
    def add_scene(self, scene: Scene):
        """
        Add a scene to the manager.
        
        Args:
            scene: Scene instance to add
        """
        scene.manager = self
        self.scenes[scene.name] = scene
    
    def switch_to(self, scene_name: str):
        """
        Switch to a different scene.
        
        Args:
            scene_name: Name of scene to switch to
        """
        # Deactivate current scene
        if self.active_scene:
            self.active_scene.deactivate()
        
        # Activate new scene
        self.active_scene = self.scenes.get(scene_name)
        if self.active_scene:
            self.active_scene.activate()
            self.active_scene.transition_to = None
    
    def push_scene(self, scene_name: str):
        """
        Push a scene onto the stack (for overlays).
        
        Args:
            scene_name: Name of scene to push
        """
        if self.active_scene:
            self.scene_stack.append(self.active_scene)
            self.active_scene.is_active = False
        
        self.active_scene = self.scenes.get(scene_name)
        if self.active_scene:
            self.active_scene.activate()
    
    def pop_scene(self):
        """Pop the top scene from the stack."""
        if self.active_scene:
            self.active_scene.deactivate()
        
        if self.scene_stack:
            self.active_scene = self.scene_stack.pop()
            self.active_scene.is_active = True
        else:
            self.active_scene = None
    
    def handle_events(self, events: list):
        """
        Handle events for active scene.
        
        Args:
            events: List of pygame events
        """
        if self.active_scene:
            self.active_scene.handle_events(events)
    
    def update(self, dt: float):
        """
        Update active scene.
        
        Args:
            dt: Delta time
        """
        if self.active_scene:
            self.active_scene.update(dt)
            
            # Check for scene transition request
            if self.active_scene.transition_to:
                self.switch_to(self.active_scene.transition_to)
    
    def draw(self, surface: pygame.Surface):
        """
        Render active scene.
        
        Args:
            surface: Pygame surface to draw on
        """
        if self.active_scene:
            self.active_scene.draw(surface)
    
    def get_active_scene(self) -> Optional[Scene]:
        """Get the currently active scene."""
        return self.active_scene
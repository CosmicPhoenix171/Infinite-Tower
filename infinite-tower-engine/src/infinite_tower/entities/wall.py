"""
Infinite Tower Engine - Wall Entity

Static solid obstacles with rectangular hitboxes.
"""
import pygame
from typing import Tuple

from ..config import GRAY, WHITE


class Wall:
    def __init__(self, x: int, y: int, width: int, height: int,
                 color: Tuple[int, int, int] = (90, 80, 70)):
        # Top-left world-space coordinates
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.color = color
        self.border_color = (140, 130, 120)

    def draw(self, surface: pygame.Surface, rect_override: pygame.Rect | None = None):
        r = rect_override if rect_override is not None else self.rect
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, self.border_color, r, 2)

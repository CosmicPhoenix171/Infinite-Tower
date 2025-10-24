import pygame
import os

class ResourceLoader:
    def __init__(self):
        self.sprites = {}
        self.sounds = {}
        self.fonts = {}

    def load_sprite(self, name, path):
        full_path = os.path.join('assets', 'sprites', path)
        self.sprites[name] = pygame.image.load(full_path).convert_alpha()

    def load_sound(self, name, path):
        full_path = os.path.join('assets', 'sounds', path)
        self.sounds[name] = pygame.mixer.Sound(full_path)

    def load_font(self, name, path, size):
        full_path = os.path.join('assets', 'fonts', path)
        self.fonts[name] = pygame.font.Font(full_path, size)

    def get_sprite(self, name):
        return self.sprites.get(name)

    def get_sound(self, name):
        return self.sounds.get(name)

    def get_font(self, name):
        return self.fonts.get(name)
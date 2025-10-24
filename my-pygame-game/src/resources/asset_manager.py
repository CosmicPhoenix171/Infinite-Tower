class AssetManager:
    def __init__(self):
        self.assets = {}

    def load_image(self, name, path):
        import pygame
        image = pygame.image.load(path)
        self.assets[name] = image
        return image

    def get_image(self, name):
        return self.assets.get(name)

    def load_sound(self, name, path):
        import pygame
        sound = pygame.mixer.Sound(path)
        self.assets[name] = sound
        return sound

    def get_sound(self, name):
        return self.assets.get(name)

    def clear_assets(self):
        self.assets.clear()
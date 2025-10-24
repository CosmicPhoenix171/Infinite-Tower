import pygame


class HUD:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        self.draw_health()
        self.draw_experience()
        self.draw_loot()

    def draw_health(self):
        health_text = f"Health: {self.player.health}"
        health_surface = self.font.render(health_text, True, (255, 0, 0))
        self.screen.blit(health_surface, (10, 10))

    def draw_experience(self):
        experience_text = f"XP: {self.player.experience}"
        experience_surface = self.font.render(experience_text, True, (0, 255, 0))
        self.screen.blit(experience_surface, (10, 50))

    def draw_loot(self):
        loot_text = f"Loot: {self.player.loot_count}"
        loot_surface = self.font.render(loot_text, True, (0, 0, 255))
        self.screen.blit(loot_surface, (10, 90))
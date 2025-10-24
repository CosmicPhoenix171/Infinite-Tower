import pygame
import sys

class GameLoop:
    def __init__(self, game):
        self.game = game
        self.clock = pygame.time.Clock()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.game.config.FRAME_RATE)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

    def update(self):
        self.game.update()

    def render(self):
        self.game.render()
        pygame.display.flip()

    def quit_game(self):
        pygame.quit()
        sys.exit()
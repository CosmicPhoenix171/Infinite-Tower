class Game:
    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("My Pygame Game")

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        pass  # Update game logic here

    def render(self):
        self.screen.fill((0, 0, 0))  # Clear the screen with black
        pygame.display.flip()  # Update the display

    def cleanup(self):
        pygame.quit()
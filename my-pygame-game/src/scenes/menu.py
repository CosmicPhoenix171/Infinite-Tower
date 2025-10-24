class MenuScene:
    def __init__(self, game):
        self.game = game
        self.font = None  # Placeholder for font
        self.options = ["Start Game", "Options", "Quit"]
        self.selected_option = 0

    def handle_events(self):
        for event in self.game.events:
            if event.type == self.game.PYGAME.KEYDOWN:
                if event.key == self.game.PYGAME.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == self.game.PYGAME.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == self.game.PYGAME.K_RETURN:
                    self.select_option()

    def select_option(self):
        if self.selected_option == 0:
            self.game.start_game()
        elif self.selected_option == 1:
            self.game.show_options()
        elif self.selected_option == 2:
            self.game.quit()

    def update(self):
        pass  # Update logic for the menu can be added here

    def draw(self, surface):
        surface.fill((0, 0, 0))  # Clear the screen with black
        for index, option in enumerate(self.options):
            color = (255, 255, 255) if index == self.selected_option else (100, 100, 100)
            text_surface = self.font.render(option, True, color)
            surface.blit(text_surface, (100, 100 + index * 30))  # Position the options vertically
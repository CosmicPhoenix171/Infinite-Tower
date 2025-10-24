import pygame
from game import Game

def main():
    pygame.init()
    
    # Create an instance of the Game class
    game = Game()
    
    # Start the game loop
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()
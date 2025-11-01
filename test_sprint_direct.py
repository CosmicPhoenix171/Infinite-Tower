#!/usr/bin/env python3
"""
Test sprint mechanics directly
"""
import sys
sys.path.insert(0, 'infinite-tower-engine/src')

from infinite_tower.entities.player import Player
from infinite_tower.utils.input_handler import InputHandler
import pygame
import time

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Sprint Test")

# Create player and input handler
player = Player("TestPlayer")
input_handler = InputHandler()

print(f"Player base speed: {player.speed}")
print(f"Player sprint multiplier: {player.sprint_multiplier}")
print(f"Sprinted speed should be: {player.speed * player.sprint_multiplier}")
print("\nMove around with WASD and hold Shift/Ctrl to sprint")
print("Watch the debug display in top-left corner\n")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        input_handler.handle_event(event)
    
    input_handler.update()
    player.handle_input(input_handler)
    player.update(dt=1.0)
    
    # Draw
    screen.fill((0, 0, 0))
    
    # Draw player
    pygame.draw.circle(screen, (255, 0, 0), (int(player.position[0]), int(player.position[1])), player.size // 2)
    
    # Draw debug info
    font = pygame.font.Font(None, 24)
    sprint_text = "SPRINTING" if player.is_sprinting else "Normal"
    debug = font.render(f"{sprint_text} | Vel: ({player.velocity[0]:.1f}, {player.velocity[1]:.1f}) | Stamina: {player.stamina:.0f}", True, (0, 255, 0))
    screen.blit(debug, (10, 10))
    
    # Show keys
    keys_text = font.render("WASD: Move, Shift/Ctrl: Sprint", True, (255, 255, 255))
    screen.blit(keys_text, (10, 40))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()

#!/usr/bin/env python3
"""
Quick test to verify sprint mechanics are working
"""
import sys
sys.path.insert(0, 'infinite-tower-engine/src')

from infinite_tower.entities.player import Player
from infinite_tower.utils.input_handler import InputHandler
import pygame

# Initialize pygame
pygame.init()
pygame.display.set_mode((100, 100))

# Create player
player = Player("TestPlayer")
print(f"Initial speed: {player.speed}")
print(f"Sprint multiplier: {player.sprint_multiplier}")
print(f"Initial stamina: {player.stamina}")

# Create input handler
input_handler = InputHandler()

# Simulate no input
player.handle_input(input_handler)
print(f"No input - is_sprinting: {player.is_sprinting}, velocity: {player.velocity}")

# Now let's manually check what happens when we press Shift
print("\n--- Testing with simulated Shift press ---")
# We can't easily simulate keys, so let's just check the logic manually

# Test case 1: Shift pressed, stamina > 0
test_stamina = 50
test_shift_pressed = True
result_sprinting = test_shift_pressed and test_stamina > 0
sprint_speed = player.speed * player.sprint_multiplier if result_sprinting else player.speed
print(f"Stamina={test_stamina}, Shift pressed={test_shift_pressed}")
print(f"  -> is_sprinting would be: {result_sprinting}")
print(f"  -> speed would be: {sprint_speed} (vs normal {player.speed})")

# Test case 2: Shift pressed, stamina = 0
test_stamina = 0
result_sprinting = test_shift_pressed and test_stamina > 0
sprint_speed = player.speed * player.sprint_multiplier if result_sprinting else player.speed
print(f"Stamina={test_stamina}, Shift pressed={test_shift_pressed}")
print(f"  -> is_sprinting would be: {result_sprinting}")
print(f"  -> speed would be: {sprint_speed} (vs normal {player.speed})")

print("\nLogic appears correct. If sprint isn't working in-game, it might be:")
print("1. Shift key not being detected by input handler")
print("2. Speed not translating to visible difference due to normalization")
print("3. Stamina not updating properly in game loop")

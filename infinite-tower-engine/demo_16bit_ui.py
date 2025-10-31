"""
Infinite Tower Engine - Full 16-bit UI Demo

Demonstrates the complete 16-bit style game UI with all features.
"""

import pygame
import sys
from src.infinite_tower.config import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE
from src.infinite_tower.entities.player import Player
from src.infinite_tower.entities.enemy import Enemy, EnemyType
from src.infinite_tower.ui.game_ui import GameUI
from src.infinite_tower.ui.inventory import InventoryUI
from src.infinite_tower.systems.combat import CombatSystem
from src.infinite_tower.systems.physics import Physics
from src.infinite_tower.utils.input_handler import InputHandler
from src.infinite_tower.items.loot import LootGenerator


def main():
    # Initialize Pygame
    pygame.init()
    # Start resizable; use SCALED for pixel-perfect scaling
    flags = pygame.SCALED | pygame.RESIZABLE
    screen = pygame.display.set_mode((1280, 720), flags)
    pygame.display.set_caption("Infinite Tower - 16-bit UI Demo")
    clock = pygame.time.Clock()
    
    print("="*60)
    print("INFINITE TOWER ENGINE - 16-BIT UI DEMO")
    print("="*60)
    
    # Initialize systems
    print("\n✓ Initializing systems...")
    input_handler = InputHandler()
    combat_system = CombatSystem()
    physics = Physics()
    loot_gen = LootGenerator(seed=12345)
    
    # Create player
    print("✓ Creating player...")
    player = Player("Hero", health=100, position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Add some attributes for UI display
    player.level = 5
    player.exp = 350
    player.max_exp = 500
    player.mana = 75
    player.max_mana = 100
    player.stamina = 100
    player.max_stamina = 100
    player.equipment = []  # Equipment slots
    
    # Add some starter loot to inventory
    print("✓ Generating starter loot...")
    for i in range(5):
        item = loot_gen.generate_random_item(floor_level=1)
        player.add_to_inventory(item)
        print(f"  Added: {item.name} ({item.rarity.value})")
    
    # Create some enemies
    print("✓ Spawning enemies...")
    enemies = [
        Enemy("Goblin", health=30, damage=5, speed=2, position=(200, 150), enemy_type=EnemyType.FAST),
        Enemy("Orc", health=80, damage=12, speed=1, position=(600, 200), enemy_type=EnemyType.TANK),
        Enemy("Skeleton", health=40, damage=8, speed=2.5, position=(400, 400), enemy_type=EnemyType.RANGER),
    ]
    
    for enemy in enemies:
        print(f"  {enemy}")
    
    # Create the full 16-bit UI
    print("✓ Initializing 16-bit UI system...")
    game_ui = GameUI(screen, player)
    game_ui.set_floor(1, "Entrance Hall")
    game_ui.show_equipment = True  # Show equipment panel
    
    # Welcome dialog
    game_ui.show_dialog(
        "Welcome to the Infinite Tower, brave adventurer! "
        "Press E to toggle equipment, Tab for inventory. "
        "Use WASD to move and Space to attack.",
        speaker="Tower Guide"
    )
    
    print("\n✓ All systems initialized!")
    print("\n" + "="*60)
    print("CONTROLS:")
    print("  WASD or Arrow Keys - Move player")
    print("  SHIFT - Sprint (2x speed)")
    print("  SPACE - Attack")
    print("  E - Toggle Equipment Panel")
    print("  TAB or I - Inventory")
    print("  ENTER - Dismiss Dialog")
    print("  ESC - Quit")
    print("="*60)
    print("\nStarting 16-bit UI demo...\n")
    
    # Test notifications
    game_ui.add_notification("Game Started!", game_ui.COLORS['text_green'])
    game_ui.add_notification("Welcome to Floor 1", game_ui.COLORS['text_yellow'])
    
    # Inventory UI overlay
    inventory_ui = InventoryUI(screen, player)
    
    # Main game loop
    running = True
    frame_count = 0
    
    while running:
        dt = clock.tick(FRAME_RATE) / 1000.0
        frame_count += 1
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            # Let inventory overlay consume events first when visible
            if inventory_ui.handle_input(event):
                continue
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    # Toggle fullscreen
                    try:
                        pygame.display.toggle_fullscreen()
                    except Exception:
                        pass
                elif event.key == pygame.K_e:
                    game_ui.toggle_equipment()
                elif event.key == pygame.K_TAB or event.key == pygame.K_i:
                    inventory_ui.toggle()
                elif event.key == pygame.K_RETURN:
                    game_ui.hide_dialog()
                elif event.key == pygame.K_t:
                    # Test dialog
                    game_ui.show_dialog(
                        "You found a mysterious chest! It contains ancient treasures.",
                        speaker="Narrator"
                    )
                elif event.key == pygame.K_n:
                    # Test notification
                    game_ui.add_notification("Test Notification", game_ui.COLORS['text_yellow'])
            elif event.type == pygame.VIDEORESIZE:
                # Recreate surface with new size (SCALED keeps aspect)
                screen = pygame.display.set_mode((event.w, event.h), flags)
                # Update UI surfaces holding references
                game_ui.screen = screen
                inventory_ui.screen = screen
        
        # Update input handler
        input_handler.update(events)
        
        # Update player (freeze movement input when inventory open)
        if not inventory_ui.is_visible:
            player.handle_input(input_handler)
        player.update(dt)
        
        # Drain stamina when sprinting
        if player.is_sprinting and player.is_moving:
            player.stamina = max(0, player.stamina - 0.5)
        else:
            player.stamina = min(player.max_stamina, player.stamina + 0.3)
        
        # Update enemies
        for enemy in enemies[:]:
            if enemy.is_alive():
                enemy.update(player, dt)
            else:
                if enemy in enemies:
                    enemies.remove(enemy)
                    game_ui.add_notification(f"Defeated {enemy.name}!", game_ui.COLORS['text_green'])
                    # Add exp
                    player.exp += 50
                    if player.exp >= player.max_exp:
                        player.level += 1
                        player.exp = 0
                        game_ui.add_notification(f"Level Up! Now Level {player.level}", 
                                               game_ui.COLORS['text_yellow'])
        
        # Combat - player attacks
        if player.is_attacking:
            attack_rect = player.get_attack_rect()
            for enemy in enemies:
                if physics.check_collision(attack_rect, enemy.rect):
                    result = combat_system.perform_attack(player, enemy)
                    game_ui.add_damage_number(result.damage, enemy.position[0], 
                                            enemy.position[1] - 20, game_ui.COLORS['text_red'])
                    if result.was_critical:
                        game_ui.add_notification("Critical Hit!", game_ui.COLORS['text_yellow'])
        
        # Combat - enemy attacks
        for enemy in enemies:
            if enemy.is_attacking and physics.check_collision(enemy.get_attack_rect(), player.rect):
                result = combat_system.perform_attack(enemy, player)
                game_ui.add_damage_number(result.damage, player.position[0], 
                                        player.position[1] - 20, game_ui.COLORS['text_red'])
                if not player.is_alive():
                    game_ui.show_dialog("You have been defeated! The tower claims another soul...", 
                                      speaker="Game Over")
                    running = False
        
        # Test damage numbers periodically
        if frame_count % 120 == 0 and enemies:
            # Show test damage on random enemy
            enemy = enemies[0]
            test_dmg = 10
            game_ui.add_damage_number(test_dmg, enemy.position[0], enemy.position[1], 
                                    game_ui.COLORS['text_yellow'])
        
        # Update UI
        game_ui.update(dt)
        
        # Render
        # Background gradient (optimized for current size)
        sw, sh = screen.get_size()
        for y in range(sh):
            color_val = int(20 + (y / max(1, sh)) * 30)
            pygame.draw.line(screen, (color_val, color_val // 2, color_val // 3), (0, y), (sw, y))
        
        # Draw floor area (darker rectangle for playable area)
        sw, sh = screen.get_size()
        floor_rect = pygame.Rect(60, 60, sw - 120, sh - 140)
        pygame.draw.rect(screen, (40, 35, 30), floor_rect)
        pygame.draw.rect(screen, (80, 70, 60), floor_rect, 2)
        
        # Draw grid on floor (16-bit tile effect)
        grid_size = 32
        grid_color = (50, 45, 40)
        for x in range(floor_rect.left, floor_rect.right, grid_size):
            pygame.draw.line(screen, grid_color, (x, floor_rect.top), (x, floor_rect.bottom), 1)
        for y in range(floor_rect.top, floor_rect.bottom, grid_size):
            pygame.draw.line(screen, grid_color, (floor_rect.left, y), (floor_rect.right, y), 1)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw player
        player.draw(screen)
        
    # Draw the complete 16-bit UI (on top of everything)
    game_ui.draw()
    # Draw inventory overlay last
    inventory_ui.draw()
        
        # Update display
        pygame.display.flip()
    
    print("\n✓ Demo ended. Thank you for playing!")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

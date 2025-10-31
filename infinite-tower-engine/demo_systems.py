"""
Demo script to showcase the implemented game systems.

This script demonstrates:
- Player movement
- Enemy AI
- Combat system
- Floor generation
- Loot system
- HUD
"""

import pygame
import sys
sys.path.insert(0, 'src')

from infinite_tower.entities.player import Player
from infinite_tower.entities.enemy import Enemy, EnemyType
from infinite_tower.floors.generator import FloorGenerator
from infinite_tower.items.loot import LootGenerator, Rarity
from infinite_tower.systems.combat import CombatSystem
from infinite_tower.systems.physics import Physics
from infinite_tower.ui.hud import HUD
from infinite_tower.ui.inventory import InventoryUI
from infinite_tower.utils.input_handler import InputHandler
from infinite_tower.config import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, WHITE, BLACK


def main():
    """Run the systems demo."""
    print("=== Infinite Tower Engine Systems Demo ===\n")
    
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Infinite Tower - Systems Demo")
    clock = pygame.time.Clock()
    
    # Initialize systems
    print("✓ Initializing game systems...")
    input_handler = InputHandler()
    combat_system = CombatSystem()
    physics = Physics()
    
    # Create player
    player = Player("TestPlayer", health=100, position=(400, 300))
    print(f"✓ Player created: {player}")
    
    # Generate floor
    print("\n✓ Generating procedural floor...")
    floor_gen = FloorGenerator(seed="demo_seed")
    rooms = floor_gen.generate_floor(num_rooms=5, floor_level=1)
    print(f"  Generated {len(rooms)} rooms")
    for i, room in enumerate(rooms):
        print(f"    Room {i+1}: {room.width}x{room.height}, "
              f"Type: {room.room_type.value}, "
              f"Enemies: {len(room.enemies)}, Loot: {len(room.loot)}")
    
    # Spawn enemies from first room
    print("\n✓ Spawning enemies...")
    enemies = []
    if rooms:
        room_enemies = floor_gen.spawn_enemies(rooms[0])
        enemies.extend(room_enemies[:3])  # Only spawn first 3 for demo
        for enemy in enemies:
            print(f"  {enemy}")
    
    # Add some manually positioned enemies for visibility
    from infinite_tower.entities.enemy import Enemy, EnemyType
    manual_enemies = [
        Enemy("Goblin Scout", health=30, damage=5, speed=4, position=(300, 200), enemy_type=EnemyType.FAST),
        Enemy("Orc Warrior", health=80, damage=12, speed=1.5, position=(500, 250), enemy_type=EnemyType.TANK),
        Enemy("Skeleton Archer", health=40, damage=8, speed=2, position=(600, 350), enemy_type=EnemyType.RANGER),
    ]
    enemies.extend(manual_enemies)
    print(f"\n✓ Added {len(manual_enemies)} additional enemies for demo")
    for enemy in manual_enemies:
        print(f"  {enemy}")
    
    # Generate loot
    print("\n✓ Generating loot...")
    loot_gen = LootGenerator(seed=hash("demo"))
    loot_items = []
    for i in range(3):
        item = loot_gen.generate_random_item(floor_level=1)
        item.set_position(200 + i * 80, 450)
        loot_items.append(item)
        print(f"  {item}")
    
    # Create HUD and Inventory UI
    hud = HUD(screen, player)
    hud.set_floor(1)
    inventory_ui = InventoryUI(screen, player)
    
    print("\n✓ All systems initialized!")
    print("\n" + "="*50)
    print("CONTROLS:")
    print("  WASD or Arrow Keys - Move player")
    print("  SHIFT - Sprint (2x speed)")
    print("  SPACE - Attack")
    print("  TAB or I - Toggle inventory")
    print("  ESC - Quit")
    print("="*50)
    print("\nStarting demo...\n")
    
    # Main game loop
    running = True
    while running:
        dt = clock.tick(FRAME_RATE) / 1000.0  # Delta time in seconds
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            # Let inventory UI handle input first
            if not inventory_ui.handle_input(event):
                # Then HUD
                if not hud.handle_input(event):
                    # Finally input handler for game controls
                    input_handler.handle_event(event)
        
        # Update input
        input_handler.update()
        
        # Update player
        player.handle_input(input_handler)
        player.update(dt)
        
        # Update enemies (AI and movement)
        for enemy in enemies[:]:  # Copy list to allow removal
            if enemy.is_alive():
                enemy.update(player, dt)
            else:
                # Remove dead enemies
                if enemy in enemies:
                    enemies.remove(enemy)
                    print(f"Enemy defeated: {enemy.name}")
        
        # Check combat collisions
        if player.is_attacking:
            attack_rect = player.get_attack_rect()
            for enemy in enemies:
                if physics.check_collision(attack_rect, enemy.rect):
                    result = combat_system.perform_attack(player, enemy)
                    hud.add_damage_number(result.damage, enemy.position[0], enemy.position[1], (255, 100, 100))
                    if result.target_defeated:
                        print(f"{enemy.name} defeated! (Dealt {result.damage} damage)")
        
        # Enemy attacks
        for enemy in enemies:
            if enemy.is_attacking and physics.check_collision(enemy.get_attack_rect(), player.rect):
                result = combat_system.perform_attack(enemy, player)
                hud.add_damage_number(result.damage, player.position[0], player.position[1], (255, 50, 50))
                if not player.is_alive():
                    print("Player defeated! Game Over")
                    running = False
        
        # Check loot collection
        for item in loot_items[:]:
            if item.rect and physics.check_collision(player.rect, item.rect):
                player.add_to_inventory(item)
                loot_items.remove(item)
                hud.add_notification(f"Picked up {item.name}")
                print(f"Collected: {item}")
        
        # Update HUD
        hud.update(dt)
        
        # Render
        screen.fill((20, 30, 40))  # Dark blue background
        
        # Draw floor tile (placeholder)
        floor_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        pygame.draw.rect(screen, (60, 50, 40), floor_rect)
        pygame.draw.rect(screen, WHITE, floor_rect, 2)
        
        # Draw loot
        for item in loot_items:
            item.draw(screen)
        
        # Draw enemies
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw player
        player.draw(screen)
        
        # Draw HUD
        hud.draw()
        
        # Draw Inventory (on top of everything)
        inventory_ui.draw()
        
        # Draw FPS
        fps_text = pygame.font.Font(None, 24).render(f"FPS: {int(clock.get_fps())}", True, WHITE)
        screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
        
        pygame.display.flip()
    
    # Cleanup
    pygame.quit()
    print("\nDemo ended. Thank you!")
    print(f"\nFinal Stats:")
    print(f"  Player Health: {player.health}/{player.max_health}")
    print(f"  Items Collected: {len(player.inventory)}")
    print(f"  Enemies Remaining: {len(enemies)}")


if __name__ == "__main__":
    main()

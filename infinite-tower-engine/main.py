"""
Infinite Tower Engine - Web Demo (Pygbag compatible)

This is the web-compatible version using asyncio for browser execution.
"""

import asyncio
import pygame
import sys

# Import game modules
try:
    from src.infinite_tower.config import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE
    from src.infinite_tower.entities.player import Player
    from src.infinite_tower.entities.enemy import Enemy, EnemyType
    from src.infinite_tower.ui.game_ui import GameUI
    from src.infinite_tower.ui.inventory import InventoryUI
    from src.infinite_tower.systems.combat import CombatSystem
    from src.infinite_tower.systems.physics import Physics
    from src.infinite_tower.utils.input_handler import InputHandler
    from src.infinite_tower.items.loot import LootGenerator
except ImportError:
    # Fallback for web build path differences
    import sys
    sys.path.insert(0, 'infinite-tower-engine/src')
    from infinite_tower.config import SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE
    from infinite_tower.entities.player import Player
    from infinite_tower.entities.enemy import Enemy, EnemyType
    from infinite_tower.ui.game_ui import GameUI
    from infinite_tower.ui.inventory import InventoryUI
    from infinite_tower.systems.combat import CombatSystem
    from infinite_tower.systems.physics import Physics
    from infinite_tower.utils.input_handler import InputHandler
    from infinite_tower.items.loot import LootGenerator


class GameState:
    """Game state container for web version."""
    def __init__(self):
        self.running = True
        self.frame_count = 0


async def main():
    """Main async game loop for web compatibility."""
    
    # Initialize Pygame
    pygame.init()
    # Use resizable + scaled so canvas fills browser; 1280x720 starting size
    flags = pygame.SCALED | pygame.RESIZABLE
    screen = pygame.display.set_mode((1920, 1080), flags)
    pygame.display.set_caption("Infinite Tower - Web Demo")
    clock = pygame.time.Clock()
    
    print("="*60)
    print("INFINITE TOWER ENGINE - WEB DEMO")
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
    
    # Add attributes for UI
    player.level = 5
    player.exp = 350
    player.max_exp = 500
    player.mana = 75
    player.max_mana = 100
    player.stamina = 100
    player.max_stamina = 100
    player.equipment = []
    
    # Add starter loot
    print("✓ Generating starter loot...")
    for i in range(5):
        item = loot_gen.generate_random_item(floor_level=1)
        player.add_to_inventory(item)
        print(f"  Added: {item.name} ({item.rarity.value})")
    
    # Create enemies
    print("✓ Spawning enemies...")
    enemies = [
        Enemy("Goblin", health=30, damage=5, speed=2, position=(200, 150), enemy_type=EnemyType.FAST),
        Enemy("Orc", health=80, damage=12, speed=1, position=(600, 200), enemy_type=EnemyType.TANK),
        Enemy("Skeleton", health=40, damage=8, speed=2.5, position=(400, 400), enemy_type=EnemyType.RANGER),
    ]
    
    # Create 16-bit UI
    print("✓ Initializing 16-bit UI system...")
    game_ui = GameUI(screen, player)
    game_ui.set_floor(1, "Entrance Hall")
    game_ui.show_equipment = True
    
    # Welcome dialog
    game_ui.show_dialog(
        "Welcome to the Infinite Tower! Press E to toggle equipment. "
        "Use WASD to move and Space to attack. Press Enter to continue.",
        speaker="Tower Guide"
    )
    
    print("\n✓ All systems initialized!")
    print("\n" + "="*60)
    print("WEB DEMO CONTROLS:")
    print("  WASD or Arrow Keys - Move")
    print("  SHIFT - Sprint")
    print("  SPACE - Attack")
    print("  E - Toggle Equipment")
    print("  TAB or I - Inventory")
    print("  ENTER - Dismiss Dialog")
    print("  ESC - Quit")
    print("="*60)
    print("\nStarting web demo...\n")
    
    game_ui.add_notification("Web Demo Started!", game_ui.COLORS['text_green'])
    game_ui.add_notification("Welcome to Floor 1", game_ui.COLORS['text_yellow'])
    
    # Game state
    game_state = GameState()
    
    # Inventory UI (overlay)
    inventory_ui = InventoryUI(screen, player)
    
    # Main game loop (async for web)
    while game_state.running:
        dt = clock.tick(FRAME_RATE) / 1000.0
        game_state.frame_count += 1
        
        # Handle events
        events = pygame.event.get()
        for event in events:
            # First, let inventory overlay consume input if visible
            if inventory_ui.handle_input(event):
                continue
            if event.type == pygame.QUIT:
                game_state.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state.running = False
                elif event.key == pygame.K_f:
                    # Attempt fullscreen toggle (may be limited in browsers)
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
            elif event.type == pygame.VIDEORESIZE:
                # Resize canvas to match browser window
                screen = pygame.display.set_mode((event.w, event.h), flags)
                # Update UI surfaces that keep a reference
                game_ui.screen = screen
                inventory_ui.screen = screen
        
        # Update input
        input_handler.update()
        
        # Update player (disable movement input if inventory open)
        if not inventory_ui.is_visible:
            player.handle_input(input_handler)
        player.update(dt)
        
        # Update stamina
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
                    game_ui.show_dialog("You have been defeated!", speaker="Game Over")
        
        # Update UI
        game_ui.update(dt)
        
        # Render
        # Background gradient (responsive)
        sw, sh = screen.get_size()
        for y in range(sh):
            color_val = int(20 + (y / max(1, sh)) * 30)
            pygame.draw.line(screen, (color_val, color_val // 2, color_val // 3), (0, y), (sw, y))
        
        # Floor area
        sw, sh = screen.get_size()
        floor_rect = pygame.Rect(60, 60, sw - 120, sh - 140)
        pygame.draw.rect(screen, (40, 35, 30), floor_rect)
        pygame.draw.rect(screen, (80, 70, 60), floor_rect, 2)
        
        # Grid
        grid_size = 32
        grid_color = (50, 45, 40)
        for x in range(floor_rect.left, floor_rect.right, grid_size):
            pygame.draw.line(screen, grid_color, (x, floor_rect.top), (x, floor_rect.bottom), 1)
        for y in range(floor_rect.top, floor_rect.bottom, grid_size):
            pygame.draw.line(screen, grid_color, (floor_rect.left, y), (floor_rect.right, y), 1)
        
        # Draw entities
        for enemy in enemies:
            enemy.draw(screen)
        player.draw(screen)
        
        # Draw UI
        game_ui.draw()
        # Draw Inventory overlay last (on top)
        inventory_ui.draw()
        
        # Update display
        pygame.display.flip()
        
        # CRITICAL: Yield control to browser (required for Pygbag)
        await asyncio.sleep(0)
    
    print("\n✓ Web demo ended!")
    pygame.quit()


# Entry point
if __name__ == "__main__":
    # Run async main
    asyncio.run(main())

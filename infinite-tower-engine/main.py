"""
Infinite Tower Engine - Web Demo (Pygbag compatible)

This is the web-compatible version using asyncio for browser execution.
"""

import asyncio
import pygame
"""
Infinite Tower Engine - Web Demo (Pygbag compatible)

Web entry that runs the same Game class as the desktop version,
using an async loop compatible with browsers.
"""

import asyncio
import pygame

# Import Game and config from source or fallback path (for pygbag packaging)
try:
    from src.infinite_tower.game import Game
    from src.infinite_tower.config import FRAME_RATE, DEBUG_MODE
except ImportError:
    import sys
    sys.path.insert(0, 'infinite-tower-engine/src')
    from infinite_tower.game import Game
    from infinite_tower.config import FRAME_RATE, DEBUG_MODE


async def main():
    # Create and start the same Game used on desktop
    game = Game()
    game.start()
    clock = pygame.time.Clock()
    frames = 0
    
    # Main loop (async for web)
    while game.is_running:
        # Events and update
        game.handle_events()
        dt = clock.tick(FRAME_RATE) / 1000.0
        game.update(dt)
        
        # Render
        if game.screen:
            game.render(game.screen)
            pygame.display.flip()
        
        # Lightweight heartbeat for web debugging (first ~3s)
        frames += 1
        if DEBUG_MODE and frames % 30 == 0 and frames <= 180:
            print(f"[web] loop heartbeat: {frames} frames")
        
        # Yield to browser
        await asyncio.sleep(0)
    
    pygame.quit()


# Entry point
if __name__ == "__main__":
    # Run async main
    asyncio.run(main())

"""
Infinite Tower Engine - Web Demo (Pygbag compatible)

This is the web-compatible version using asyncio for browser execution.
It robustly resolves imports both in dev and inside the APK, and shows
an on-canvas error overlay if boot fails so issues are visible.
"""

import asyncio
import sys
import os
import traceback
import pygame


def _resolve_imports():
    """Attempt to import Game and config with multiple path strategies."""
    candidates = []
    here = os.path.dirname(__file__)
    candidates.extend([
        (None, 'src.infinite_tower'),
        (os.path.join(here, 'src'), 'infinite_tower'),
        (os.path.join(here), 'infinite_tower'),
        ('infinite-tower-engine/src', 'infinite_tower'),
        ('/data/data/infinite-tower-engine/src', 'infinite_tower'),
        ('/data/data/infinite-tower-engine/assets/src', 'infinite_tower'),
    ])

    last_err = None
    for path_entry, pkg in candidates:
        try:
            if path_entry and path_entry not in sys.path:
                sys.path.insert(0, path_entry)
            Game = __import__(f"{pkg}.game", fromlist=['Game']).Game
            cfg = __import__(f"{pkg}.config", fromlist=['FRAME_RATE', 'DEBUG_MODE'])
            FRAME_RATE = getattr(cfg, 'FRAME_RATE', 60)
            DEBUG_MODE = getattr(cfg, 'DEBUG_MODE', False)
            print(f"[web] Imported Game from pkg='{pkg}' path='{path_entry or 'sys'}'")
            return Game, FRAME_RATE, DEBUG_MODE
        except Exception as e:
            last_err = e
            # keep trying next candidate
            continue
    raise last_err or ImportError("Failed to import Game/config for web runner")


def _draw_error_overlay(message: str):
    """Initialize pygame minimally and draw a readable error to the canvas."""
    try:
        pygame.init()
        # Use a small window; pygbag will map it to the canvas
        screen = pygame.display.set_mode((1024, 576))
        screen.fill((30, 30, 30))
        font = pygame.font.Font(None, 28)
        lines = ["Boot Error:"] + message.splitlines()
        y = 40
        for line in lines[:18]:  # cap lines to avoid overflow
            surf = font.render(line, True, (240, 220, 220))
            screen.blit(surf, (20, y))
            y += 24
        foot = pygame.font.Font(None, 24).render("Check browser console for details.", True, (200, 200, 120))
        screen.blit(foot, (20, y + 12))
        pygame.display.flip()
        # keep the error on screen a bit in web context; event loop continues
    except Exception:
        pass


async def main():
    try:
        Game, FRAME_RATE, DEBUG_MODE = _resolve_imports()
    except Exception:
        err = traceback.format_exc()
        print(err)
        _draw_error_overlay(err)
        # keep yielding so the page remains responsive
        while True:
            await asyncio.sleep(0.1)

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
        if frames % 30 == 0 and frames <= 180:
            print(f"[web] loop heartbeat: {frames} frames")

        # Yield to browser
        await asyncio.sleep(0)

    pygame.quit()


# Entry point
if __name__ == "__main__":
    # Run async main
    asyncio.run(main())

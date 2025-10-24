#!/usr/bin/env python3
"""
Infinite Tower Engine - Main Entry Point

Copyright (c) 2025 CosmicPhoenix171. All Rights Reserved.
This is proprietary commercial software. Unauthorized use is prohibited.

TRADE SECRET AND CONFIDENTIAL INFORMATION
This file contains valuable commercial algorithms and game engine technology.
Any unauthorized access, use, copying, or distribution is strictly prohibited
and may result in legal action including criminal prosecution.
"""

import pygame
import sys
import os
import logging

# Add the src directory to the path so we can import infinite_tower
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infinite_tower import config
from infinite_tower.game import Game


def setup_logging():
    """Setup logging configuration for the game."""
    logging.basicConfig(
        level=logging.INFO if config.DEBUG_MODE else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main entry point for the Infinite Tower Engine."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize pygame
        pygame.init()
        logger.info("Starting Infinite Tower Engine")
        
        # Create the game instance
        game = Game()
        
        # Start the game
        game.start()
        
        # Main game loop
        clock = pygame.time.Clock()
        while game.is_running:
            # Handle events
            game.handle_events()
            
            # Update game state  
            game.update()
            
            # Render the frame
            if game.screen:
                game.render(game.screen)
                pygame.display.flip()
            
            # Maintain frame rate
            clock.tick(config.FRAME_RATE)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        # Ensure cleanup happens
        if 'game' in locals():
            game.end()
        pygame.quit()
        logger.info("Game shutdown complete")


if __name__ == "__main__":
    main()
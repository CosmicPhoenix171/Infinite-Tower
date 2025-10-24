# Design Document for Infinite Tower Engine

## Overview
The Infinite Tower Engine is a Pygame-based action looter game that features infinite floors, allowing players to explore procedurally generated environments filled with enemies, loot, and challenges. The game aims to provide an engaging experience with a focus on fast-paced action and strategic gameplay.

## Design Principles
1. **Modularity**: The game is designed with a modular architecture, allowing for easy updates and maintenance. Each component (e.g., entities, systems, UI) is encapsulated within its own module.

2. **Procedural Generation**: Floors are generated procedurally, ensuring that each playthrough offers a unique experience. This is achieved through algorithms that create layouts based on player input and random seeds.

3. **Separation of Concerns**: Different aspects of the game (e.g., physics, combat, AI) are handled by dedicated systems, promoting clean code and easier debugging.

4. **Scalability**: The engine is built to accommodate future expansions, such as new enemy types, items, and gameplay mechanics, without requiring significant rewrites.

## Architecture
- **Main Loop**: The game runs on a main loop that handles events, updates game state, and renders graphics. This loop is managed by the `loop.py` module.

- **Scenes**: The game utilizes a scene management system to transition between different game states (e.g., menu, gameplay). The `scene.py` module defines the structure and behavior of these scenes.

- **Entities**: The game features various entities, including players and enemies, each defined by their own classes (`player.py` and `enemy.py`). These classes manage properties such as health, movement, and interactions.

- **Items and Loot**: The `loot.py` module handles the generation and management of loot items, incorporating rarity and stacking mechanics to enhance gameplay.

- **Floor Generation**: The `generator.py` module is responsible for creating the procedural layouts of the game floors, ensuring a diverse range of environments.

- **Systems**: Core gameplay mechanics are implemented in separate systems:
  - **Physics**: Handled by `physics.py`, which includes collision detection and movement calculations.
  - **Combat**: Implemented in `combat.py`, managing attack mechanics and damage calculations.
  - **AI**: Enemy behavior is defined in `ai.py`, allowing for dynamic interactions with the player.

- **User Interface**: The HUD is managed by `hud.py`, displaying essential information such as health and loot status to the player.

## Conclusion
The Infinite Tower Engine is designed to provide a rich and engaging gameplay experience through its modular architecture, procedural generation, and separation of concerns. This design document serves as a foundation for the development and future enhancements of the game.
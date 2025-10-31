# Infinite Tower Engine

## Overview
Infinite Tower Engine is a Pygame-based action looter game that features an infinite number of floors, each procedurally generated to provide a unique gameplay experience. Players will navigate through various floors, battling enemies, collecting loot, and upgrading their characters.

## Features
- **Procedural Floor Generation**: Each floor is generated based on a seed derived from the player's name, ensuring a unique experience every time.
- **Dynamic Combat System**: Engage in fast-paced combat with various enemies, utilizing a robust combat system.
- **Loot Collection**: Discover and collect a variety of loot items, each with unique properties and rarity.
- **Player Progression**: Upgrade your character's abilities and equipment as you progress through the infinite tower.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd infinite-tower-engine
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

There are two runnable entry points:

- Full desktop game (uses the complete engine and game loop):
   - Run via the convenience launcher:
      ```
      python run_desktop_game.py
      ```
   - Or directly (equivalent):
      ```
      python src/infinite_tower/main.py
      ```

- Web demo (lightweight demo to test the same shared game code in a browser-friendly loop):
   - Run locally with Python (windowed, resizable):
      ```
      python main.py
      ```
   - To build for the web with pygbag and serve from `docs/`, follow WEB_DEPLOY_GUIDE.md.

## Directory Structure
```
infinite-tower-engine
├── src
│   ├── infinite_tower          # Main game package
│   ├── scripts                 # Scripts for data generation
├── tests                       # Unit tests for the game
├── assets                      # Game assets (sprites, sounds, fonts)
├── docs                        # Documentation files
├── .gitignore                  # Git ignore file
├── pyproject.toml              # Project metadata
├── requirements.txt            # Required Python packages
├── README.md                   # Project overview
├── run_desktop_game.py         # Convenience launcher for the full desktop game
└── LICENSE                     # Licensing information
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is proprietary software with all rights reserved. Unauthorized use, copying, modification, or distribution is strictly prohibited. See the LICENSE file for complete terms and conditions.
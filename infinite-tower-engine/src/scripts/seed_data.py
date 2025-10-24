import random

def generate_seed_data():
    player_data = {
        "name": "Player1",
        "level": 1,
        "health": 100,
        "experience": 0,
        "inventory": []
    }

    world_data = {
        "floors": [],
        "current_floor": 0,
        "max_floors": 100,
        "seed": random.randint(0, 10000)
    }

    return player_data, world_data

if __name__ == "__main__":
    player, world = generate_seed_data()
    print("Player Data:", player)
    print("World Data:", world)
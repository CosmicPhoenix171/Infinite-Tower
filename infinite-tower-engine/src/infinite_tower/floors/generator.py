import random

class FloorGenerator:
    def __init__(self, seed):
        self.seed = seed
        random.seed(seed)
        self.rooms = []

    def generate_floor(self, num_rooms):
        self.rooms = []
        for _ in range(num_rooms):
            room = self.create_room()
            self.rooms.append(room)
        return self.rooms

    def create_room(self):
        width = random.randint(5, 15)
        height = random.randint(5, 15)
        return {
            'width': width,
            'height': height,
            'enemies': self.generate_enemies(),
            'loot': self.generate_loot()
        }

    def generate_enemies(self):
        num_enemies = random.randint(0, 5)
        return [{'type': 'enemy', 'strength': random.randint(1, 10)} for _ in range(num_enemies)]

    def generate_loot(self):
        num_loot = random.randint(0, 3)
        return [{'type': 'loot', 'value': random.randint(1, 100)} for _ in range(num_loot)]
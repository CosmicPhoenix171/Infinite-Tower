class Player:
    def __init__(self, name, health=100, position=(0, 0)):
        self.name = name
        self.health = health
        self.position = position
        self.inventory = []

    def move(self, direction):
        if direction == 'up':
            self.position = (self.position[0], self.position[1] - 1)
        elif direction == 'down':
            self.position = (self.position[0], self.position[1] + 1)
        elif direction == 'left':
            self.position = (self.position[0] - 1, self.position[1])
        elif direction == 'right':
            self.position = (self.position[0] + 1, self.position[1])

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health += amount

    def add_to_inventory(self, item):
        self.inventory.append(item)

    def __str__(self):
        return f"Player {self.name}: Health={self.health}, Position={self.position}, Inventory={self.inventory}"
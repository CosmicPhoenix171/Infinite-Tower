class Loot:
    def __init__(self, name, rarity, stackable=True):
        self.name = name
        self.rarity = rarity
        self.stackable = stackable
        self.quantity = 1 if stackable else None

    def generate_loot(self):
        # Logic to generate loot based on rarity
        pass

    def stack(self, amount):
        if self.stackable:
            self.quantity += amount

    def __str__(self):
        return f"{self.name} (Rarity: {self.rarity}, Quantity: {self.quantity})"
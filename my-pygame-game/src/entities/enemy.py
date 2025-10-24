class Enemy:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = 100
        self.speed = 2

    def update(self):
        # Update enemy position or behavior
        pass

    def render(self, screen):
        # Draw the enemy on the screen
        pass

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.destroy()

    def destroy(self):
        # Handle enemy destruction
        pass
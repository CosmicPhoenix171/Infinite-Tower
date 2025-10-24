class Enemy:
    def __init__(self, name, health, damage, speed):
        self.name = name
        self.health = health
        self.damage = damage
        self.speed = speed
        self.position = (0, 0)

    def move(self, direction):
        if direction == "up":
            self.position = (self.position[0], self.position[1] - self.speed)
        elif direction == "down":
            self.position = (self.position[0], self.position[1] + self.speed)
        elif direction == "left":
            self.position = (self.position[0] - self.speed, self.position[1])
        elif direction == "right":
            self.position = (self.position[0] + self.speed, self.position[1])

    def attack(self, target):
        target.health -= self.damage

    def is_alive(self):
        return self.health > 0

    def __str__(self):
        return f"{self.name}: Health={self.health}, Damage={self.damage}, Position={self.position}"
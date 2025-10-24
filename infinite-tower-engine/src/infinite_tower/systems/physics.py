class Physics:
    def __init__(self):
        pass

    @staticmethod
    def check_collision(rect1, rect2):
        return rect1.colliderect(rect2)

    @staticmethod
    def move(rect, dx, dy):
        rect.x += dx
        rect.y += dy
        return rect

    @staticmethod
    def apply_gravity(rect, gravity, ground_level):
        if rect.y < ground_level:
            rect.y += gravity
        else:
            rect.y = ground_level
        return rect
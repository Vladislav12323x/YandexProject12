import arcade


class Enemy(arcade.Sprite):
    """Класс для враждебных мобов"""

    def __init__(self, x, y):
        super().__init__()
        self.width = 64
        self.height = 64
        self.texture = arcade.load_texture("../textures/Mob1.png")

        self.center_x = x
        self.center_y = y
        self.change_x = -2  # Движение влево по умолчанию
        self.boundary_left = x - 100
        self.boundary_right = x + 100

    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())

    def update(self, delta_time=0):
        """Обновление позиции врага"""
        self.center_x += self.change_x

        # Изменение направления при достижении границ
        if self.left < self.boundary_left or self.right > self.boundary_right:
            self.change_x *= -1

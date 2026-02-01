import arcade


class Heart(arcade.Sprite):
    """Класс для сердечек, показывающих жизни"""

    def __init__(self, active=True):
        super().__init__()
        self.active = active
        self.width = 32
        self.height = 32
        self.update_texture()

    def update_texture(self):
        """Обновление текстуры в зависимости от состояния"""
        if self.active:
            self.texture = arcade.load_texture("../textures/TrueHeart.png")
        else:
            self.texture = arcade.load_texture("../textures/FalseHeart.png")

    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())

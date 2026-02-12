import arcade


class Heart(arcade.Sprite):
    """Класс для сердечек, показывающих жизни"""

    def __init__(self, active=True):
        super().__init__()
        self.active = active
        self.width = 64
        self.height = 64
        self.update_texture()

    def update_texture(self):
        """Обновление текстуры в зависимости от состояния"""
        if self.active:
            self.texture = arcade.load_texture("textures/hud_heart.png")
        else:
            self.texture = arcade.load_texture("textures/hud_heart_empty.png")

    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())

from settings.consts import *


class PlayerCharacter(arcade.Sprite):
    """Класс для главного персонажа"""

    def __init__(self):
        super().__init__()
        self.width = 10
        self.height = 10
        self.character_face_direction = Facing.RIGHT
        self.stand_right_texture = arcade.load_texture("textures/rwalk0.webp")

        self.stand_left_texture = arcade.load_texture("textures/rwalk0.webp")

        self.walk_right_textures = []
        self.walk_left_textures = []

        for i in range(1, 3):
            texture_right = arcade.load_texture(f"textures/rwalk{i}.webp")
            texture_left = arcade.load_texture(f"textures/lwalk{i}.webp")

            self.walk_right_textures.append(texture_right)
            self.walk_left_textures.append(texture_left)

        self.texture = self.stand_right_texture
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        self.change_x = 0
        self.change_y = 0
        self.is_on_ground = False

    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())

    def update_animation(self, delta_time: float = 1 / 60):
        """Обновление анимации персонажа"""
        if self.change_x > 0 and self.character_face_direction == Facing.LEFT:
            self.character_face_direction = Facing.RIGHT
        elif self.change_x < 0 and self.character_face_direction == Facing.RIGHT:
            self.character_face_direction = Facing.LEFT

        if self.change_x == 0:
            if self.character_face_direction == Facing.RIGHT:
                self.texture = self.stand_right_texture
            else:
                self.texture = self.stand_left_texture
            return

        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0

        frame = self.cur_texture // 4

        if self.character_face_direction == Facing.RIGHT:
            self.texture = self.walk_right_textures[frame]
        else:
            self.texture = self.walk_left_textures[frame]

    def update(self, delta_time=0):
        """Обновление физики персонажа"""
        self.change_y -= GRAVITY

        if self.bottom <= 32 and self.change_y < 0:
            self.is_on_ground = True
            self.change_y = 0
            self.center_y = 32 + self.height / 2

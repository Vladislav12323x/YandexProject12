import os

import arcade

from settings.consts import *


class PlayerCharacter(arcade.Sprite):
    """Класс для главного персонажа"""

    def __init__(self):
        super().__init__()
        self.width = 10
        self.height = 10
        self.character_face_direction = Facing.RIGHT
        self.stand_right_texture = arcade.load_texture("../textures/Mario.png")

        try:
            if os.path.exists("../textures/Mario_left.png"):
                self.stand_left_texture = arcade.load_texture("../textures/Mario_left.png")
            else:
                self.stand_left_texture = self.stand_right_texture
        except:
            self.stand_left_texture = self.stand_right_texture

        self.walk_right_textures = []
        self.walk_left_textures = []

        # Загрузка текстур для ходьбы
        for i in range(1, 3):
            try:
                texture = arcade.load_texture("../textures/Mario.png")
            except:
                texture = self.stand_right_texture

            self.walk_right_textures.append(texture)

            try:
                if os.path.exists("../textures/Mario_left.png"):
                    self.walk_left_textures.append(arcade.load_texture("../textures/Mario_left.png"))
                else:
                    self.walk_left_textures.append(texture)
            except:
                self.walk_left_textures.append(texture)

        # Текущая текстура
        self.texture = self.stand_right_texture
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Физические параметры
        self.change_x = 0
        self.change_y = 0
        self.is_on_ground = False

    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())

    def update_animation(self, delta_time: float = 1 / 60):
        """Обновление анимации персонажа"""
        # Ходьба вправо
        if self.change_x > 0 and self.character_face_direction == Facing.LEFT:
            self.character_face_direction = Facing.RIGHT
        # Ходьба влево
        elif self.change_x < 0 and self.character_face_direction == Facing.RIGHT:
            self.character_face_direction = Facing.LEFT

        # Стоит на месте
        if self.change_x == 0:
            if self.character_face_direction == Facing.RIGHT:
                self.texture = self.stand_right_texture
            else:
                self.texture = self.stand_left_texture
            return

        # Анимация ходьбы
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
        # Применение гравитации
        self.change_y -= GRAVITY

        # Проверка, стоит ли персонаж на земле
        if self.bottom <= 32 and self.change_y < 0:
            self.is_on_ground = True
            self.change_y = 0
            self.center_y = 32 + self.height / 2

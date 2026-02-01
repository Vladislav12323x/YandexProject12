import os

import arcade

from models.enemy import Enemy
from settings.consts import *


class GameLevel:
    """Базовый класс для уровней"""

    def __init__(self, game_window):
        self.game_window = game_window
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()
        self.cloud_list = arcade.SpriteList()
        self.background = None
        self.map_width = 0
        self.setup()

    def setup(self):
        """Настройка уровня"""
        pass

    def update(self, delta_time):
        """Обновление уровня"""
        self.enemy_list.update()

    def draw(self):
        """Отрисовка уровня"""
        # Фон
        if self.background:
            try:
                arcade.draw_texture_rectangle(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    SCREEN_WIDTH, SCREEN_HEIGHT,
                    self.background
                )
            except:
                # Фолбэк для старых версий
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                    arcade.color.SKY_BLUE
                )
        else:
            # Рисуем простой фон если нет текстуры
            try:
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                    arcade.color.SKY_BLUE
                )
            except:
                # Еще один фолбэк для очень старых версий
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                    (135, 206, 235)  # Цвет неба в RGB
                )

        # Отрисовка всех спрайтов через SpriteList
        self.wall_list.draw()
        self.coin_list.draw()
        self.enemy_list.draw()
        self.finish_flag_list.draw()


class Level1(GameLevel):
    """Первый уровень игры в стиле классической Super Mario Bros"""

    def setup(self):
        # Создание списков спрайтов
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()
        self.cloud_list = arcade.SpriteList()  # Список для облаков

        # Создание земли (основная платформа)
        for x in range(0, 1000, 64):
            # Используем текстуру кирпичей вместо травы
            wall = arcade.Sprite("../textures/brick.png", 0.5)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        # Средние платформы
        platform_positions = [
            (300, 200),  # Первая платформа
            (600, 250),  # Вторая платформа
            (900, 200)  # Третья платформа
        ]
        for x, y in platform_positions:
            for i in range(0, 192, 64):  # 3 блока в длину
                if os.path.exists("../textures/brick1.png"):
                    wall = arcade.Sprite("../textures/brick1.png", 0.3)
                wall.center_x = x + i
                wall.center_y = y
                self.wall_list.append(wall)

        # Добавляем монеты над платформами
        coin_positions = [
            (330, 250), (360, 250), (390, 250),  # Над первой платформой
            (630, 300), (660, 300), (690, 300),  # Над второй платформой
            (930, 250), (960, 250), (990, 250)  # Над третьей платформой
        ]
        for x, y in coin_positions:
            coin = arcade.Sprite("../textures/coin.png", COIN_SCALE)
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)

        # Добавляем облака (как в оригинале)
        cloud_positions = [
            (100, 400),  # Первое облако
            (400, 450),  # Второе облако
            (700, 400)  # Третье облако
        ]
        for x, y in cloud_positions:
            cloud = arcade.Sprite("../textures/cloud.webp", 0.01)  # Облака обычно меньше
            cloud.center_x = x
            cloud.center_y = y
            self.cloud_list.append(cloud)

        # Флаг финиша
        if os.path.exists("../textures/Flag.png"):
            self.finish_flag = arcade.Sprite("../textures/Flag.png", 0.1)
        self.finish_flag.center_x = 950
        self.finish_flag.center_y = 96
        self.finish_flag_list.append(self.finish_flag)

        # Устанавливаем ширину уровня
        self.map_width = 1000


class Level2(GameLevel):
    """Второй уровень игры"""

    def setup(self):
        # Создание списков спрайтов
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()

        # Создание земли
        for x in range(0, 2000, 64):
            if os.path.exists("../textures/grass.png"):
                try:
                    wall = arcade.Sprite("../textures/grass.png", TILE_SCALING)
                except:
                    wall = create_solid_sprite(64, 64, arcade.color.GREEN)
                    wall.scale = TILE_SCALING
            else:
                wall = create_solid_sprite(64, 64, arcade.color.GREEN)
                wall.scale = TILE_SCALING

            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        # Платформы
        platform_positions = [(200, 150), (400, 250), (600, 150), (800, 300),
                              (1000, 200), (1200, 250), (1400, 150), (1600, 250)]
        for x, y in platform_positions:
            if os.path.exists("../textures/grass.png"):
                try:
                    wall = arcade.Sprite("../textures/grass.png", TILE_SCALING)
                except:
                    wall = create_solid_sprite(64, 64, arcade.color.BROWN)
                    wall.scale = TILE_SCALING
            else:
                wall = create_solid_sprite(64, 64, arcade.color.BROWN)
                wall.scale = TILE_SCALING

            wall.center_x = x
            wall.center_y = y
            self.wall_list.append(wall)

        # Монеты
        coin_positions = [(200, 200), (400, 300), (600, 200), (800, 350),
                          (1000, 250), (1200, 300), (1400, 200), (1600, 300)]
        for x, y in coin_positions:
            if os.path.exists("../textures/coin.png"):
                try:
                    coin = arcade.Sprite("../textures/coin.png", TILE_SCALING)
                except:
                    coin = create_solid_sprite(32, 32, arcade.color.GOLD)
                    coin.scale = TILE_SCALING
            else:
                coin = create_solid_sprite(32, 32, arcade.color.GOLD)
                coin.scale = TILE_SCALING

            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)

        # Враги
        enemy_positions = [(300, 96), (500, 96), (900, 240), (1100, 140), (1500, 96)]
        for x, y in enemy_positions:
            enemy = Enemy(x, y)
            self.enemy_list.append(enemy)

        # Флаг финиша
        if os.path.exists("../textures/Flag.png"):
            try:
                self.finish_flag = arcade.Sprite("../textures/Flag.png", TILE_SCALING)
            except:
                self.finish_flag = create_solid_sprite(64, 128, arcade.color.RED)
                self.finish_flag.scale = TILE_SCALING
        else:
            self.finish_flag = create_solid_sprite(64, 128, arcade.color.RED)
            self.finish_flag.scale = TILE_SCALING

        self.finish_flag.center_x = 1900
        self.finish_flag.center_y = 96
        self.finish_flag_list.append(self.finish_flag)

        self.map_width = 2000

import os
from datetime import datetime

import arcade.color

from models import Heart, PlayerCharacter
from scenes import Level1, Level2, CompleteMenu
from settings.consts import *


class MainGame(arcade.View):
    """Основной класс игры"""

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.SKY_BLUE

        # Установка пути к ресурсам
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Создание игрока
        self.player = PlayerCharacter()
        self.player.center_x = 128
        self.player.center_y = 192

        self.time_elapsed = datetime.now().second - 3

        # Список для игрока (для отрисовки в старых версиях)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        # Физический движок
        self.physics_engine = None

        # Параметры камеры
        self.view_left = 0
        self.view_bottom = 0
        self.level_width = 1500

        # Очки и жизни
        self.score = 0
        self.lives = 3
        self.hearts_list = arcade.SpriteList()

        # Текущий уровень
        self.current_level = 1
        self.levels = [Level1(self), Level2(self)]

        # Настройка игры
        self.setup()

    def setup(self):
        """Настройка игры перед началом"""

        map_name = "../l1.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        self.platforms = tile_map.sprite_lists["platforms"]
        self.coins = tile_map.sprite_lists["coins"]
        self.flags = tile_map.sprite_lists["flags"]
        self.enemies = tile_map.sprite_lists["enemies"]
        self.other = tile_map.sprite_lists["other"]

        # Создание физического движка
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.platforms,
            gravity_constant=GRAVITY
        )

        # Создание сердечек для отображения жизней
        self.hearts_list = arcade.SpriteList()
        for i in range(3):
            heart = Heart(active=(i < self.lives))
            heart.center_x = 30 + i * 40
            heart.center_y = SCREEN_HEIGHT - 20
            self.hearts_list.append(heart)

        # Сброс очков при начале новой игры
        if self.current_level == 1:
            self.score = 0

    def on_draw(self):
        """Отрисовка всех объектов на экране"""
        # Очищаем экран
        self.clear()

        # Отрисовка уровня
        self.platforms.draw()
        self.coins.draw()
        self.enemies.draw()
        self.other.draw()
        self.flags.draw()

        # Отрисовка всех спрайтов через SpriteList
        self.player_list.draw()
        self.hearts_list.draw()

        # Отрисовка интерфейса (очков, уровня) без смещения камеры
        self._draw_ui()

    def _draw_ui(self):
        """Отрисовка пользовательского интерфейса"""
        arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 30,
                         arcade.color.BLACK, 18, font_name="Contra Phobotech")
        arcade.draw_text(f"Уровень: {self.current_level}", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 60,
                         arcade.color.BLACK, 18, font_name="Contra Phobotech")

    def lose_life(self):
        """Потеря одной жизни"""
        if self.lives > 0 and datetime.now().second - self.time_elapsed > 3:
            self.time_elapsed = datetime.now().second
            self.lives -= 1
            # Обновление сердечек
            self.hearts_list = arcade.SpriteList()
            for i in range(3):
                heart = Heart(active=(i < self.lives))
                heart.center_x = 30 + i * 40
                heart.center_y = SCREEN_HEIGHT - 20
                self.hearts_list.append(heart)
        if self.lives <= 0:
            self.setup()
            self.player.center_x = 64
            self.player.center_y = 128

    def on_update(self, delta_time):
        # Обновление физики
        self.physics_engine.update()

        # Обновление анимации игрока
        self.player.update_animation(delta_time)

        # Обновление сердечек
        self.hearts_list.update()

        # Проверка сбора монет
        coin_hit_list = arcade.check_for_collision_with_list(
            self.player, self.coins
        )

        for coin in coin_hit_list:
            coin.kill()
            self.score += 10

        # Проверка столкновений с врагами
        enemy_hit_list = arcade.check_for_collision_with_list(
            self.player, self.enemies
        )

        for enemy in enemy_hit_list:
            enemy.kill()
            self.lose_life()

        # Проверка достижения флага финиша
        if arcade.check_for_collision_with_list(
                self.player, self.flags
        ):
            self.complete_level()

    def complete_level(self):
        """Завершение текущего уровня"""
        # self.game_state = GameState.LEVEL_COMPLETE
        game_view = CompleteMenu(self.score)
        self.window.show_view(game_view)

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.ESCAPE:
            self.game_state = GameState.PAUSED

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            if self.player.change_x < 0:
                self.player.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            if self.player.change_x > 0:
                self.player.change_x = 0

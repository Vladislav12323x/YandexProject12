import os
from datetime import datetime

import arcade.color
from arcade import Camera2D
from pyglet.graphics import Batch

from core.shader import CustomCRT
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

        # Камеры
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()

        # Физический движок
        self.physics_engine = None

        # Очки и жизни
        self.score = 0
        self.lives = 3
        self.hearts_list = arcade.SpriteList()

        # Текущий уровень
        self.current_level = 1
        self.levels = [Level1(self), Level2(self)]
        self.batch = Batch()

        p_width, p_height = self.window.get_size()

        self.crt_shader = CustomCRT(
            p_width,
            p_height,
            self.window.ctx
        )

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
            player_sprite=self.player,
            platforms=self.platforms,
            gravity_constant=GRAVITY
        )

        # Создание сердечек для отображения жизней
        self.hearts_list = arcade.SpriteList()
        for i in range(3):
            heart = Heart(active=(i < self.lives))
            heart.center_x = 30 + i * 50
            heart.center_y = SCREEN_HEIGHT - 30
            self.hearts_list.append(heart)

        # Сброс очков при начале новой игры
        if self.current_level == 1:
            self.score = 0

    def on_draw(self):
        """Отрисовка всех объектов на экране"""
        self.crt_shader.use()
        self.crt_shader.clear()

        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)

        self.clear()

        self.world_camera.use()
        self.platforms.draw()
        self.coins.draw()
        self.enemies.draw()
        self.other.draw()
        self.flags.draw()
        self.player_list.draw()

        # Отрисовка всех спрайтов через SpriteList
        self.gui_camera.use()
        self.hearts_list.draw()

        # Отрисовка интерфейса (очков, уровня)
        self.batch.draw()

        self.window.use()
        self.window.clear()

        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        self.window.default_camera.use()

        self.crt_shader.draw()

    def lose_life(self):
        """Потеря одной жизни"""
        if self.lives > 0 and datetime.now().second - self.time_elapsed > 3:
            self.time_elapsed = datetime.now().second
            self.lives -= 1
            # Обновление сердечек
            self.hearts_list = arcade.SpriteList()
            for i in range(3):
                heart = Heart(active=(i < self.lives))
                heart.center_x = 30 + i * 50
                heart.center_y = SCREEN_HEIGHT - 30
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
            coin.remove_from_sprite_lists()
            self.score += 10

        arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 30,
                         arcade.color.BLACK, 18, font_name="Contra Phobotech")
        arcade.draw_text(f"Уровень: {self.current_level}", SCREEN_WIDTH - 300, SCREEN_HEIGHT - 60,
                         arcade.color.BLACK, 18, font_name="Contra Phobotech")

        self.text = arcade.Text(f"Уровень: {self.current_level} Очки: {self.score}",
                                self.width - 530, self.height - 30, arcade.color.WHITE,
                                18, batch=self.batch, font_name="Contra Phobotech")

        # Проверка столкновений с врагами
        enemy_hit_list = arcade.check_for_collision_with_list(
            self.player, self.enemies
        )

        for enemy in enemy_hit_list:
            enemy.remove_from_sprite_lists()
            self.lose_life()

        # Проверка достижения флага финиша
        if arcade.check_for_collision_with_list(
                self.player, self.flags
        ):
            self.complete_level()

        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        world_w = 3000
        world_h = 1000
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def complete_level(self):
        """Завершение текущего уровня"""
        game_view = CompleteMenu(self.score)
        self.window.show_view(game_view)

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key in (arcade.key.LEFT, arcade.key.A):
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif key in (arcade.key.UP, arcade.key.SPACE, arcade.key.W):
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key in (arcade.key.LEFT, arcade.key.A) and self.player.change_x < 0:
            self.player.change_x = 0
        elif key in (arcade.key.RIGHT, arcade.key.D) and self.player.change_x > 0:
            self.player.change_x = 0

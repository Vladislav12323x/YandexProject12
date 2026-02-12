import random
from datetime import datetime

import arcade.color
from arcade import Camera2D
from arcade.particles import Emitter, FadeParticle, EmitBurst
from pyglet.graphics import Batch

from core.shader import CustomCRT
from models import Heart, PlayerCharacter
from scenes import CompleteMenu
from scenes.pause import PauseView
from settings.consts import *


def smoke_mutator(p):
    p.scale_x *= 1.02
    p.scale_y *= 1.02
    p.alpha = max(0, p.alpha - 2)


def make_smoke_puff(x, y):
    return Emitter(
        center_xy=(x, y),
        emit_controller=EmitBurst(12),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=SMOKE_TEX,
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 0.6),
            lifetime=random.uniform(1.5, 2.5),
            start_alpha=200, end_alpha=0,
            scale=random.uniform(0.6, 0.9),
            mutation_callback=smoke_mutator,
        ),
    )


class MainGame(arcade.View):
    """Основной класс игры"""

    def __init__(self, menu_view):
        super().__init__()

        self.background = arcade.load_texture("textures/main_back.webp")

        self.sound = arcade.load_sound("back.mp3")

        self.background_color = arcade.color.SKY_BLUE

        self.menu_view = menu_view

        self.player = PlayerCharacter()
        self.player.center_x = 128
        self.player.center_y = 192

        self.time_elapsed = datetime.now().timestamp() - 3

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()

        self.physics_engine = None

        self.score = 0
        self.lives = 3
        self.hearts_list = arcade.SpriteList()

        self.current_level = 1
        self.batch = Batch()

        self.emitters = []
        self.smoke = None

        p_width, p_height = self.window.get_size()

        self.crt_shader = CustomCRT(
            p_width,
            p_height,
            self.window.ctx
        )

        self.setup()

    def setup(self):
        """Настройка игры перед началом"""

        self.sound.play()

        map_name = f"l{self.current_level}.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

        self.platforms = tile_map.sprite_lists["platforms"]
        self.coins = tile_map.sprite_lists["coins"]
        self.flags = tile_map.sprite_lists["flags"]
        self.enemies = tile_map.sprite_lists["enemies"]
        self.jump = tile_map.sprite_lists["jump"]
        self.other = tile_map.sprite_lists["other"]

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            platforms=self.platforms,
            gravity_constant=GRAVITY
        )

        self.hearts_list = arcade.SpriteList()
        for i in range(3):
            heart = Heart(active=(i < self.lives))
            heart.center_x = 30 + i * 50
            heart.center_y = SCREEN_HEIGHT - 30
            self.hearts_list.append(heart)

        if self.current_level == 1:
            self.score = 0

    def on_draw(self):
        """Отрисовка всех объектов на экране"""
        self.crt_shader.use()
        self.crt_shader.clear()

        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)

        self.clear()

        arcade.draw_texture_rect(self.background, arcade.rect.LBWH(0, 0, self.width, self.height))

        self.world_camera.use()
        self.platforms.draw()
        self.coins.draw()
        self.enemies.draw()
        self.other.draw()
        self.flags.draw()
        self.jump.draw()
        for e in self.emitters:
            e.draw()
        self.player_list.draw()

        self.gui_camera.use()
        self.hearts_list.draw()

        self.batch.draw()

        self.window.use()
        self.window.clear()

        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        self.window.default_camera.use()

        self.crt_shader.draw()

    def lose_life(self):
        """Потеря одной жизни"""
        if self.lives > 0 and datetime.now().timestamp() - self.time_elapsed > 0.3:
            self.time_elapsed = datetime.now().timestamp()
            self.lives -= 1
            self.hearts_list = arcade.SpriteList()
            for i in range(3):
                heart = Heart(active=(i < self.lives))
                heart.center_x = 30 + i * 50
                heart.center_y = SCREEN_HEIGHT - 30
                self.hearts_list.append(heart)
        if self.lives <= 0:
            self.kill()

    def kill(self):
        self.setup()
        self.player.center_x = 128
        self.player.center_y = 192
        self.lives = 3
        for i in range(3):
            heart = Heart(active=(i < self.lives))
            heart.center_x = 30 + i * 50
            heart.center_y = SCREEN_HEIGHT - 30
            self.hearts_list.append(heart)

    def on_show_view(self):
        p_width, p_height = self.window.get_size()

        self.crt_shader = CustomCRT(
            p_width,
            p_height,
            self.window.ctx
        )

    def on_update(self, delta_time):
        self.physics_engine.update()

        self.player.update_animation(delta_time)

        self.hearts_list.update()

        coin_hit_list = arcade.check_for_collision_with_list(
            self.player, self.coins
        )

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            self.score += 10

        jump_hit_list = arcade.check_for_collision_with_list(
            self.player, self.jump
        )

        for jump in jump_hit_list:
            self.player.change_y = PLAYER_JUMP_SPEED * 1.7

        self.text = arcade.Text(f"Уровень: {self.current_level} Очки: {self.score}",
                                self.width - 530, self.height - 30, arcade.color.WHITE,
                                18, batch=self.batch, font_name="Contra Phobotech")

        enemy_hit_list = arcade.check_for_collision_with_list(
            self.player, self.enemies
        )

        for enemy in enemy_hit_list:
            enemy.remove_from_sprite_lists()
            self.lose_life()

        if self.player.center_y < 0:
            self.kill()

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
        world_w = 4000
        world_h = 1000
        cam_x = max(half_w, min(world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        if self.smoke:
            self.smoke.center_x = self.player.center_x
            self.smoke.center_y = self.player.center_y

        emitters_copy = self.emitters.copy()  # Защищаемся от мутаций списка
        for e in emitters_copy:
            e.update(delta_time)
        for e in emitters_copy:
            if e.can_reap():  # Готов к уборке?
                self.emitters.remove(e)

    def complete_level(self):
        """Завершение текущего уровня"""
        if self.current_level == 3:
            complete_view = CompleteMenu(self.score, self.menu_view)
            self.window.show_view(complete_view)
        self.current_level += 1
        self.player.center_x = 128
        self.player.center_y = 192
        self.lives = 3
        self.setup()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key in (arcade.key.LEFT, arcade.key.A):
            self.emitters.append(make_smoke_puff(self.player.center_x, self.player.center_y - 20))
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.emitters.append(make_smoke_puff(self.player.center_x, self.player.center_y - 20))
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif key in (arcade.key.UP, arcade.key.SPACE, arcade.key.W):
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        if key == arcade.key.ESCAPE:
            pause_view = PauseView(self, self.menu_view)
            self.window.show_view(pause_view)

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key in (arcade.key.LEFT, arcade.key.A) and self.player.change_x < 0:
            self.player.change_x = 0
        elif key in (arcade.key.RIGHT, arcade.key.D) and self.player.change_x > 0:
            self.player.change_x = 0

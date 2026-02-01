import os

from models import Heart, PlayerCharacter
from scenes import Level1, Level2
from settings.consts import *


class MainGame(arcade.Window):
    """Основной класс игры"""

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Установка пути к ресурсам
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Состояние игры
        self.game_state = GameState.PLAYING

        # Создание игрока
        self.player = PlayerCharacter()
        self.player.center_x = 64
        self.player.center_y = 128

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
        self.current_level_object = self.levels[self.current_level - 1]

        # Настройка игры
        self.setup()

    def setup(self):
        """Настройка игры перед началом"""
        # Создание физического движка
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.current_level_object.wall_list,
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

        # Сброс камеры
        self.view_left = 0
        self.view_bottom = 0
        self.level_width = self.current_level_object.map_width

    def on_draw(self):
        """Отрисовка всех объектов на экране"""
        # Очищаем экран
        self.clear()

        # Смещаем все спрайты для эмуляции камеры
        self._shift_sprites_for_camera()

        # Отрисовка уровня
        self.current_level_object.draw()

        # Отрисовка всех спрайтов через SpriteList
        self.player_list.draw()
        self.hearts_list.draw()

        # Восстанавливаем оригинальные позиции
        self._restore_sprites_positions()

        # Отрисовка интерфейса (очков, уровня) без смещения камеры
        self._draw_ui()

        # Отображение меню в зависимости от состояния игры
        self._draw_game_menus()

    def _shift_sprites_for_camera(self):
        """Смещение спрайтов для эмуляции камеры"""
        self.original_positions = []

        # Все списки спрайтов, которые нужно сместить
        sprite_lists = [
            self.current_level_object.wall_list,
            self.current_level_object.coin_list,
            self.current_level_object.enemy_list,
            self.current_level_object.finish_flag_list,
            self.player_list
        ]

        for sprite_list in sprite_lists:
            for sprite in sprite_list:
                self.original_positions.append((sprite, sprite.center_x))
                sprite.center_x -= self.view_left

    def _restore_sprites_positions(self):
        """Восстановление оригинальных позиций спрайтов"""
        for sprite, original_x in self.original_positions:
            sprite.center_x = original_x

    def _draw_ui(self):
        """Отрисовка пользовательского интерфейса"""
        try:
            arcade.draw_text(f"Очки: {self.score}", 10, SCREEN_HEIGHT - 30,
                             arcade.color.WHITE, 18)
            arcade.draw_text(f"Уровень: {self.current_level}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30,
                             arcade.color.WHITE, 18)
        except:
            # Фолбэк для очень старых версий
            arcade.draw_text(f"Очки: {self.score}", 10, SCREEN_HEIGHT - 30,
                             arcade.color.WHITE, 14)
            arcade.draw_text(f"Уровень: {self.current_level}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30,
                             arcade.color.WHITE, 14)

    def _draw_game_menus(self):
        """Отрисовка меню игры в зависимости от состояния"""
        if self.game_state == GameState.PAUSED:
            self._draw_pause_menu()
        elif self.game_state == GameState.LEVEL_COMPLETE:
            self._draw_level_complete_menu()
        elif self.game_state == GameState.GAME_OVER:
            self._draw_game_over_menu()

    def _draw_pause_menu(self):
        """Отрисовка меню паузы"""
        try:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)
        except:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0))

        try:
            arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.GRAY)
        except:
            arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, (128, 128, 128))
        try:
            arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.WHITE, 2)
        except:
            arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, (255, 255, 255), 2)

        try:
            arcade.draw_text("ПАУЗА", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.WHITE, 40,
                             anchor_x="center")
            arcade.draw_text("R - перезапустить уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, arcade.color.WHITE,
                             20, anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10, arcade.color.WHITE, 20,
                             anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.WHITE, 20,
                             anchor_x="center")
            arcade.draw_text("ESC - продолжить игру", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, 20,
                             anchor_x="center")
        except:
            arcade.draw_text("ПАУЗА", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.WHITE, 24,
                             anchor_x="center")
            arcade.draw_text("R - перезапустить уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, arcade.color.WHITE,
                             14, anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10, arcade.color.WHITE, 14,
                             anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.WHITE, 14,
                             anchor_x="center")
            arcade.draw_text("ESC - продолжить игру", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, 14,
                             anchor_x="center")

    def _draw_level_complete_menu(self):
        """Отрисовка меню завершения уровня"""
        try:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.GOLD)
        except:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (255, 215, 0))
        try:
            arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.YELLOW)
        except:
            arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, (255, 255, 0))
        try:
            arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.BLACK, 2)
        except:
            arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, (0, 0, 0), 2)

        try:
            arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.BLACK, 30,
                             anchor_x="center")
            arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30, arcade.color.BLACK, 24,
                             anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30, arcade.color.BLACK, 20,
                             anchor_x="center")
            arcade.draw_text("R - повторить уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.BLACK, 20,
                             anchor_x="center")
        except:
            arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.BLACK, 20,
                             anchor_x="center")
            arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30, arcade.color.BLACK, 16,
                             anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30, arcade.color.BLACK, 14,
                             anchor_x="center")
            arcade.draw_text("R - повторить уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.BLACK, 14,
                             anchor_x="center")

    def _draw_game_over_menu(self):
        """Отрисовка меню Game Over"""
        try:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.RED)
        except:
            arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (255, 0, 0))
        try:
            arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.DARK_RED)
        except:
            arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, (139, 0, 0))
        try:
            arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.BLACK, 2)
        except:
            arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, (0, 0, 0), 2)

        try:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.WHITE, 40,
                             anchor_x="center")
            arcade.draw_text(f"Финальные очки: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
                             arcade.color.WHITE, 24, anchor_x="center")
            arcade.draw_text("R - начать заново", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30, arcade.color.WHITE, 20,
                             anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.WHITE, 20,
                             anchor_x="center")
        except:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.WHITE, 24,
                             anchor_x="center")
            arcade.draw_text(f"Финальные очки: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
                             arcade.color.WHITE, 16, anchor_x="center")
            arcade.draw_text("R - начать заново", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30, arcade.color.WHITE, 14,
                             anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.WHITE, 14,
                             anchor_x="center")

    def center_camera_to_player(self):
        """Центрирование камеры на игроке"""
        # Центрирование по горизонтали
        screen_center_x = self.player.center_x - (SCREEN_WIDTH / 2)

        # Не двигаем камеру дальше границ уровня
        screen_center_x = max(screen_center_x, 0)
        screen_center_x = min(screen_center_x, self.level_width - SCREEN_WIDTH)

        # Плавное перемещение камеры
        self.view_left = screen_center_x

    def on_update(self, delta_time):
        """Логика обновления игры"""
        if self.game_state == GameState.PLAYING:
            # Обновление физики
            self.physics_engine.update()

            # Обновление анимации игрока
            self.player.update_animation(delta_time)

            # Обновление текущего уровня
            self.current_level_object.update(delta_time)

            # Обновление сердечек
            self.hearts_list.update()

            # Центрирование камеры
            self.center_camera_to_player()

            # Проверка сбора монет
            coin_hit_list = arcade.check_for_collision_with_list(
                self.player, self.current_level_object.coin_list
            )

            for coin in coin_hit_list:
                coin.kill()
                self.score += 10

            # Проверка столкновений с врагами
            enemy_hit_list = arcade.check_for_collision_with_list(
                self.player, self.current_level_object.enemy_list
            )

            if enemy_hit_list:
                self.lose_life()

            # Проверка достижения флага финиша
            if arcade.check_for_collision_with_list(
                    self.player, self.current_level_object.finish_flag_list
            ):
                self.complete_level()

    def lose_life(self):
        """Потеря одной жизни"""
        if self.lives > 0:
            self.lives -= 1
            # Обновление сердечек
            self.hearts_list = arcade.SpriteList()
            for i in range(3):
                heart = Heart(active=(i < self.lives))
                heart.center_x = 30 + i * 40
                heart.center_y = SCREEN_HEIGHT - 20
                self.hearts_list.append(heart)

            # Перезапуск уровня при потере всех жизней
            if self.lives <= 0:
                self.game_state = GameState.GAME_OVER
            else:
                # Перезапуск текущего уровня
                self.setup()

    def complete_level(self):
        """Завершение текущего уровня"""
        self.game_state = GameState.LEVEL_COMPLETE

    def next_level(self):
        """Переход на следующий уровень"""
        self.current_level += 1
        if self.current_level > len(self.levels):
            # Если все уровни пройдены
            self.game_state = GameState.GAME_OVER
        else:
            self.current_level_object = self.levels[self.current_level - 1]
            self.setup()
            self.game_state = GameState.PLAYING

    def restart_level(self):
        """Перезапуск текущего уровня"""
        self.setup()
        self.game_state = GameState.PLAYING

    def restart_game(self):
        """Начать игру заново"""
        self.current_level = 1
        self.lives = 3
        self.current_level_object = self.levels[self.current_level - 1]
        self.setup()
        self.game_state = GameState.PLAYING

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if self.game_state == GameState.PLAYING:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.player.change_x = -PLAYER_MOVEMENT_SPEED
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.player.change_x = PLAYER_MOVEMENT_SPEED
            elif key == arcade.key.UP or key == arcade.key.SPACE:
                if self.physics_engine.can_jump():
                    self.player.change_y = PLAYER_JUMP_SPEED
            elif key == arcade.key.ESCAPE:
                self.game_state = GameState.PAUSED
        else:
            if key == arcade.key.ESCAPE:
                if self.game_state == GameState.PAUSED:
                    self.game_state = GameState.PLAYING

            if key == arcade.key.R:
                if self.game_state == GameState.GAME_OVER:
                    self.restart_game()
                else:
                    self.restart_level()

            if key == arcade.key.N and self.game_state == GameState.LEVEL_COMPLETE:
                self.next_level()

            if key == arcade.key.Q and (self.game_state == GameState.PAUSED or
                                        self.game_state == GameState.GAME_OVER):
                arcade.close_window()

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            if self.player.change_x < 0:
                self.player.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            if self.player.change_x > 0:
                self.player.change_x = 0

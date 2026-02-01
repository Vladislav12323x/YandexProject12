import arcade
from settings.consts import *


class CompleteMenu(arcade.View):
    def __init__(self, score):
        super().__init__()
        self.score = score

    def on_draw(self):
        self.clear()
        """Отрисовка меню завершения уровня"""
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.GOLD)
        arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.YELLOW)
        arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.BLACK, 2)

        arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.color.BLACK, 30,
                         anchor_x="center", font_name="Contra Phobotech")
        arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30, arcade.color.BLACK, 24,
                         anchor_x="center", font_name="Contra Phobotech")
        arcade.draw_text("N - следующий уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30, arcade.color.BLACK, 20,
                         anchor_x="center", font_name="Contra Phobotech")
        arcade.draw_text("R - повторить уровень", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 70, arcade.color.BLACK, 20,
                         anchor_x="center", font_name="Contra Phobotech")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.N:
            pass

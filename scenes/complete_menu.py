from arcade.gui import UIAnchorLayout, UIBoxLayout, UIManager, UILabel, UIFlatButton

from core.shader import CustomCRT
from scenes.settings import SettingsView
from settings.consts import *


class CompleteMenu(arcade.View):
    def __init__(self, score, menu_view):
        super().__init__()
        self.background = arcade.load_texture("textures/menu_background.png")

        self.menu_view = menu_view
        self.score = score

        with open("score", "r") as f:
            self.best_result = int(f.read().strip())

        with open("score", "w") as f:
            f.write(str(self.score))

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=30)
        self.setup_widgets()
        self.anchor_layout.add(self.box_layout)
        self.manager.add(self.anchor_layout)

        p_width, p_height = self.window.get_size()

        self.crt_shader = CustomCRT(
            p_width,
            p_height,
            self.window.ctx
        )

    def setup_widgets(self):
        """Настройка виджетов в меню"""
        title = UILabel(text="Победа!!!",
                        font_size=48,
                        text_color=arcade.color.WHITE,
                        width=400,
                        align="center",
                        bold=True)
        self.box_layout.add(title)

        score = UILabel(text=f"Счёт: {self.score}",
                        font_size=18,
                        text_color=arcade.color.WHITE,
                        width=400,
                        align="center",
                        bold=True)
        self.box_layout.add(score)

        best_result = UILabel(text=f"Рекорд: {self.best_result}",
                        font_size=18,
                        text_color=arcade.color.WHITE,
                        width=400,
                        align="center",
                        bold=True)
        self.box_layout.add(best_result)

        if self.score > self.best_result:
            win = UILabel(text="Вы побили свой рекорд",
                                  font_size=24,
                                  text_color=arcade.color.WHITE,
                                  width=400,
                                  align="center",
                                  bold=True)
            self.box_layout.add(win)

        exit_button = UIFlatButton(text="В меню", width=200, height=50)
        exit_button.on_click = lambda event: self.menu()
        self.box_layout.add(exit_button)

    def menu(self):
        self.window.show_view(self.menu_view)

    def settings(self):
        game_view = SettingsView(self)
        self.window.show_view(game_view)

    def on_show_view(self):
        p_width, p_height = self.window.get_size()

        self.crt_shader = CustomCRT(
            p_width,
            p_height,
            self.window.ctx
        )
        self.manager.enable()

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        """Отрисовка с исправлением масштабирования"""
        self.crt_shader.use()
        self.crt_shader.clear()

        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)

        arcade.draw_texture_rect(self.background, arcade.rect.LBWH(0, 0, self.width, self.height))
        self.manager.draw()

        self.window.use()
        self.window.clear()

        self.window.ctx.viewport = (0, 0, self.window.width, self.window.height)
        self.window.default_camera.use()

        self.crt_shader.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)

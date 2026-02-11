from arcade.gui import UIFlatButton, UILabel, UIManager, UIAnchorLayout, UIBoxLayout

from core.main_game import MainGame
from core.shader import CustomCRT
from settings.consts import *


class MenuView(arcade.View):
    """Класс меню"""

    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("textures/menu_background.png")

        self.manager = UIManager()
        self.manager.enable()

        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)
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
        title = UILabel(text=SCREEN_TITLE,
                        font_size=32,
                        text_color=arcade.color.WHITE,
                        width=400,
                        align="center",
                        bold=True)
        self.box_layout.add(title)

        sub_title = UILabel(text="Специально для Яндекс Лицея",
                            font_size=14,
                            text_color=arcade.color.WHITE,
                            width=400,
                            align="center",
                            bold=True)
        self.box_layout.add(sub_title)

        play_button = UIFlatButton(text="Играть", width=200, height=50)  # Убрал color для теста
        play_button.on_click = lambda event: self.play()
        self.box_layout.add(play_button)

        settings_button = UIFlatButton(text="Настройки", width=200, height=50)
        settings_button.on_click = lambda event: print("Настройки")
        self.box_layout.add(settings_button)

        exit_button = UIFlatButton(text="Выход", width=200, height=50)
        exit_button.on_click = lambda event: exit(0)
        self.box_layout.add(exit_button)

    def play(self):
        game_view = MainGame()
        self.window.show_view(game_view)

    def on_draw(self):
        """Отрисовка с исправлением масштабирования"""
        # c шейдером 🥰🥰🥰
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

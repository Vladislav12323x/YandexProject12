import json

import arcade
from arcade.gui import UIAnchorLayout, UIBoxLayout, UIManager, UILabel, UIFlatButton, UIInputText

from core.shader import CustomCRT
from settings import consts



class SettingsView(arcade.View):
    def __init__(self, view):
        super().__init__()
        self.background = arcade.load_texture("textures/menu_background.png")

        self.view = view
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
        title = UILabel(text="Настройки",
                        font_size=32,
                        text_color=arcade.color.WHITE,
                        width=400,
                        align="center",
                        bold=True)
        self.box_layout.add(title)

        resolution = UILabel(text="Разрешение",
                        font_size=14,
                        text_color=arcade.color.WHITE,
                        width=400,
                        align="center",
                        bold=True)
        self.box_layout.add(resolution)

        self.input_width = UIInputText(x=0, y=0, width=200, height=50, text=str(consts.SCREEN_WIDTH), font_size=16)
        self.box_layout.add(self.input_width)

        self.input_height = UIInputText(x=0, y=0, width=200, height=50, text=str(consts.SCREEN_HEIGHT), font_size=16)
        self.box_layout.add(self.input_height)

        apply_button = UIFlatButton(text="Применить", width=200, height=50)
        apply_button.on_click = lambda event: self.change_resolution()
        self.box_layout.add(apply_button)

        exit_button = UIFlatButton(text="Вернуться", width=200, height=50)
        exit_button.on_click = lambda event: self.continue_view()
        self.box_layout.add(exit_button)

    def continue_view(self):
        self.window.show_view(self.view)

    def change_resolution(self):
        consts.SCREEN_WIDTH = int(self.input_width.text)
        consts.SCREEN_HEIGHT = int(self.input_height.text)
        with open("settings.json", "w", encoding="utf-8") as f:
            f.write(json.dumps({"width": consts.SCREEN_WIDTH, "height": consts.SCREEN_HEIGHT}))
        self.window.set_size(consts.SCREEN_WIDTH * 2, consts.SCREEN_HEIGHT * 2)
        p_width, p_height = self.window.get_size()

        self.crt_shader = CustomCRT(
            p_width,
            p_height,
            self.window.ctx
        )


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

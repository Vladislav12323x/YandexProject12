import json

import arcade

from scenes.menu import MenuView
from settings import *
from settings import consts


def main():
    """Главная функция"""
    arcade.text.load_font("SNPro-VariableFont_wght.ttf")
    arcade.text.load_font("ContraPhobotech-Regular.otf")
    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)
        consts.SCREEN_WIDTH = settings["width"]
        consts.SCREEN_HEIGHT = settings["height"]
    window = arcade.Window(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT, consts.SCREEN_TITLE)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
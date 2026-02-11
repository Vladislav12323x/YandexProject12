from core.main_game import MainGame
from scenes.menu import MenuView
from settings.consts import *


def main():
    """Главная функция"""
    arcade.text.load_font("SNPro-VariableFont_wght.ttf")
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    # menu_view = MainGame()
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
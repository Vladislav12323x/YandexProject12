from core.main_game import MainGame
from settings.consts import *


def main():
    """Главная функция"""
    arcade.text.load_font("ContraPhobotech-Regular.otf")
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    menu_view = MainGame()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
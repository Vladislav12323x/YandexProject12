import arcade

from core.main_game import MainGame


def main():
    """Главная функция"""
    window = MainGame()
    arcade.run()


if __name__ == "__main__":
    main()
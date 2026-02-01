from enum import Enum

import arcade

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Марио"

# Константы для физики
GRAVITY = 0.8
PLAYER_JUMP_SPEED = 15
PLAYER_MOVEMENT_SPEED = 5

# Масштаб спрайтов
CHARACTER_SCALING = 0.04
TILE_SCALING = 0.8
ENEMY_SCALING = 1
HEART_SCALING = 0.5
COIN_SCALE = 0.07

# Камера
CAMERA_LERP = 0.01


# Константы для направления персонажа
class Facing(Enum):
    RIGHT = 0
    LEFT = 1


# Константы для состояний игры
class GameState(Enum):
    PLAYING = 0
    PAUSED = 1
    LEVEL_COMPLETE = 2
    GAME_OVER = 3


def create_solid_sprite(width, height, color):
    """Создание цветного спрайта для старых версий Arcade"""
    try:
        # Пытаемся создать через SpriteSolidColor
        return arcade.SpriteSolidColor(width, height, color)
    except:
        # Если не работает, создаем вручную
        sprite = arcade.Sprite()
        sprite.width = width
        sprite.height = height
        sprite.center_x = 0
        sprite.center_y = 0

        try:
            # Попытка создать текстуру
            texture = arcade.Texture.create_empty("solid_color", (width, height))
            sprite.texture = texture
            sprite.color = color
        except:
            # Если и это не работает
            try:
                texture = arcade.Texture.create_empty("solid_fallback", (width, height))
                sprite.texture = texture
                sprite.color = color
            except:
                sprite = arcade.Sprite()
                sprite.width = width
                sprite.height = height
                sprite.color = color
                sprite.center_x = 0
                sprite.center_y = 0

        return sprite

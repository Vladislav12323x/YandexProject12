import arcade
import os
import math

# Константы
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Марио"

# Константы для физики
GRAVITY = 0.8
PLAYER_JUMP_SPEED = 15
PLAYER_MOVEMENT_SPEED = 5

# Масштаб спрайтов
CHARACTER_SCALING = 0.05
TILE_SCALING = 0.5
ENEMY_SCALING = 1
HEART_SCALING = 0.5
COIN_SCALE = 0.07

# Константы для состояний игры
GAME_STATE_PLAYING = 0
GAME_STATE_PAUSED = 1
GAME_STATE_LEVEL_COMPLETE = 2
GAME_STATE_GAME_OVER = 3

# Константы для направления персонажа
RIGHT_FACING = 0
LEFT_FACING = 1

class Heart(arcade.Sprite):
    """Класс для сердечек, показывающих жизни"""
    def __init__(self, active=True):
        super().__init__()
        self.active = active
        self.width = 32
        self.height = 32
        self.update_texture()
    
    def update_texture(self):
        """Обновление текстуры в зависимости от состояния"""
        if self.active:
            self.texture = arcade.load_texture("TrueHeart.png")
        else:
            self.texture = arcade.load_texture("FalseHeart.png")
    
    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())

class Enemy(arcade.Sprite):
    """Класс для враждебных мобов"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 64
        self.height = 64
        self.texture = arcade.load_texture("Mob1.png")
        
        self.center_x = x
        self.center_y = y
        self.change_x = -2  # Движение влево по умолчанию
        self.boundary_left = x - 100
        self.boundary_right = x + 100
    
    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())
    
    def update(self, delta_time=0):
        """Обновление позиции врага"""
        self.center_x += self.change_x
        
        # Изменение направления при достижении границ
        if self.left < self.boundary_left or self.right > self.boundary_right:
            self.change_x *= -1

class PlayerCharacter(arcade.Sprite):
    """Класс для главного персонажа"""
    def __init__(self):
        super().__init__()
        self.width = 10
        self.height = 10
        self.character_face_direction = RIGHT_FACING
        self.stand_right_texture = arcade.load_texture("Mario.png")
        
        try:
            if os.path.exists("Mario_left.png"):
                self.stand_left_texture = arcade.load_texture("Mario_left.png")
            else:
                self.stand_left_texture = self.stand_right_texture
        except:
            self.stand_left_texture = self.stand_right_texture
        
        self.walk_right_textures = []
        self.walk_left_textures = []
        
        # Загрузка текстур для ходьбы
        for i in range(1, 3):
            try:
                texture = arcade.load_texture(f"Mario.png")
            except:
                texture = self.stand_right_texture
            
            self.walk_right_textures.append(texture)
            
            try:
                if os.path.exists("Mario_left.png"):
                    self.walk_left_textures.append(arcade.load_texture("Mario_left.png"))
                else:
                    self.walk_left_textures.append(texture)
            except:
                self.walk_left_textures.append(texture)
        
        # Текущая текстура
        self.texture = self.stand_right_texture
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        
        # Физические параметры
        self.change_x = 0
        self.change_y = 0
        self.is_on_ground = False
        
    def _get_unique_name(self):
        """Генерация уникального имени для текстуры"""
        import uuid
        return str(uuid.uuid4())
    
    def update_animation(self, delta_time: float = 1/60):
        """Обновление анимации персонажа"""
        # Ходьба вправо
        if self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        # Ходьба влево
        elif self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        
        # Стоит на месте
        if self.change_x == 0:
            if self.character_face_direction == RIGHT_FACING:
                self.texture = self.stand_right_texture
            else:
                self.texture = self.stand_left_texture
            return
        
        # Анимация ходьбы
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        
        frame = self.cur_texture // 4
        
        if self.character_face_direction == RIGHT_FACING:
            self.texture = self.walk_right_textures[frame]
        else:
            self.texture = self.walk_left_textures[frame]
        
    def update(self, delta_time=0):
        """Обновление физики персонажа"""
        # Применение гравитации
        self.change_y -= GRAVITY
        
        # Проверка, стоит ли персонаж на земле
        if self.bottom <= 32 and self.change_y < 0:
            self.is_on_ground = True
            self.change_y = 0
            self.center_y = 32 + self.height/2

class GameLevel:
    """Базовый класс для уровней"""
    def __init__(self, game_window):
        self.game_window = game_window
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()
        self.cloud_list = arcade.SpriteList()
        self.background = None
        self.map_width = 0
        self.setup()
    
    def setup(self):
        """Настройка уровня"""
        pass
    
    def update(self, delta_time):
        """Обновление уровня"""
        self.enemy_list.update()
    
    def draw(self):
        """Отрисовка уровня"""
        # Фон
        if self.background:
            try:
                arcade.draw_texture_rectangle(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                    SCREEN_WIDTH, SCREEN_HEIGHT,
                    self.background
                )
            except:
                # Фолбэк для старых версий
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                    arcade.color.SKY_BLUE
                )
        else:
            # Рисуем простой фон если нет текстуры
            try:
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                    arcade.color.SKY_BLUE
                )
            except:
                # Еще один фолбэк для очень старых версий
                arcade.draw_lrbt_rectangle_filled(
                    0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                    (135, 206, 235)  # Цвет неба в RGB
                )
        
        # Отрисовка всех спрайтов через SpriteList
        self.wall_list.draw()
        self.coin_list.draw()
        self.enemy_list.draw()
        self.finish_flag_list.draw()

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

class Level1(GameLevel):
    """Первый уровень игры в стиле классической Super Mario Bros"""
    def setup(self):
        # Создание списков спрайтов
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()
        self.cloud_list = arcade.SpriteList()  # Список для облаков
        
        # Создание земли (основная платформа)
        for x in range(0, 1000, 64):
            # Используем текстуру кирпичей вместо травы
            wall = arcade.Sprite("brick.png", 0.5)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)
        
        
        # Средние платформы
        platform_positions = [
            (300, 200),    # Первая платформа
            (600, 250),    # Вторая платформа
            (900, 200)     # Третья платформа
        ]
        for x, y in platform_positions:
            for i in range(0, 192, 64):  # 3 блока в длину
                if os.path.exists("brick1.png"):
                        wall = arcade.Sprite("brick1.png", 0.3)
                wall.center_x = x + i
                wall.center_y = y
                self.wall_list.append(wall)
        
        # Добавляем монеты над платформами
        coin_positions = [
            (330, 250), (360, 250), (390, 250),  # Над первой платформой
            (630, 300), (660, 300), (690, 300),  # Над второй платформой
            (930, 250), (960, 250), (990, 250)   # Над третьей платформой
        ]
        for x, y in coin_positions:
            if os.path.exists("coin.png") or os.path.exists("coin.png"):
                coin = arcade.Sprite("coin.png", COIN_SCALE)
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)
        
        # Добавляем облака (как в оригинале)
        cloud_positions = [
            (100, 400),   # Первое облако
            (400, 450),   # Второе облако
            (700, 400)    # Третье облако
        ]
        for x, y in cloud_positions:
            if os.path.exists("cloud.webp"):
                cloud = arcade.Sprite("cloud.webp", 0.01)  # Облака обычно меньше
            cloud.center_x = x
            cloud.center_y = y
            self.cloud_list.append(cloud)

        
        # Флаг финиша
        if os.path.exists("Flag.png"):
            self.finish_flag = arcade.Sprite("Flag.png", 0.1)
        self.finish_flag.center_x = 950
        self.finish_flag.center_y = 96
        self.finish_flag_list.append(self.finish_flag)
        
        # Устанавливаем ширину уровня
        self.map_width = 1000

class Level2(GameLevel):
    """Второй уровень игры"""
    def setup(self):
        # Создание списков спрайтов
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()
        
        # Создание земли
        for x in range(0, 2000, 64):
            if os.path.exists("grass.png"):
                try:
                    wall = arcade.Sprite("grass.png", TILE_SCALING)
                except:
                    wall = create_solid_sprite(64, 64, arcade.color.GREEN)
                    wall.scale = TILE_SCALING
            else:
                wall = create_solid_sprite(64, 64, arcade.color.GREEN)
                wall.scale = TILE_SCALING
            
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)
        
        # Платформы
        platform_positions = [(200, 150), (400, 250), (600, 150), (800, 300), 
                             (1000, 200), (1200, 250), (1400, 150), (1600, 250)]
        for x, y in platform_positions:
            if os.path.exists("grass.png"):
                try:
                    wall = arcade.Sprite("grass.png", TILE_SCALING)
                except:
                    wall = create_solid_sprite(64, 64, arcade.color.BROWN)
                    wall.scale = TILE_SCALING
            else:
                wall = create_solid_sprite(64, 64, arcade.color.BROWN)
                wall.scale = TILE_SCALING
            
            wall.center_x = x
            wall.center_y = y
            self.wall_list.append(wall)
        
        # Монеты
        coin_positions = [(200, 200), (400, 300), (600, 200), (800, 350),
                         (1000, 250), (1200, 300), (1400, 200), (1600, 300)]
        for x, y in coin_positions:
            if os.path.exists("coin.png"):
                try:
                    coin = arcade.Sprite("coin.png", TILE_SCALING)
                except:
                    coin = create_solid_sprite(32, 32, arcade.color.GOLD)
                    coin.scale = TILE_SCALING
            else:
                coin = create_solid_sprite(32, 32, arcade.color.GOLD)
                coin.scale = TILE_SCALING
            
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)
        
        # Враги
        enemy_positions = [(300, 96), (500, 96), (900, 240), (1100, 140), (1500, 96)]
        for x, y in enemy_positions:
            enemy = Enemy(x, y)
            self.enemy_list.append(enemy)
        
        # Флаг финиша
        if os.path.exists("Flag.png"):
            try:
                self.finish_flag = arcade.Sprite("Flag.png", TILE_SCALING)
            except:
                self.finish_flag = create_solid_sprite(64, 128, arcade.color.RED)
                self.finish_flag.scale = TILE_SCALING
        else:
            self.finish_flag = create_solid_sprite(64, 128, arcade.color.RED)
            self.finish_flag.scale = TILE_SCALING
        
        self.finish_flag.center_x = 1900
        self.finish_flag.center_y = 96
        self.finish_flag_list.append(self.finish_flag)
        
        self.map_width = 2000

class MarioGame(arcade.Window):
    """Основной класс игры"""
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # Установка пути к ресурсам
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
        # Состояние игры
        self.game_state = GAME_STATE_PLAYING
        
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
        if self.game_state == GAME_STATE_PAUSED:
            self._draw_pause_menu()
        elif self.game_state == GAME_STATE_LEVEL_COMPLETE:
            self._draw_level_complete_menu()
        elif self.game_state == GAME_STATE_GAME_OVER:
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
            arcade.draw_text("ПАУЗА", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.WHITE, 40, anchor_x="center")
            arcade.draw_text("R - перезапустить уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20, arcade.color.WHITE, 20, anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10, arcade.color.WHITE, 20, anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.WHITE, 20, anchor_x="center")
            arcade.draw_text("ESC - продолжить игру", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100, arcade.color.WHITE, 20, anchor_x="center")
        except:
            arcade.draw_text("ПАУЗА", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.WHITE, 24, anchor_x="center")
            arcade.draw_text("R - перезапустить уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20, arcade.color.WHITE, 14, anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10, arcade.color.WHITE, 14, anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.WHITE, 14, anchor_x="center")
            arcade.draw_text("ESC - продолжить игру", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100, arcade.color.WHITE, 14, anchor_x="center")
    
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
            arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.BLACK, 30, anchor_x="center")
            arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, arcade.color.BLACK, 24, anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, arcade.color.BLACK, 20, anchor_x="center")
            arcade.draw_text("R - повторить уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.BLACK, 20, anchor_x="center")
        except:
            arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.BLACK, 20, anchor_x="center")
            arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, arcade.color.BLACK, 16, anchor_x="center")
            arcade.draw_text("N - следующий уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, arcade.color.BLACK, 14, anchor_x="center")
            arcade.draw_text("R - повторить уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.BLACK, 14, anchor_x="center")
    
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
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.WHITE, 40, anchor_x="center")
            arcade.draw_text(f"Финальные очки: {self.score}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, arcade.color.WHITE, 24, anchor_x="center")
            arcade.draw_text("R - начать заново", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, arcade.color.WHITE, 20, anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.WHITE, 20, anchor_x="center")
        except:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.WHITE, 24, anchor_x="center")
            arcade.draw_text(f"Финальные очки: {self.score}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, arcade.color.WHITE, 16, anchor_x="center")
            arcade.draw_text("R - начать заново", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, arcade.color.WHITE, 14, anchor_x="center")
            arcade.draw_text("Q - выход из игры", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.WHITE, 14, anchor_x="center")
    
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
        if self.game_state == GAME_STATE_PLAYING:
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
                self.game_state = GAME_STATE_GAME_OVER
            else:
                # Перезапуск текущего уровня
                self.setup()
    
    def complete_level(self):
        """Завершение текущего уровня"""
        self.game_state = GAME_STATE_LEVEL_COMPLETE
    
    def next_level(self):
        """Переход на следующий уровень"""
        self.current_level += 1
        if self.current_level > len(self.levels):
            # Если все уровни пройдены
            self.game_state = GAME_STATE_GAME_OVER
        else:
            self.current_level_object = self.levels[self.current_level - 1]
            self.setup()
            self.game_state = GAME_STATE_PLAYING
    
    def restart_level(self):
        """Перезапуск текущего уровня"""
        self.setup()
        self.game_state = GAME_STATE_PLAYING
    
    def restart_game(self):
        """Начать игру заново"""
        self.current_level = 1
        self.lives = 3
        self.current_level_object = self.levels[self.current_level - 1]
        self.setup()
        self.game_state = GAME_STATE_PLAYING
    
    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if self.game_state == GAME_STATE_PLAYING:
            if key == arcade.key.LEFT or key == arcade.key.A:
                self.player.change_x = -PLAYER_MOVEMENT_SPEED
            elif key == arcade.key.RIGHT or key == arcade.key.D:
                self.player.change_x = PLAYER_MOVEMENT_SPEED
            elif key == arcade.key.UP or key == arcade.key.SPACE:
                if self.physics_engine.can_jump():
                    self.player.change_y = PLAYER_JUMP_SPEED
            elif key == arcade.key.ESCAPE:
                self.game_state = GAME_STATE_PAUSED
        else:
            if key == arcade.key.ESCAPE:
                if self.game_state == GAME_STATE_PAUSED:
                    self.game_state = GAME_STATE_PLAYING
            
            if key == arcade.key.R:
                if self.game_state == GAME_STATE_GAME_OVER:
                    self.restart_game()
                else:
                    self.restart_level()
            
            if key == arcade.key.N and self.game_state == GAME_STATE_LEVEL_COMPLETE:
                self.next_level()
            
            if key == arcade.key.Q and (self.game_state == GAME_STATE_PAUSED or 
                                      self.game_state == GAME_STATE_GAME_OVER):
                arcade.close_window()
    
    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            if self.player.change_x < 0:
                self.player.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            if self.player.change_x > 0:
                self.player.change_x = 0

def main():
    """Главная функция"""
    window = MarioGame()
    arcade.run()

if __name__ == "__main__":
    main()
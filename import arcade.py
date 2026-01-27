import arcade
import os

# Константы
SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Марио"

# Константы для физики
GRAVITY = 0.8
PLAYER_JUMP_SPEED = 25
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
    
    def update(self, delta_time=0):
        """Обновление позиции врага"""
        self.center_x += self.change_x
        if self.left < self.boundary_left or self.right > self.boundary_right:
            self.change_x *= -1


class PlayerCharacter(arcade.Sprite):
    """Класс для главного персонажа"""
    def __init__(self):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.stand_right_texture = arcade.load_texture("Mario.png")
        
        if os.path.exists("Mario_left.png"):
            self.stand_left_texture = arcade.load_texture("Mario_left.png")
        else:
            self.stand_left_texture = self.stand_right_texture
        
        self.walk_right_textures = [self.stand_right_texture, self.stand_right_texture]
        self.walk_left_textures = [self.stand_left_texture, self.stand_left_texture]
        
        self.texture = self.stand_right_texture
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        
        self.change_x = 0
        self.change_y = 0
        
    def update_animation(self, delta_time: float = 1/60):
        if self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        elif self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        
        if self.change_x == 0:
            if self.character_face_direction == RIGHT_FACING:
                self.texture = self.stand_right_texture
            else:
                self.texture = self.stand_left_texture
            return
        
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        frame = self.cur_texture // 4
        
        if self.character_face_direction == RIGHT_FACING:
            self.texture = self.walk_right_textures[frame]
        else:
            self.texture = self.walk_left_textures[frame]


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
        pass
    
    def update(self, delta_time):
        self.enemy_list.update()
    
    def draw(self):
        if self.background:
            arcade.draw_texture_rectangle(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                self.background
            )
        else:
            arcade.draw_lrbt_rectangle_filled(
                0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
                arcade.color.SKY_BLUE
            )
        
        self.wall_list.draw()
        self.coin_list.draw()
        self.enemy_list.draw()
        self.finish_flag_list.draw()
        self.cloud_list.draw()


def create_solid_sprite(width, height, color):
    try:
        return arcade.SpriteSolidColor(width, height, color)
    except:
        sprite = arcade.Sprite()
        sprite.width = width
        sprite.height = height
        texture = arcade.Texture.create_empty("solid", (width, height))
        sprite.texture = texture
        sprite.color = color
        return sprite


class Level1(GameLevel):
    def setup(self):
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()
        self.cloud_list = arcade.SpriteList()
        
        # Земля
        for x in range(0, 1064, 64):  # до 1000 + 64
            wall = arcade.Sprite("brick.png", 0.5) if os.path.exists("brick.png") else create_solid_sprite(64, 64, arcade.color.BROWN)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)
        
        # Платформы
        platform_positions = [(300, 200), (600, 250), (900, 200)]
        for x, y in platform_positions:
            for i in range(0, 192, 64):
                if os.path.exists("brick1.png"):
                    wall = arcade.Sprite("brick1.png", 0.3)
                else:
                    wall = create_solid_sprite(64, 32, arcade.color.RED)
                wall.center_x = x + i
                wall.center_y = y
                self.wall_list.append(wall)
        
        # Монеты
        coin_positions = [
            (330, 250), (360, 250), (390, 250),
            (630, 300), (660, 300), (690, 300),
            (930, 250), (960, 250), (990, 250)
        ]
        for x, y in coin_positions:
            if os.path.exists("coin.png"):
                coin = arcade.Sprite("coin.png", COIN_SCALE)
            else:
                coin = create_solid_sprite(32, 32, arcade.color.GOLD)
                coin.scale = COIN_SCALE
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)
        
        # Облака
        cloud_positions = [(100, 400), (400, 450), (700, 400)]
        for x, y in cloud_positions:
            if os.path.exists("cloud.webp"):
                cloud = arcade.Sprite("cloud.webp", 0.01)
                cloud.center_x = x
                cloud.center_y = y
                self.cloud_list.append(cloud)
        
        # Флаг
        if os.path.exists("Flag.png"):
            self.finish_flag = arcade.Sprite("Flag.png", 0.1)
        else:
            self.finish_flag = create_solid_sprite(64, 128, arcade.color.RED)
        self.finish_flag.center_x = 950
        self.finish_flag.center_y = 96
        self.finish_flag_list.append(self.finish_flag)
        
        self.map_width = 1000


class Level2(GameLevel):
    def setup(self):
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.finish_flag_list = arcade.SpriteList()
        
        for x in range(0, 2000, 64):
            if os.path.exists("grass.png"):
                wall = arcade.Sprite("grass.png", TILE_SCALING)
            else:
                wall = create_solid_sprite(64, 64, arcade.color.GREEN)
                wall.scale = TILE_SCALING
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)
        
        platform_positions = [(200, 150), (400, 250), (600, 150), (800, 300), 
                             (1000, 200), (1200, 250), (1400, 150), (1600, 250)]
        for x, y in platform_positions:
            if os.path.exists("grass.png"):
                wall = arcade.Sprite("grass.png", TILE_SCALING)
            else:
                wall = create_solid_sprite(64, 64, arcade.color.BROWN)
                wall.scale = TILE_SCALING
            wall.center_x = x
            wall.center_y = y
            self.wall_list.append(wall)
        
        coin_positions = [(200, 200), (400, 300), (600, 200), (800, 350),
                         (1000, 250), (1200, 300), (1400, 200), (1600, 300)]
        for x, y in coin_positions:
            if os.path.exists("coin.png"):
                coin = arcade.Sprite("coin.png", COIN_SCALE)
            else:
                coin = create_solid_sprite(32, 32, arcade.color.GOLD)
                coin.scale = COIN_SCALE
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)
        
        enemy_positions = [(300, 96), (500, 96), (900, 240), (1100, 140), (1500, 96)]
        for x, y in enemy_positions:
            enemy = Enemy(x, y)
            self.enemy_list.append(enemy)
        
        if os.path.exists("Flag.png"):
            self.finish_flag = arcade.Sprite("Flag.png", 0.1)
        else:
            self.finish_flag = create_solid_sprite(64, 128, arcade.color.RED)
        self.finish_flag.center_x = 1900
        self.finish_flag.center_y = 96
        self.finish_flag_list.append(self.finish_flag)
        
        self.map_width = 2000


class MarioGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
        self.game_state = GAME_STATE_PLAYING
        self.player = PlayerCharacter()
        self.player.center_x = 64
        self.player.center_y = 128
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.physics_engine = None
        self.view_left = 0
        self.level_width = 1500
        self.score = 0
        self.lives = 3
        self.current_level = 1
        self.levels = [Level1(self), Level2(self)]
        self.current_level_object = self.levels[self.current_level - 1]
        self.setup()
    
    def setup(self):
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.current_level_object.wall_list,
            gravity_constant=GRAVITY
        )
        
        self.hearts_list = arcade.SpriteList()
        for i in range(3):
            heart = Heart(active=(i < self.lives))
            heart.center_x = 30 + i * 40
            heart.center_y = SCREEN_HEIGHT - 20
            self.hearts_list.append(heart)
        
        if self.current_level == 1:
            self.score = 0
        
        self.view_left = 0
        self.level_width = self.current_level_object.map_width
    
    def on_draw(self):
        self.clear()
        
        # Камера: показываем часть мира
        MarioGame.set_viewport(
            self.view_left,
            self.view_left + SCREEN_WIDTH,
            0,
            SCREEN_HEIGHT
        )
        
        self.current_level_object.draw()
        self.player_list.draw()
        self.hearts_list.draw()
        
        # Сброс камеры для UI
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        self._draw_ui()
        self._draw_game_menus()
    
    def _draw_ui(self):
        arcade.draw_text(f"Очки: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 18)
        arcade.draw_text(f"Уровень: {self.current_level}", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30, arcade.color.WHITE, 18)
    
    def _draw_game_menus(self):
        if self.game_state == GAME_STATE_PAUSED:
            self._draw_pause_menu()
        elif self.game_state == GAME_STATE_LEVEL_COMPLETE:
            self._draw_level_complete_menu()
        elif self.game_state == GAME_STATE_GAME_OVER:
            self._draw_game_over_menu()
    
    def _draw_pause_menu(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.BLACK)
        arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.GRAY)
        arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.WHITE, 2)
        arcade.draw_text("ПАУЗА", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.WHITE, 40, anchor_x="center")
        arcade.draw_text("R - перезапустить уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("N - следующий уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Q - выход из игры", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("ESC - продолжить игру", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100, arcade.color.WHITE, 20, anchor_x="center")
    
    def _draw_level_complete_menu(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.GOLD)
        arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.YELLOW)
        arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.BLACK, 2)
        arcade.draw_text("УРОВЕНЬ ПРОЙДЕН!", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.BLACK, 30, anchor_x="center")
        arcade.draw_text(f"Очки: {self.score}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, arcade.color.BLACK, 24, anchor_x="center")
        arcade.draw_text("N - следующий уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, arcade.color.BLACK, 20, anchor_x="center")
        arcade.draw_text("R - повторить уровень", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.BLACK, 20, anchor_x="center")
    
    def _draw_game_over_menu(self):
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, arcade.color.RED)
        arcade.draw_lrbt_rectangle_filled(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.DARK_RED)
        arcade.draw_lrbt_rectangle_outline(30, SCREEN_WIDTH - 30, 30, SCREEN_HEIGHT - 30, arcade.color.BLACK, 2)
        arcade.draw_text("GAME OVER", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 100, arcade.color.WHITE, 40, anchor_x="center")
        arcade.draw_text(f"Финальные очки: {self.score}", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 30, arcade.color.WHITE, 24, anchor_x="center")
        arcade.draw_text("R - начать заново", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 30, arcade.color.WHITE, 20, anchor_x="center")
        arcade.draw_text("Q - выход из игры", SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 70, arcade.color.WHITE, 20, anchor_x="center")
    
    def center_camera_to_player(self):
        screen_center_x = self.player.center_x - SCREEN_WIDTH / 2
        screen_center_x = max(screen_center_x, 0)
        screen_center_x = min(screen_center_x, self.level_width - SCREEN_WIDTH)
        self.view_left = int(screen_center_x)
    
    def on_update(self, delta_time):
        if self.game_state == GAME_STATE_PLAYING:
            self.physics_engine.update()
            self.player.update_animation(delta_time)
            self.current_level_object.update(delta_time)
            
            self.center_camera_to_player()
            
            # Сбор монет
            coin_hit_list = arcade.check_for_collision_with_list(self.player, self.current_level_object.coin_list)
            for coin in coin_hit_list:
                coin.kill()
                self.score += 10
            
            # Столкновение с врагами
            enemy_hit_list = arcade.check_for_collision_with_list(self.player, self.current_level_object.enemy_list)
            if enemy_hit_list:
                self.lose_life()
            
            # Флаг финиша
            if arcade.check_for_collision_with_list(self.player, self.current_level_object.finish_flag_list):
                self.complete_level()
    
    def lose_life(self):
        if self.lives > 0:
            self.lives -= 1
            self.hearts_list = arcade.SpriteList()
            for i in range(3):
                heart = Heart(active=(i < self.lives))
                heart.center_x = 30 + i * 40
                heart.center_y = SCREEN_HEIGHT - 20
                self.hearts_list.append(heart)
            if self.lives <= 0:
                self.game_state = GAME_STATE_GAME_OVER
            else:
                self.setup()
    
    def complete_level(self):
        self.game_state = GAME_STATE_LEVEL_COMPLETE
    
    def next_level(self):
        self.current_level += 1
        if self.current_level > len(self.levels):
            self.game_state = GAME_STATE_GAME_OVER
        else:
            self.current_level_object = self.levels[self.current_level - 1]
            self.setup()
            self.game_state = GAME_STATE_PLAYING
    
    def restart_level(self):
        self.setup()
        self.game_state = GAME_STATE_PLAYING
    
    def restart_game(self):
        self.current_level = 1
        self.lives = 3
        self.current_level_object = self.levels[0]
        self.setup()
        self.game_state = GAME_STATE_PLAYING
    
    def on_key_press(self, key, modifiers):
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
            if key == arcade.key.ESCAPE and self.game_state == GAME_STATE_PAUSED:
                self.game_state = GAME_STATE_PLAYING
            elif key == arcade.key.R:
                if self.game_state == GAME_STATE_GAME_OVER:
                    self.restart_game()
                else:
                    self.restart_level()
            elif key == arcade.key.N and self.game_state == GAME_STATE_LEVEL_COMPLETE:
                self.next_level()
            elif key == arcade.key.Q and (self.game_state == GAME_STATE_PAUSED or self.game_state == GAME_STATE_GAME_OVER):
                arcade.close_window()
    
    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A) and self.player.change_x < 0:
            self.player.change_x = 0
        elif key in (arcade.key.RIGHT, arcade.key.D) and self.player.change_x > 0:
            self.player.change_x = 0


def main():
    window = MarioGame()
    arcade.run()


if __name__ == "__main__":
    main()
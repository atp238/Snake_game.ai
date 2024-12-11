import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
import time
import os

pygame.init()
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, 'BlackOpsOne-Regular.ttf')
font = pygame.font.Font(font_path, 25)
# font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 50

class SnakeGameAI:
    def __init__(self, w=820, h=720): 
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.background = pygame.image.load('g.png')
        self.reset()
        self.editing_speed = False
        self.new_speed = ""

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        # Sử dụng phép chia nguyên để đảm bảo tọa độ là số nguyên và là bội số của BLOCK_SIZE
        self.head = Point((self.w // 2) // BLOCK_SIZE * BLOCK_SIZE, 
                          (self.h // 2) // BLOCK_SIZE * BLOCK_SIZE)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        self.snake_colors = [self._get_random_color() for _ in self.snake]
        self.last_color_change_time = time.time()

    def _get_random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def _place_food(self):
        # Đảm bảo mồi được đặt trong giới hạn của màn hình và là bội số của BLOCK_SIZE
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        else:
            self.food_color = self._get_random_color()

    def play_step(self, action):
        self.frame_iteration += 1
        reward = 0
        game_over = False
        score = self.score
        
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.w - 150 <= mouse_pos[0] <= self.w - 10 and 0 <= mouse_pos[1] <= 30:
                    self.editing_speed = True
                    self.new_speed = ""
            elif event.type == pygame.KEYDOWN and self.editing_speed:
                if event.key == pygame.K_RETURN:
                    if self.new_speed.isdigit():
                        global SPEED
                        SPEED = int(self.new_speed)
                    self.editing_speed = False
                elif event.key == pygame.K_BACKSPACE:
                    self.new_speed = self.new_speed[:-1]
                else:
                    self.new_speed += event.unicode

        if not self.editing_speed:
            # 2. move
            self._move(action)  # update the head
            self.snake.insert(0, self.head)

            # In tọa độ của đầu rắn và mồi
            print(f"Head: {self.head}, Food: {self.food}")

            # 3. check if game over
            if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
                game_over = True
                reward = -10
            else:
                # 4. place new food or just move
                if self.head == self.food:
                    print(f"Rắn đã ăn mồi! Head: {self.head}, Food: {self.food}")  # In ra tọa độ khi rắn ăn mồi
                    self.score += 1
                    reward = 10
                    self._place_food()
                    self.snake_colors.insert(0, self._get_random_color())
                else:
                    self.snake.pop()
                    self.snake_colors.pop()

            score = self.score

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return reward, game_over, score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        # Kiểm tra va chạm với biên của màn hình
        if pt.x >= self.w or pt.x < 0 or pt.y >= self.h or pt.y < 0:
            return True

        # Kiểm tra va chạm với chính thân rắn
        if pt in self.snake[1:]:
            return True

        return False

    def _update_ui(self):
        self.display.blit(self.background, (0, 0))

        current_time = time.time()
        if current_time - self.last_color_change_time >= 0.5:
            self.snake_colors = [self._get_random_color() for _ in self.snake]
            self.last_color_change_time = current_time

        while len(self.snake_colors) < len(self.snake):
            self.snake_colors.append(self._get_random_color())

        for idx, pt in enumerate(self.snake):
            color = self.snake_colors[idx]
            pygame.draw.rect(self.display, color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render(f"Score: {self.score}  Head: ({self.head.x}, {self.head.y})  Food: ({self.food.x}, {self.food.y})", True, WHITE)
        self.display.blit(text, [0, 0])

        # Thêm dòng hiển thị tốc độ
        speed_text = font.render(f"Speed: {self.new_speed if self.editing_speed else SPEED}", True, RED)
        self.display.blit(speed_text, [self.w - 150, 0])  # Điều chỉnh vị trí nếu cần

        pygame.display.flip()

    def _move(self, action):
        # [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        x, y = self.head
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN: 
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        # Cập nhật tọa độ của đầu rắn đảm bảo là số nguyên và là bội số của BLOCK_SIZE
        self.head = Point((x // BLOCK_SIZE) * BLOCK_SIZE, 
                          (y // BLOCK_SIZE) * BLOCK_SIZE)

import pygame  # Thư viện Pygame, dùng để tạo trò chơi 2D
import random  # Thư viện chuẩn của Python, dùng để tạo số ngẫu nhiên
from enum import Enum  # Thư viện chuẩn của Python, dùng để tạo các kiểu liệt kê
from collections import namedtuple  # Thư viện chuẩn của Python, dùng để tạo các kiểu dữ liệu đơn giản
import time  # Thư viện chuẩn của Python, dùng để làm việc với thời gian
import os  # Thư viện chuẩn của Python, dùng để làm việc với hệ điều hành 

pygame.init()  # Khởi tạo tất cả các mô-đun của Pygame
# Lấy đường dẫn tuyệt đối đến thư mục chứa script
current_dir = os.path.dirname(os.path.abspath(__file__))  # Lấy đường dẫn thư mục hiện tại của tệp
font_path = os.path.join(current_dir, 'BlackOpsOne-Regular.ttf')  # Tạo đường dẫn đến tệp font

font = pygame.font.Font(font_path, 25)  # Tạo font chữ với kích thước 25
# font = pygame.font.SysFont('arial', 25)  # Tạo font chữ hệ thống Arial với kích thước 25

class Direction(Enum):  # Đnh nghĩa kiểu liệt kê cho hướng di chuyển của rắn
    RIGHT = 1  # Hướng sang phải
    LEFT = 2  # Hướng sang trái
    UP = 3  # Hướng lên trên
    DOWN = 4  # Hướng xuống dưới

Point = namedtuple('Point', 'x, y')  # Tạo kiểu dữ liệu đơn giản cho điểm với tọa độ x, y

# Màu sắc RGB
WHITE = (255, 255, 255)  # Màu trắng
RED = (200, 0, 0)  # Màu đỏ
BLUE2 = (0, 100, 255)  # Màu xanh dương nhạt
BLACK = (0, 0, 0)  # Định nghĩa màu đen

BLOCK_SIZE = 20  # Kích thước của mỗi khối trong trò chơi
SPEED = 8  # Tốc độ của trò chơi

class SnakeGame:
    scores = []  # Biến lớp để lưu trữ điểm số

    def __init__(self, display, w=824, h=724):
        self.w = w  # Chiều rộng của cửa sổ trò chơi
        self.h = h  # Chiều cao của cửa sổ trò chơi
        # Khởi tạo hiển thị
        self.display = display  # Sử dụng màn hình được truyền vào thay vì tạo mới
        pygame.display.set_caption('Snake')  # Đặt tiêu đề cửa sổ trò chơi
        self.clock = pygame.time.Clock()  # Tạo đối tượng đồng hồ để điều khiển tốc độ trò chơi
        self.background = pygame.image.load('g.png')  # Tải hình nền cho trò chơi

        # Khởi tạo trạng thái trò chơi
        self.direction = Direction.RIGHT  # Hướng di chuyển ban đầu là sang phải

        self.head = Point(self.w/2, self.h/2)  # Đặt đầu rắn ở giữa màn hình
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),  # Thân rắn ban đầu gồm 3 khối
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0  # Điểm số ban đầu
        self.food = None  # Vị trí mồi ban đầu

        # Thêm bộ đếm thời gian thay đổi màu
        self.last_color_change_time = time.time()  # Thời gian lần cuối thay đổi màu sắc
        self.snake_colors = [self._get_random_color() for _ in self.snake]  # Màu sắc ngẫu nhiên cho từng khối của rắn

        self.paused = False  # {{ Thêm cờ tạm dừng }}

        self.load_scores_from_file()  # Tải điểm số từ tệp

        self.control_mode = 'keyboard'  # Mặc định là chơi bằng bàn phím
        self.toggle_button = pygame.Rect(self.w - 230, 10, 40, 40)  # Kích thước nút gạt

        # Tải hình ảnh biểu tượng
        self.mouse_icon = pygame.image.load('mouse_icon.png').convert_alpha()  # Tải biểu tượng chuột
        self.keyboard_icon = pygame.image.load('keyboard_icon.png').convert_alpha()  # Tải biểu tượng bàn phím

        # Khởi tạo trạng thái mồi đặc biệt
        self.special_food_active = False  # Cho phép đi xuyên tường
        self.invisible_mood_active = False  # Cho phép đi xuyên thân

        # Khởi tạo thông tin cho mồi vô hình
        self.invisible_mood_duration = 15  # Thời gian (giây) cho mồi vô hình
        self.invisible_mood_start_time = None  # Thời gian bắt đầu mồi vô hình

        # Khởi tạo thông tin cho mồi đặc biệt
        self.special_food_duration = 20  # Thời gian (giây) mồi đặc biệt hoạt động
        self.special_food_start_time = None  # Thời gian bắt đầu mồi đặc biệt

        # Danh sách các mồi đặc biệt hiện tại
        self.special_foods = []  # Danh sách chứa thông tin mồi đặc biệt

        # Khởi tạo mồi bình thường
        self.normal_food = None
        self._place_normal_food()  # Đặt mồi bình thường đầu tiên

        # Thêm bộ đếm thời gian để sinh mồi đặc biệt
        self.special_food_spawn_timer = time.time()
        self.special_food_spawn_interval = 15  # Khoảng thời gian (giây) để sinh mồi đặc biệt

        # Khởi tạo thông tin cho mồi ngẫu nhiên
        self.random_food_duration = 10  # Thời gian (giây) mồi ngẫu nhiên tồn tại
        self.random_food_start_time = None  # Thời gian bắt đầu mồi ngẫu nhiên

        # Khởi tạo thông tin cho mồi đa hiệu ứng
        self.multi_effect_food_duration = 10  # Thời gian (giây) mồi đa hiệu ứng tồn tại
        self.multi_effect_food_start_time = None  # Thời gian bắt đầu mồi đa hiệu ứng

        # Biến để lưu trữ thông báo hiện tại
        self.current_message = ""  # Thông báo hiện tại
        self.message_start_time = None  # Thời gian bắt đầu hiển thị thông báo

    def _get_random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Trả về màu sắc ngẫu nhiên


    def _place_normal_food(self):
        """Đặt mồi bình thường ngẫu nhiên trên màn hình."""
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.normal_food = Point(x, y)

        # Đảm bảo mồi không trùng với thân rắn hoặc các mồi đặc biệt
        if self.normal_food in self.snake or any(sf['position'] == self.normal_food for sf in self.special_foods):
            self._place_normal_food()

    def _spawn_special_food(self):
        """Sinh mồi đặc biệt ngẫu nhiên trên màn hình."""
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        position = Point(x, y)

        # Đảm bảo mồi không trùng với thân rắn, mồi bình thường hoặc các mồi đặc biệt khác
        if position in self.snake or position == self.normal_food or any(sf['position'] == position for sf in self.special_foods):
            return  # Không sinh mồi nếu vị trí trùng

        # Xác định loại mồi đặc biệt
        food_type_chance = random.random()
        if food_type_chance < 0.15:
            food_type = 'special'  # 15% khả năng là mồi đặc biệt (đi xuyên tường)
        elif food_type_chance < 0.3:
            food_type = 'invisible'  # 15% khả năng là mồi vô hình (đi xuyên thân)
        elif food_type_chance < 0.45:
            food_type = 'random'  # 15% khả năng là mồi ngẫu nhiên
        elif food_type_chance < 0.60:
            food_type = 'multi_effect'  # 15% khả năng là mồi đa hiệu ứng
        else:
            return  # Không sinh mồi đặc biệt

        # Thêm mồi đặc biệt vào danh sách
        special_food_info = {
            'type': food_type,
            'position': position,
            'start_time': time.time(),    # Ghi nhận thời gian sinh mồi
            'lifetime': 10               # Khoảng thời gian tồn tại trên màn hình (giây)
        }
        self.special_foods.append(special_food_info)

    def play_step(self):
        if not self.paused:
            # 1. Thu thập đầu vào từ người dùng
            for event in pygame.event.get():  # Duyệt qua các sự kiện
                if event.type == pygame.QUIT:  # Kiểm tra sự kiện thoát
                    pygame.quit()  # Thoát Pygame
                    quit()  # Thoát chương trình
                if event.type == pygame.KEYDOWN:
                    # Kiểm tra nếu sự kiện là nhấn phím
                    if self.control_mode == 'keyboard':
                        # Kiểm tra nếu chế độ điều khiển là bàn phím
                        new_direction = self.direction  # Khởi tạo hướng di chuyển mới bằng hướng hiện tại
                        if event.key == pygame.K_LEFT:
                            # Kiểm tra nếu phím nhấn là phím mũi tên trái
                            new_direction = Direction.LEFT  # Đặt hướng di chuyển mới là trái
                        elif event.key == pygame.K_RIGHT:
                            # Kiểm tra nếu phím nhấn là phím mũi tên phải
                            new_direction = Direction.RIGHT  # Đặt hướng di chuyển mới là phải
                        elif event.key == pygame.K_UP:
                            # Kiểm tra nếu phím nhấn là phím mũi tên lên
                            new_direction = Direction.UP  # Đặt hướng di chuyển mới là lên
                        elif event.key == pygame.K_DOWN:
                            # Kiểm tra nếu phím nhấn là phím mũi tên xuống
                            new_direction = Direction.DOWN  # Đặt hướng di chuyển mới là xuống

                        # Kiểm tra nếu hướng mới không phải là ngược lại với hướng hiện tại
                        if not self._is_opposite_direction(new_direction):
                            self.direction = new_direction  # Cập nhật hướng di chuyển của rắn

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Kiểm tra nếu sự kiện là nhấn chuột
                    mouse_pos = event.pos  # Lấy vị trí hiện tại của con trỏ chuột
                    if self.pause_button.collidepoint(mouse_pos):
                        # Kiểm tra nếu vị trí chuột nằm trong vùng của nút tạm dừng
                        action = self.show_pause_menu()  # Hiển thị menu tạm dừng
                        if action == 'menu':
                            # Kiểm tra nếu hành động là 'menu'
                            return True, self.score, 'menu'  # Trả về True, điểm số và 'menu'
                    if self.toggle_button.collidepoint(mouse_pos):
                        # Kiểm tra nếu vị trí chuột nằm trong vùng của nút chuyển đổi chế độ điều khiển
                        self.control_mode = 'mouse' if self.control_mode == 'keyboard' else 'keyboard'  # Chuyển đổi chế độ điều khiển

            # Cập nhật hướng di chuyển dựa trên chế độ điều khiển
            if self.control_mode == 'mouse':
                mouse_pos = pygame.mouse.get_pos()  # Lấy vị trí chuột
                new_direction = self._get_mouse_direction(self.head, mouse_pos)  # Lấy hướng di chuyển từ chuột
                if not self._is_opposite_direction(new_direction):
                    self.direction = new_direction  # Cập nhật hướng di chuyển của rắn

            # Lấy thời gian hiện tại
            current_time = time.time()

            # Cập nhật mồi đặc biệt theo khoảng thời gian
            if current_time - self.special_food_spawn_timer >= self.special_food_spawn_interval:
                self._spawn_special_food()
                self.special_food_spawn_timer = current_time

            # 2. Di chuyển
            self._move(self.direction)  # Cập nhật vị trí đầu rắn
            self.snake.insert(0, self.head)  # Thêm đầu rắn vào danh sách thân rắn
            self.snake_colors.insert(0, self._get_random_color())  # Thêm màu sắc mới cho khối rắn

            # Cập nhật màu sắc của mồi để giống với màu của đầu rắn
            self.food_color = self.snake_colors[0]

            # 3. Kiểm tra nếu game over
            game_over = False  # Khởi tạo biến game_over là False
            if self._is_collision():
                # Kiểm tra va chạm
                game_over = True  # Đặt game_over là True nếu có va chạm
                SnakeGame.scores.append(self.score)  # Lưu điểm số vào biến lớp
                self.save_scores_to_file()  # Lưu điểm số vào tệp khi trò chơi kết thúc

                # Giới hạn số lượng điểm số lưu trữ
                if len(SnakeGame.scores) > 8:
                    SnakeGame.scores.pop(0)  # Xóa điểm số cũ nhất nếu vượt quá 8

                return game_over, self.score, None  # {{ Trả về None cho action khi game_over }}

            # 4. Đặt thức ăn mới hoặc chỉ di chuyển
            if self.head == self.normal_food:
                self.score += 1
                self._place_normal_food()  # Đặt lại mồi bình thường
            else:
                # Kiểm tra xem rắn có ăn mồi đặc biệt nào không
                eaten_special = None
                for special_food in self.special_foods:
                    if self.head == special_food['position']:
                        eaten_special = special_food
                        break

                if eaten_special:
                    self.score += 1
                    if eaten_special['type'] == 'special':
                        self.special_food_active = True  # Kích hoạt khả năng đi xuyên tường
                        self.special_food_start_time = eaten_special['start_time']
                        self.current_message = "Đi xuyên tường!"  # Thông báo
                    elif eaten_special['type'] == 'invisible':
                        self.invisible_mood_active = True  # Kích hoạt khả năng đi xuyên thân
                        self.invisible_mood_start_time = eaten_special['start_time']
                        self.current_message = "Đi xuyên thân!"  # Thông báo
                    elif eaten_special['type'] == 'random':
                        # Xử lý mồi ngẫu nhiên
                        random_effect = random.choice(['shorten', 'lengthen', 'double_lengthen', 'shorten_to_one'])
                        if random_effect == 'shorten':
                            self.snake = self.snake[:len(self.snake)//2]  # Ngắn lại gấp 2
                            self.snake_colors = self.snake_colors[:len(self.snake)]
                            self.current_message = "Ngắn lại gấp 2!"  # Thông báo
                        elif random_effect == 'lengthen':
                            self.snake.append(self.snake[-1])  # Dài ra 1 đoạn
                            self.snake_colors.append(self._get_random_color())
                            self.current_message = "Dài ra 1 đoạn!"  # Thông báo
                        elif random_effect == 'double_lengthen':
                            self.snake.extend([self.snake[-1]] * len(self.snake))  # Dài ra gấp 2
                            self.snake_colors.extend([self._get_random_color() for _ in range(len(self.snake))])
                            self.current_message = "Dài ra gấp 2!"  # Thông báo
                        elif random_effect == 'shorten_to_one':
                            self.snake = [self.head]  # Ngắn lại chỉ còn 1 đốm
                            self.snake_colors = [self._get_random_color()]
                            self.current_message = "Ngắn lại chỉ còn 1 đốm!"  # Thông báo
                    elif eaten_special['type'] == 'multi_effect':
                        # Xử lý mồi đa hiệu ứng
                        effects = random.sample(['special', 'invisible', 'random'], k=random.randint(1, 3))
                        messages = []
                        for effect in effects:
                            if effect == 'special':
                                self.special_food_active = True
                                self.special_food_start_time = current_time
                                messages.append("Đi xuyên tường")
                            elif effect == 'invisible':
                                self.invisible_mood_active = True
                                self.invisible_mood_start_time = current_time
                                messages.append("Đi xuyên thân")
                            elif effect == 'random':
                                random_effect = random.choice(['shorten', 'lengthen', 'double_lengthen', 'shorten_to_one'])
                                if random_effect == 'shorten':
                                    self.snake = self.snake[:len(self.snake)//2]
                                    self.snake_colors = self.snake_colors[:len(self.snake)]
                                    messages.append("Ngắn lại gấp 2")
                                elif random_effect == 'lengthen':
                                    self.snake.append(self.snake[-1])
                                    self.snake_colors.append(self._get_random_color())
                                    messages.append("Dài ra 1 đoạn")
                                elif random_effect == 'double_lengthen':
                                    self.snake.extend([self.snake[-1]] * len(self.snake))
                                    self.snake_colors.extend([self._get_random_color() for _ in range(len(self.snake))])
                                    messages.append("Dài ra gấp 2")
                                elif random_effect == 'shorten_to_one':
                                    self.snake = [self.head]
                                    self.snake_colors = [self._get_random_color()]
                                    messages.append("Ngắn lại chỉ còn 1 đốm")
                    self.message_start_time = current_time  # Ghi nhận thời gian bắt đầu hiển thị thông báo
                    self.special_foods.remove(eaten_special)  # Loại bỏ mồi đặc biệt đã ăn
                else:
                    self.snake.pop()
                    self.snake_colors.pop()

            # Quản lý thời gian tồn tại của các mồi đặc biệt
            for special_food in self.special_foods.copy():
                elapsed_time = current_time - special_food['start_time']
                if elapsed_time >= special_food['lifetime']:
                    self.special_foods.remove(special_food)  # Loại bỏ mồi đặc biệt đã hết thời gian

            # Quản lý thời gian cho mồi đặc biệt
            if self.special_food_active:
                elapsed_time = current_time - self.special_food_start_time
                if elapsed_time >= self.special_food_duration:
                    self.special_food_active = False  # Tắt khả năng đặc biệt khi hết thời gian

            # Quản lý thời gian cho mồi vô hình
            if self.invisible_mood_active:
                elapsed_time = current_time - self.invisible_mood_start_time
                if elapsed_time >= self.invisible_mood_duration:
                    self.invisible_mood_active = False  # Tắt khả năng vô hình khi hết thời gian

            # Xóa thông báo sau 3.5 giây
            if self.current_message and current_time - self.message_start_time > 3.5:
                self.current_message = ""  # Xóa thông báo

            # 5. Cập nhật giao diện hiển thị
            self._update_ui()  # Cập nhật giao diện người dùng
            self.clock.tick(SPEED)  # Điều chỉnh tốc độ trò chơi

            # 6. Trả về game_over và score
            return False, self.score, None  # {{ Trả về None cho action khi không game_over }}
        else:
            # {{ Nếu đang tạm dừng, không tiến hành bước chơi nào }}
            return False, self.score, None

    def _is_collision(self):
        # Bỏ qua kiểm tra va chạm với biên nếu mồi đặc biệt đang hoạt động
        if not self.special_food_active:
            # chạm biên
            if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
                return True  # Trả về True nếu có va chạm với biên

        # Bỏ qua kiểm tra va chạm với thân rắn nếu mồi vô hình đang hoạt động
        if not self.invisible_mood_active:
            # chạm chính nó
            if self.head in self.snake[1:]:
                return True  # Trả về True nếu có va chạm với thân rắn

        return False  # Trả về False nếu không có va chạm

    def _update_ui(self):
        self.display.blit(self.background, (0, 0))  # Vẽ hình nền lên màn hình

        while len(self.snake_colors) < len(self.snake):  # Đảm bảo số lượng màu sắc bằng số lượng khối rắn
            self.snake_colors.append(self._get_random_color())  # Thêm màu sắc ngẫu nhiên

        for idx, pt in enumerate(self.snake):  # Duyệt qua từng khối của rắn
            color = self.snake_colors[idx]  # Lấy màu sắc tương ứng
            pygame.draw.rect(self.display, color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))  # Vẽ khối rắn
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))  # Vẽ viền cho khối rắn

        # Vẽ mồi bình thường
        pygame.draw.rect(self.display, self._get_food_color(self.normal_food), pygame.Rect(self.normal_food.x, self.normal_food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Vẽ tất cả các mồi đặc biệt
        for special_food in self.special_foods:
            special_color = self._get_food_color(special_food['position'], special=True, type=special_food['type'])
            pygame.draw.rect(self.display, special_color, pygame.Rect(special_food['position'].x, special_food['position'].y, BLOCK_SIZE, BLOCK_SIZE))

            # Thêm thanh thời gian tồn tại cho mỗi mồi đặc biệt
            remaining_time = max(0, special_food['lifetime'] - (time.time() - special_food['start_time']))
            # Vẽ thanh tiến trình dưới mỗi mồi đặc biệt
            bar_width, bar_height = BLOCK_SIZE, 5
            bar_x = special_food['position'].x
            bar_y = special_food['position'].y + BLOCK_SIZE + 2  # Vẽ thanh ngay dưới mồi
            fill_width = (remaining_time / special_food['lifetime']) * bar_width

            # Vẽ nền thanh tiến trình
            pygame.draw.rect(self.display, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))  # Nền trắng

            # Vẽ phần đã đi
            pygame.draw.rect(self.display, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))  # Màu xanh lá cây

            # Vẽ viền thanh tiến trình
            pygame.draw.rect(self.display, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)  # Viền đen

        # Hiển thị thông báo hiện tại
        if self.current_message:
            message_text = font.render(self.current_message, True, RED)  # Tạo văn bản thông báo với màu đỏ
            self.display.blit(message_text, (10, self.h - 40))  # Vẽ thông báo ở góc dưới bên trái

        # {{ Thêm thanh thời gian cho mồi đặc biệt (đi xuyên tường) }}
        if self.special_food_active:
            remaining_time = max(0, self.special_food_duration - (time.time() - self.special_food_start_time))
            # Vẽ thanh tiến trình màu xanh lá cây sáng
            bar_width, bar_height = 200, 20
            bar_x, bar_y = 10, 50
            fill_width = (remaining_time / self.special_food_duration) * bar_width
            # Vẽ nền thanh tiến trình
            pygame.draw.rect(self.display, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))  # Nền trắng
            # Vẽ phần đã đi
            pygame.draw.rect(self.display, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))  # Màu xanh lá cây
            # Vẽ viền thanh tiến trình
            pygame.draw.rect(self.display, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)  # Viền đen
            # Vẽ thời gian còn lại
            timer_text = font.render(f"Đặc Biệt: {int(remaining_time)}s", True, (0, 0, 0))
            self.display.blit(timer_text, (bar_x, bar_y - 25))

        # {{ Thêm thanh thời gian cho mồi vô hình }}
        if self.invisible_mood_active:
            remaining_time = max(0, self.invisible_mood_duration - (time.time() - self.invisible_mood_start_time))
            # Vẽ thanh tiến trình màu xanh lá cây sáng
            bar_width, bar_height = 200, 20
            bar_x, bar_y = 10, 80
            fill_width = (remaining_time / self.invisible_mood_duration) * bar_width
            # Vẽ nền thanh tiến trình
            pygame.draw.rect(self.display, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))  # Nền trắng
            # Vẽ phần đã đi
            pygame.draw.rect(self.display, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))  # Màu xanh lá cây
            # Vẽ viền thanh tiến trình
            pygame.draw.rect(self.display, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)  # Viền đen
            # Vẽ thời gian còn lại
            timer_text = font.render(f"Vô Hình: {int(remaining_time)}s", True, (0, 0, 0))
            self.display.blit(timer_text, (bar_x, bar_y - 25))

        # {{ Thay thế nút "Tạm dừng" bằng hình ảnh "nut.png" }}
        try:
            pause_image = pygame.image.load('nut.png').convert_alpha()  # Tải hình ảnh với hỗ trợ chuyển đổi alpha
            pause_image = pygame.transform.scale(pause_image, (100, 40))  # Điều chỉnh kích thước nếu cần
        except pygame.error as e:
            print(f"Không thể tải hình ảnh 'nut.png': {e}")
            # Nếu không thể tải hình ảnh, vẽ nút "Tạm dừng" bằng hình chữ nhật như trước
            button_width, button_height = 100, 40  # Đặt kích thước cho nút "Tạm dừng"
            button_x, button_y = self.w - button_width - 10, 10  # Tính toán vị trí của nút "Tạm dừng" trên màn hình
            self.pause_button = pygame.Rect(button_x, button_y, button_width, button_height)  # Tạo một hình chữ nhật đại diện cho nút "Tạm dừng"
            pygame.draw.rect(self.display, (180, 180, 180), self.pause_button, border_radius=5)  # Vẽ nút "Tạm dừng" với màu xám và bo góc
            pause_text = font.render("Tạm dừng", True, (179, 74, 70))  # Tạo văn bản "Tạm dừng" với màu nâu đỏ nhạt
            self.display.blit(
                pause_text,
                (
                    self.pause_button.x + (button_width - pause_text.get_width()) // 2,  # Căn giữa văn bản theo chiều ngang
                    self.pause_button.y + (button_height - pause_text.get_height()) // 2  # Căn giữa văn bản theo chiều dọc
                )
            )
        else:
            # Hiển thị hình ảnh "nut.png" tại vị trí nút "Tạm dừng"
            button_width, button_height = pause_image.get_size()  # Lấy kích thước của hình ảnh "nut.png"
            button_x, button_y = self.w - button_width - 10, 10  # Tính toán vị trí của hình ảnh trên màn hình
            self.pause_button = pygame.Rect(button_x, button_y, button_width, button_height)  # Tạo một hình chữ nhật đại diện cho nút "Tạm dừng"
            self.display.blit(pause_image, (button_x, button_y))  # Vẽ hình ảnh "nut.png" lên màn hình tại vị trí đã tính toán

        text = font.render(f"Score: {self.score}", True, WHITE)  # Tạo văn bản hiển thị điểm số với màu trắng
        self.display.blit(text, [0, 0])  # Vẽ văn bản điểm số lên góc trên bên trái của màn hình

        # Hiển thị biểu tượng điều khiển
        if self.control_mode == 'mouse':
            self.display.blit(self.mouse_icon, self.toggle_button.topleft)  # Hiển thị biểu tượng chuột nếu chế độ điều khiển là chuột
        else:
            self.display.blit(self.keyboard_icon, self.toggle_button.topleft)  # Hiển thị biểu tượng bàn phím nếu chế độ điều khiển là bàn phím

        pygame.display.flip()  # Cập nhật toàn bộ màn hình để hiển thị các thay đổi

    def show_pause_menu(self):
        self.paused = True  # Đặt cờ tạm dừng trò chơi

        # Vẽ nền trắng mờ để làm nổi bật menu tạm dừng
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 150))  # Đặt màu trắng với độ trong suốt 150
        self.display.blit(overlay, (0, 0))  # Vẽ lớp phủ lên toàn bộ màn hình

        # Tạo bảng popup cho menu tạm dừng
        popup_width, popup_height = 400, 300  # Đặt kích thước cho bảng popup
        popup_rect = pygame.Rect(
            (self.w - popup_width) // 2,  # Căn giữa bảng popup theo chiều ngang
            (self.h - popup_height) // 2,  # Căn giữa bảng popup theo chiều dọc
            popup_width,
            popup_height
        )
        pygame.draw.rect(self.display, WHITE, popup_rect, border_radius=10)  # Vẽ bảng popup với màu trắng và bo góc

        # Tiêu đề của popup
        popup_title = font.render("Trò chơi tạm dừng", True, (204, 106, 106))  # Tạo văn bản tiêu đề với màu đỏ nhạt
        self.display.blit(
            popup_title,
            (
                popup_rect.x + (popup_rect.width - popup_title.get_width()) // 2,  # Căn giữa tiêu đề theo chiều ngang
                popup_rect.y + 30  # Đặt tiêu đề cách đỉnh popup 30 pixel
            )
        )

        # Nút "Chơi tiếp" để tiếp tục trò chơi
        button_width, button_height = 200, 50  # Đặt kích thước cho nút
        continue_button = pygame.Rect(
            (self.w - button_width) // 2,  # Căn giữa nút theo chiều ngang
            popup_rect.y + 100,  # Đặt nút cách đỉnh popup 100 pixel
            button_width,
            button_height
        )
        pygame.draw.rect(self.display, (255, 223, 186), continue_button, border_radius=10)  # Vẽ nút với màu cam nhạt và bo góc
        continue_text = font.render("Chơi tiếp", True, (179, 74, 70))  # Tạo văn bản "Chơi tiếp" với màu nâu đỏ nhạt
        self.display.blit(
            continue_text,
            (
                continue_button.x + (button_width - continue_text.get_width()) // 2,  # Căn giữa văn bản theo chiều ngang
                continue_button.y + (button_height - continue_text.get_height()) // 2  # Căn giữa văn bản theo chiều dọc
            )
        )

        # Nút "Về menu" để quay lại menu chính
        menu_button = pygame.Rect(
            (self.w - button_width) // 2,  # Căn giữa nút theo chiều ngang
            popup_rect.y + 180,  # Đặt nút cách đỉnh popup 180 pixel
            button_width,
            button_height
        )
        pygame.draw.rect(self.display, (255, 223, 186), menu_button, border_radius=10)  # Vẽ nút với màu cam nhạt và bo góc
        menu_text = font.render("Về menu", True, (179, 74, 70))  # Tạo văn bản "Về menu" với màu nâu đỏ nhạt
        self.display.blit(
            menu_text,
            (
                menu_button.x + (button_width - menu_text.get_width()) // 2,  # Căn giữa văn bản theo chiều ngang
                menu_button.y + (button_height - menu_text.get_height()) // 2  # Căn giữa văn bản theo chiều dọc
            )
        )

        pygame.display.flip()  # Cập nhật toàn bộ màn hình để hiển thị các thay đổi

        # Vòng lặp chờ cho đến khi người chơi nhấn nút
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if continue_button.collidepoint(mouse_pos):
                        self.paused = False  # Tiếp tục trò chơi
                        waiting = False
                    elif menu_button.collidepoint(mouse_pos):
                        self.paused = False  # Tiếp tục trò chơi
                        return 'menu'  # Quay lại menu chính

    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        # {{ Chỉnh sửa cơ chế đi xuyên tường theo thời gian }}
        if self.special_food_active:
            # Cho phép đi xuyên qua biên mà không cần đặt lại sau mỗi lần
            x = x % self.w
            y = y % self.h

        self.head = Point(round(x // BLOCK_SIZE) * BLOCK_SIZE, round(y // BLOCK_SIZE) * BLOCK_SIZE)

    def show_scores(self):
        # Sử dụng nền OIG3.jpg thay vì lấp đầy màn hình bằng màu đen
        self.display.blit(pygame.image.load('OIG3.jpg'), (0, 0))  # Sử dụng nn OIG3.jpg

        # Tạo một bề mặt cho bảng điểm với nền màu trắng trong suốt
        score_panel = pygame.Surface((self.w * 0.8, self.h * 0.6), pygame.SRCALPHA)  # Tạo bề mặt với kích thước 80% chiều rộng và 60% chiều cao của màn hình, hỗ trợ độ trong suốt
        score_panel.fill((255, 255, 255, 90))  # Điền màu trắng với độ trong suốt 90

        # Vị trí của bảng điểm trên màn hình (đã nhích lên một chút)
        panel_rect = score_panel.get_rect(center=(self.w // 2, self.h // 2 - 30))  # Đặt bảng điểm ở giữa màn hình, nhích lên 30 pixel
        self.display.blit(score_panel, panel_rect)  # Vẽ bảng điểm lên màn hình

        # Tiêu đề bảng điểm
        title_font = pygame.font.Font(font_path, 50)  # Tạo font chữ với kích thước 50
        title_text = title_font.render("BẢNG ĐIỂM", True, (204, 106, 106))  # Tạo văn bản tiêu đề với màu đỏ nhạt
        self.display.blit(title_text, (self.w // 2 - title_text.get_width() // 2, self.h * 0.1))  # Vẽ tiêu đề lên màn hình, căn giữa và nhích lên 10% chiều cao

        # Hiển thị danh sách điểm số
        score_font = pygame.font.Font(font_path, 30)  # Tạo font chữ với kích thước 30 cho điểm số
        for idx, score in enumerate(SnakeGame.scores[-8:], 1):  # Duyệt qua tối đa 8 điểm số gần nhất
            score_text = score_font.render(f"Ván Số {idx}: {' ' * 56} {score}", True, (204, 106, 106))  # Tạo văn bản điểm số với màu đỏ nhạt
            self.display.blit(score_text, (self.w // 2 - score_text.get_width() // 2, self.h * 0.2 + idx * 40))  # Vẽ điểm số lên màn hình, căn giữa và giảm khoảng cch

        # Tạo nút "Chơi lại" và "Về menu" nằm theo hàng ngang
        button_width = 180  # Đặt chiều rộng cho nút
        button_height = 50  # Đặt chiều cao cho nút
        button_spacing = 40  # Khoảng cách giữa các nút

        # Vị trí của nút "Chơi lại"
        replay_button = pygame.Rect(self.w // 2 - button_width - button_spacing // 2, self.h * 0.75, button_width, button_height)  # Tạo hình chữ nhật cho nút "Chơi lại"
        pygame.draw.rect(self.display, (255, 223, 186), replay_button, border_radius=10)  # Vẽ nút "Chơi lại" với màu cam nhạt và bo góc
        replay_text = font.render("Chơi lại", True, (179, 74, 70))  # Tạo văn bản "Chơi lại" với màu nâu đỏ nhạt
        self.display.blit(
            replay_text,
            (
                replay_button.x + replay_button.width // 2 - replay_text.get_width() // 2,  # Căn giữa văn bản theo chiều ngang
                replay_button.y + (button_height - replay_text.get_height()) // 2  # Căn giữa văn bản theo chiều dọc
            )
        )

        # Vị trí của nút "Về menu"
        menu_button = pygame.Rect(self.w // 2 + button_spacing // 2, self.h * 0.75, button_width, button_height)  # Tạo hình chữ nhật cho nút "Về menu"
        pygame.draw.rect(self.display, (255, 223, 186), menu_button, border_radius=10)  # Vẽ nút "Về menu" với màu cam nhạt và bo góc
        menu_text = font.render("Về menu", True, (179, 74, 70))  # Tạo văn bản "Về menu" với màu nâu đỏ nhạt
        self.display.blit(
            menu_text,
            (
                menu_button.x + menu_button.width // 2 - menu_text.get_width() // 2,  # Căn giữa văn bản theo chiều ngang
                menu_button.y + (button_height - menu_text.get_height()) // 2  # Căn giữa văn bản theo chiều dọc
            )
        )

        pygame.display.flip()  # Cập nhật toàn bộ màn hình để hiển thị các thay đổi

        # Chờ cho đến khi người chơi nhấn nút
        waiting = True  # Đặt cờ chờ để duy trì vòng lặp cho đến khi người chơi nhấn nút
        while waiting:
            for event in pygame.event.get():  # Duyệt qua tất cả các sự kiện trong hàng đợi sự kiện
                if event.type == pygame.QUIT:  # Kiểm tra nếu sự kiện là thoát chương trình
                    pygame.quit()  # Thoát khỏi Pygame
                    quit()  # Thoát khỏi chương trình
                if event.type == pygame.MOUSEBUTTONDOWN:  # Kiểm tra nếu sự kiện là nhấn chuột
                    mouse_pos = event.pos  # Lấy vị trí hiện tại của con trỏ chuột
                    if replay_button.collidepoint(mouse_pos):  # Kiểm tra nếu vị trí chuột nằm trong vùng của nút "Chơi lại"
                        waiting = False  # Đặt cờ chờ thành False để thoát khỏi vòng lặp
                        return 'replay'  # Trả về hành động 'replay'
                    elif menu_button.collidepoint(mouse_pos):  # Nếu nhấn vào nút "Về menu"
                        waiting = False  # Thoát khỏi vòng lặp chờ
                        return 'menu'  # Trả về hành động 'menu'

    def reset(self):
        """Khôi phục trạng thái ban đầu của trò chơi."""
        self.direction = Direction.RIGHT  # Hướng di chuyển ban đầu là sang phải
        self.head = Point(self.w / 2, self.h / 2)  # Đặt đầu rắn ở giữa màn hình
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),  # Thân rắn ban đầu gồm 3 khối head, với 2 cái trong [ ]
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]
        self.score = 0  # Điểm số ban đầu
        self.food = None  # Vị trí mồi ban đầu
        self._place_normal_food()  # Đặt mồi ngẫu nhiên trên màn hình
        self.snake_colors = [self._get_random_color() for _ in self.snake]  # Màu sắc ngẫu nhiên cho từng khối của rắn

    def show_game_over(self):
        """Hiển thị màn hình kết thúc trò chơi."""
        try:
            game_over_background = pygame.image.load('game_over_background.png')  # Tải hình nền game over
            game_over_background = pygame.transform.scale(game_over_background, (self.w, self.h))  # Điều chỉnh kích thước hình nền
            self.display.blit(game_over_background, (0, 0))  # Vẽ hình nền lên màn hình
        except pygame.error as e:
            print(f"Không thể tải hình ảnh 'game_over_background.png': {e}")  # Thông báo lỗi nếu không thể tải hình ảnh
            self.display.fill(BLACK)  # Nếu không thể tải hình ảnh, lấp đầy màn hình bằng màu đen

        # Tạo nút 'Next' với màu vàng sáng hơn và căn chỉnh vị trí, kích thước
        button_width, button_height = 200, 60  # Tăng kích thước nút
        next_button = pygame.Rect(
            self.w // 2 - button_width // 2,  # Căn giữa theo chiều ngang
            self.h * 0.6,  # Nhích lên cao hơn (60% chiều cao màn hình)
            button_width, button_height
        )

        # Vẽ nút 'Next' với màu vàng sáng (giống màu đám mây) và bo góc mềm mại
        pygame.draw.rect(self.display, (255, 243, 176), next_button, border_radius=20)  # Màu vàng sáng
        next_text = font.render("Next", True, (179, 74, 70))  # Văn bản với màu nâu đỏ nhạt
        self.display.blit(
            next_text,
            (
                next_button.x + (button_width - next_text.get_width()) // 2,  # Căn giữa văn bản theo chiều ngang
                next_button.y + (button_height - next_text.get_height()) // 2  # Căn giữa văn bản theo chiều dọc
            )
        )

        pygame.display.flip()  # Cập nhật toàn bộ màn hình

        # Chờ cho đến khi người chơi nhấn nút 'Next'
        waiting = True  # Đặt cờ chờ để duy trì vòng lặp cho đến khi người chơi nhấn nút
        while waiting:
            for event in pygame.event.get():  # Duyệt qua tất cả các sự kiện trong hàng đợi sự kiện
                if event.type == pygame.QUIT:  # Kiểm tra nếu sự kiện là thoát chương trình
                    pygame.quit()  # Thoát khỏi Pygame
                    quit()  # Thoát khỏi chương trình
                if event.type == pygame.MOUSEBUTTONDOWN:  # Kiểm tra nếu sự kiện là nhấn chuột
                    mouse_pos = event.pos  # Lấy vị trí hiện tại của con trỏ chuột
                    if next_button.collidepoint(mouse_pos):  # Kiểm tra nếu vị trí chuột nằm trong vùng của nút 'Next'
                        waiting = False  # Đặt cờ chờ thành False để thoát khỏi vòng lặp

    def save_scores_to_file(self, filename='scores.txt'):
        """Lưu điểm số vào tệp."""
        with open(filename, 'w') as file:  # Mở tệp để ghi
            for score in SnakeGame.scores:  # Duyệt qua từng điểm số
                file.write(f"{score}\n")  # Ghi điểm s vào tệp

    def load_scores_from_file(self, filename='scores.txt'):
        """Tải điểm số từ tệp."""
        if os.path.exists(filename):  # Kiểm tra nếu tệp tồn tại
            with open(filename, 'r') as file:  # M tệp để đọc
                SnakeGame.scores = [int(line.strip()) for line in file.readlines()]  # Đọc điểm số từ tệp

    def _get_mouse_direction(self, snake_head, mouse_pos):
        """Xác định hướng di chuyển dựa trên vị trí chuột."""
        x_diff = mouse_pos[0] - snake_head.x  # Tính độ chênh lệch x giữa chuột và đu rắn
        y_diff = mouse_pos[1] - snake_head.y  # Tính độ chênh lệch y giữa chuột và đầu rắn
        
        if abs(x_diff) > abs(y_diff):  # Kiểm tra nếu độ chênh lệch x lớn hơn y
            if x_diff > 0:
                return Direction.RIGHT  # Trả về hướng phải
            else:
                return Direction.LEFT  # Trả về hướng trái
        else:
            if y_diff > 0:
                return Direction.DOWN  # Trả về hướng xuống
            else:
                return Direction.UP  # Trả về hướng lên

    def _is_opposite_direction(self, new_direction):
        """Kiểm tra nếu hướng mới là ngược lại với hướng hiện tại."""
        # Kiểm tra nếu hướng hiện tại là trái và hướng mới là phải
        if (self.direction == Direction.LEFT and new_direction == Direction.RIGHT):
            # Kiểm tra nếu hướng hiện tại là trái và hướng mới là phải
            return True  # Trả về True nếu hướng mới là ngược lại
        elif (self.direction == Direction.RIGHT and new_direction == Direction.LEFT):
            # Kiểm tra nếu hướng hiện tại là phải và hướng mới là trái
            return True  # Trả về True nếu hướng mới là ngược lại
        elif (self.direction == Direction.UP and new_direction == Direction.DOWN):
            # Kiểm tra nếu hướng hiện tại là lên và hướng mới là xuống
            return True  # Trả về True nếu hướng mới là ngược lại
        elif (self.direction == Direction.DOWN and new_direction == Direction.UP):
            # Kiểm tra nếu hướng hiện tại là xuống và hướng mới là lên
            return True  # Trả về True nếu hướng mới là ngược lại
        return False  # Trả về False nếu không phải là ngược lại

    def _get_food_color(self, position, special=False, type=None):
        """Xác định màu sắc của mồi dựa trên loại mồi."""
        if special:
            if type == 'special':
                return (255, 223, 0)  # Màu vàng cho mồi đặc biệt
            elif type == 'invisible':
                return (128, 0, 128)  # Màu tím cho mồi vô hình
            elif type == 'random':
                return (0, 255, 255)  # Màu xanh ngọc cho mồi ngẫu nhiên
            elif type == 'multi_effect':
                return (255, 165, 0)  # Màu cam cho mồi đa hiệu ứng
        else:
            return self.snake_colors[0]  # Màu của đầu rắn cho mồi bình thường

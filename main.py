import pygame
import sys
import math

# -------------------------- 常量配置 --------------------------
WIDTH = 700
HEIGHT = 750
FPS = 60
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
GREEN = (30, 180, 60)
BLUE = (30, 80, 200)
ORANGE = (255, 140, 0)
CELL_SIZE = 80
MARGIN = 10

# 方向 Unicode 箭头
DIR_VEC = {
    "\u2191": (0, -1),
    "\u2193": (0, 1),
    "\u2190": (-1, 0),
    "\u2192": (1, 0)
}

# ========== 这里是你给的新关卡 ==========
LEVELS = [
    # 关卡1 4x4
    {
        "size": 4,
        "max_mistake": 3,
        "map": [
            ["", "→", "", ""],
            ["↑", "", "", "↓"],
            ["", "", "", ""],
            ["", "", "←", ""]
        ]
    },
    # 关卡2 5x5
    {
        "size": 5,
        "max_mistake": 3,
        "map": [
            ["→", "↓", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", "↓", ""],
            ["", "→", "", "", "↑"]
        ]
    },
    # 关卡3 5x5
    {
        "size": 5,
        "max_mistake": 3,
        "map": [
            ["→", "", "", "", "↓"],
            ["", "", "", "", ""],
            ["↑", "", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", "←", ""]
        ]
    },
    # 关卡4【新增嵌套关卡】，箭头多，必须按固定顺序消除
    {
        "size": 6,
        "max_mistake": 4,
        "map": [
            ["→", "", "", "", "", "↑"],
            ["", "", "", "", "", ""],
            ["", "↓", "←", "", "", ""],
            ["", "", "", "↑", "", ""],
            ["", "", "", "", "", ""],
            ["", "→", "", "", "", "↓"]
        ]
    },
    # 关卡5【最终嵌套关卡】，最多箭头，强嵌套，解法唯一
    {
        "size": 6,
        "max_mistake": 4,
        "map": [
            ["", "", "→", "", "", "↑"],
            ["", "", "↑", "", "↓", "←"],
            ["", "", "", "", "", ""],
            ["", "", "↓", "", "←", ""],
            ["", "", "", "", "", ""],
            ["", "", "→", "", "", "↓"]
        ]
    }
]


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()

        self.font_big = pygame.font.SysFont("Microsoft YaHei", 48)
        self.font_mid = pygame.font.SysFont("Microsoft YaHei", 28)
        self.font_small = pygame.font.SysFont("Microsoft YaHei", 22)

        self.state = "start"
        self.current_level_idx = 0
        self.unlocked_levels = {0}
        self.mistake_left = 3
        self.arrows = []
        self.animating = False
        self.anim_timer = 0
        self.anim_type = None
        self.anim_target = None

        self.offset_x = 0
        self.offset_y = 0
        self.level_btns = []

        # 加载背景图
        self.bg_img = pygame.image.load("images/bg.png").convert()
        self.bg_img = pygame.transform.scale(self.bg_img, (WIDTH, HEIGHT))

        # 加载按钮图片
        self.btn_start = pygame.image.load("images/btn_start.png").convert_alpha()
        self.btn_restart = pygame.image.load("images/btn_restart.png").convert_alpha()
        self.btn_setting = pygame.image.load("images/btn_setting.png").convert_alpha()
        self.btn_level_select = pygame.image.load("images/btn_level_select.png").convert_alpha()
        self.btn_exit = pygame.image.load("images/btn_exit.png").convert_alpha()
        self.btn_back = pygame.image.load("images/btn_back.png").convert_alpha()
        self.btn_next_level = pygame.image.load("images/btn_next_level.png").convert_alpha()
        self.btn_replay = pygame.image.load("images/btn_replay.png").convert_alpha()

        # 缩放按钮
        self.btn_start = pygame.transform.scale(self.btn_start, (200, 60))
        self.btn_restart = pygame.transform.scale(self.btn_restart, (140, 40))
        self.btn_setting = pygame.transform.scale(self.btn_setting, (120, 40))
        self.btn_level_select = pygame.transform.scale(self.btn_level_select, (140, 48))
        self.btn_exit = pygame.transform.scale(self.btn_exit, (140, 48))
        self.btn_back = pygame.transform.scale(self.btn_back, (160, 50))
        self.btn_next_level = pygame.transform.scale(self.btn_next_level, (130, 48))
        self.btn_replay = pygame.transform.scale(self.btn_replay, (130, 48))

        # 顶部按钮碰撞区域
        self.restart_rect = pygame.Rect(520, 8, 140, 40)
        self.setting_rect = pygame.Rect(370, 8, 120, 40)

        # 弹窗按钮位置
        self.btn_next_rect = None
        self.btn_replay_rect = None
        self.btn_select_rect = None
        self.btn_exit_rect = None
        self.btn_back_rect = None

    def load_level(self, level_idx=None):
        if level_idx is not None:
            self.current_level_idx = level_idx
        lv = LEVELS[self.current_level_idx]
        self.mistake_left = lv["max_mistake"]
        self.arrows = []
        size = lv["size"]
        for y in range(size):
            for x in range(size):
                d = lv["map"][y][x]
                if d != "":
                    self.arrows.append({"x": x, "y": y, "dir": d})
        self.animating = False
        self.anim_timer = 0
        self.anim_type = None
        self.anim_target = None
        self.offset_x = (WIDTH - size * CELL_SIZE) // 2
        self.offset_y = 80

    def check_block(self, x, y, direction):
        dx, dy = DIR_VEC[direction]
        cx = x + dx
        cy = y + dy
        board_size = LEVELS[self.current_level_idx]["size"]
        while 0 <= cx < board_size and 0 <= cy < board_size:
            for arr in self.arrows:
                if arr["x"] == cx and arr["y"] == cy:
                    return True
            cx += dx
            cy += dy
        return False

    def draw_start_screen(self):
        self.screen.blit(self.bg_img, (0, 0))

        title = self.font_big.render("一箭又一箭", True, DARK_GRAY)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        text1 = self.font_mid.render("点击箭头，让它朝指向飞出棋盘", True, DARK_GRAY)
        text2 = self.font_mid.render("前方有箭头阻挡会消耗失误次数", True, DARK_GRAY)
        text3 = self.font_mid.render("清空所有箭头通关，失误用完失败", True, DARK_GRAY)
        self.screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, 220))
        self.screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, 270))
        self.screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, 320))

        start_rect = self.btn_start.get_rect(center=(WIDTH // 2, 440))
        self.screen.blit(self.btn_start, start_rect)
        return start_rect

    def draw_game_screen(self):
        self.screen.blit(self.bg_img, (0, 0))

        lv = LEVELS[self.current_level_idx]
        board_size = lv["size"]

        info1 = self.font_small.render(f"关卡：{self.current_level_idx + 1}", True, DARK_GRAY)
        info2 = self.font_small.render(f"剩余箭头：{len(self.arrows)}", True, DARK_GRAY)
        info3 = self.font_small.render(f"剩余失误：{self.mistake_left}", True, RED)
        self.screen.blit(info1, (20, 12))
        self.screen.blit(info2, (160, 12))
        self.screen.blit(info3, (320, 12))

        self.screen.blit(self.btn_setting, self.setting_rect)
        self.screen.blit(self.btn_restart, self.restart_rect)

        for y in range(board_size):
            for x in range(board_size):
                rect = pygame.Rect(
                    self.offset_x + x * CELL_SIZE,
                    self.offset_y + y * CELL_SIZE,
                    CELL_SIZE - MARGIN,
                    CELL_SIZE - MARGIN
                )
                pygame.draw.rect(self.screen, GRAY, rect, border_radius=4)

        for arr in self.arrows:
            ax, ay = arr["x"], arr["y"]
            rect = pygame.Rect(
                self.offset_x + ax * CELL_SIZE,
                self.offset_y + ay * CELL_SIZE,
                CELL_SIZE - MARGIN,
                CELL_SIZE - MARGIN
            )
            color = BLACK

            if self.animating and self.anim_type == "bump" and self.anim_target == arr:
                shake = int(math.sin(self.anim_timer * 0.3) * 6)
                rect.x += shake
                color = RED

            if self.animating and self.anim_type == "fly" and self.anim_target == arr:
                dx, dy = DIR_VEC[arr["dir"]]
                rect.x += dx * self.anim_timer * 3
                rect.y += dy * self.anim_timer * 3
                color = (100, 100, 100)

            text = self.font_big.render(arr["dir"], True, color)
            self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def draw_setting_panel(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(180, 220, 340, 260)
        pygame.draw.rect(self.screen, WHITE, panel_rect, border_radius=12)

        title = self.font_big.render("设置", True, DARK_GRAY)
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 30))

        btn_level_rect = pygame.Rect(200, 300, 300, 60)
        btn_exit_rect = pygame.Rect(200, 380, 300, 60)

        self.screen.blit(self.btn_level_select, btn_level_rect)
        self.screen.blit(self.btn_exit, btn_exit_rect)

        return btn_level_rect, btn_exit_rect

    def draw_modal(self, is_win):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        box_rect = pygame.Rect(100, 160, 500, 340)
        pygame.draw.rect(self.screen, WHITE, box_rect, border_radius=12)

        is_all_clear = is_win and (self.current_level_idx == len(LEVELS) - 1)

        if is_all_clear:
            title = self.font_big.render("恭喜！通关所有关卡！", True, GREEN)
            msg = self.font_mid.render("你完成全部挑战！", True, DARK_GRAY)
        elif is_win:
            title = self.font_big.render("本关通关！", True, GREEN)
            msg = self.font_mid.render("所有箭头已飞出", True, DARK_GRAY)
        else:
            title = self.font_big.render("挑战失败", True, RED)
            msg = self.font_mid.render("失误次数耗尽", True, DARK_GRAY)

        self.screen.blit(title, (box_rect.centerx - title.get_width() // 2, box_rect.y + 20))
        self.screen.blit(msg, (box_rect.centerx - msg.get_width() // 2, box_rect.y + 70))

        self.btn_next_rect = pygame.Rect(120, box_rect.y + 130, 130, 48)
        self.btn_replay_rect = pygame.Rect(270, box_rect.y + 130, 130, 48)
        self.btn_select_rect = pygame.Rect(120, box_rect.y + 200, 130, 48)
        self.btn_exit_rect = pygame.Rect(270, box_rect.y + 200, 130, 48)

        if is_win and not is_all_clear:
            self.screen.blit(self.btn_next_level, self.btn_next_rect)

        self.screen.blit(self.btn_replay, self.btn_replay_rect)
        self.screen.blit(self.btn_level_select, self.btn_select_rect)
        self.screen.blit(self.btn_exit, self.btn_exit_rect)

    def draw_level_select(self):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(80, 120, 540, 500)
        pygame.draw.rect(self.screen, WHITE, panel_rect, border_radius=12)

        title = self.font_big.render("选择关卡", True, DARK_GRAY)
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 20))

        self.level_btns = []
        btn_w = 120
        btn_h = 60
        start_x = 110
        start_y = 100 + 80

        for i in range(len(LEVELS)):
            bx = start_x + (i % 3) * (btn_w + 20)
            by = start_y + (i // 3) * (btn_h + 20)
            rect = pygame.Rect(bx, by, btn_w, btn_h)
            self.level_btns.append(rect)

            if i in self.unlocked_levels:
                color = GREEN
            else:
                color = LIGHT_GRAY

            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            txt = self.font_mid.render(f"关卡{i + 1}", True, WHITE)
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        self.btn_back_rect = pygame.Rect(260, 620, 180, 50)
        self.screen.blit(self.btn_back, self.btn_back_rect)

    def run(self):
        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = event.pos

                    if self.state == "start":
                        start_rect = self.draw_start_screen()
                        if start_rect.collidepoint(click_pos):
                            self.state = "game"
                            self.load_level()

                    elif self.state == "game":
                        if self.setting_rect.collidepoint(click_pos):
                            self.state = "setting"
                            continue

                        if self.restart_rect.collidepoint(click_pos):
                            self.state = "game"
                            self.load_level()
                            continue

                        if not self.animating:
                            lv = LEVELS[self.current_level_idx]
                            board_size = lv["size"]
                            for arr in self.arrows:
                                cx = self.offset_x + arr["x"] * CELL_SIZE
                                cy = self.offset_y + arr["y"] * CELL_SIZE
                                rect = pygame.Rect(cx, cy, CELL_SIZE - MARGIN, CELL_SIZE - MARGIN)
                                if rect.collidepoint(click_pos):
                                    block = self.check_block(arr["x"], arr["y"], arr["dir"])
                                    if block:
                                        self.animating = True
                                        self.anim_type = "bump"
                                        self.anim_target = arr
                                        self.anim_timer = 0
                                        self.mistake_left -= 1
                                    else:
                                        self.animating = True
                                        self.anim_type = "fly"
                                        self.anim_target = arr
                                        self.anim_timer = 0

                    elif self.state == "setting":
                        btn_level_rect, btn_exit_rect = self.draw_setting_panel()
                        if btn_level_rect.collidepoint(click_pos):
                            self.state = "level_select"
                        if btn_exit_rect.collidepoint(click_pos):
                            pygame.quit()
                            sys.exit()

                    elif self.state in ("win", "lose"):
                        self.draw_modal(self.state == "win")

                        if self.btn_replay_rect and self.btn_replay_rect.collidepoint(click_pos):
                            self.state = "game"
                            self.load_level()

                        if self.btn_select_rect and self.btn_select_rect.collidepoint(click_pos):
                            self.state = "level_select"

                        if self.btn_exit_rect and self.btn_exit_rect.collidepoint(click_pos):
                            pygame.quit()
                            sys.exit()

                        if self.state == "win" and self.btn_next_rect and self.btn_next_rect.collidepoint(click_pos):
                            if self.current_level_idx + 1 < len(LEVELS):
                                self.current_level_idx += 1
                                self.state = "game"
                                self.load_level()

                    elif self.state == "level_select":
                        for idx, rect in enumerate(self.level_btns):
                            if rect.collidepoint(click_pos):
                                if idx in self.unlocked_levels:
                                    self.current_level_idx = idx
                                    self.state = "game"
                                    self.load_level()

                        if self.btn_back_rect and self.btn_back_rect.collidepoint(click_pos):
                            self.state = "start"

            if self.animating:
                self.anim_timer += 1
                if self.anim_timer > 25:
                    if self.anim_type == "fly":
                        self.arrows.remove(self.anim_target)
                        if len(self.arrows) == 0:
                            self.state = "win"
                            self.unlocked_levels.add(self.current_level_idx)

                    self.animating = False
                    self.anim_timer = 0
                    self.anim_target = None

                    if self.mistake_left <= 0:
                        self.state = "lose"

            if self.state == "start":
                self.draw_start_screen()
            elif self.state == "game":
                self.draw_game_screen()
            elif self.state == "setting":
                self.draw_game_screen()
                self.draw_setting_panel()
            elif self.state in ("win", "lose"):
                self.draw_game_screen()
                self.draw_modal(self.state == "win")
            elif self.state == "level_select":
                self.draw_level_select()

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()

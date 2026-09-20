import pygame
import sys
import math

# -------------------------- 常量配置 --------------------------
WIDTH = 700
HEIGHT = 750
FPS = 60
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
GREEN = (30, 180, 60)
BLUE = (30, 80, 200)
CELL_SIZE = 80
MARGIN = 10
# 方向字符和向量
DIR_VEC = {
    "↑": (0, -1),
    "↓": (0, 1),
    "←": (-1, 0),
    "→": (1, 0)
}
# 关卡（人工试玩，可通关）
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
            ["→", "", "", "", ""],
            ["", "↑", "", "", ""],
            ["", "", "", "", ""],
            ["", "", "", "↓", ""],
            ["", "", "", "", "←"]
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
    }
]
# -------------------------- 游戏状态 --------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("一箭又一箭")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("simhei", 48)
        self.font_mid = pygame.font.SysFont("simhei", 28)
        self.font_small = pygame.font.SysFont("simhei", 22)
        self.state = "start"  # start / game / win / lose
        self.current_level_idx = 0
        self.mistake_left = 3
        self.arrows = []  # 存储箭头：{"x":x,"y":y,"dir":dir}
        self.animating = False
        self.anim_timer = 0
        self.anim_type = None  # fly / bump
        self.anim_target = None
        self.restart_rect = pygame.Rect(520, 8, 140, 36) # 重新开始按钮矩形
        self.offset_x = 0
        self.offset_y = 0

    def load_level(self):
        """加载当前关卡"""
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
        # 计算棋盘偏移
        self.offset_x = (WIDTH - size * CELL_SIZE) // 2
        self.offset_y = 80

    def check_block(self, x, y, direction):
        """检测箭头沿方向前进是否有阻挡"""
        dx, dy = DIR_VEC[direction]
        cx = x + dx
        cy = y + dy
        board_size = LEVELS[self.current_level_idx]["size"]
        while 0 <= cx < board_size and 0 <= cy < board_size:
            for arr in self.arrows:
                if arr["x"] == cx and arr["y"] == cy:
                    return True  # 前方有阻挡
            cx += dx
            cy += dy
        return False

    def draw_start_screen(self):
        self.screen.fill(WHITE)
        title = self.font_big.render("一箭又一箭", True, BLACK)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        text1 = self.font_mid.render("点击箭头，让它朝指向飞出棋盘", True, BLACK)
        text2 = self.font_mid.render("前方有箭头阻挡会消耗失误次数", True, BLACK)
        text3 = self.font_mid.render("清空所有箭头通关，失误用完失败", True, BLACK)
        self.screen.blit(text1, (WIDTH//2-text1.get_width()//2,220))
        self.screen.blit(text2, (WIDTH//2-text2.get_width()//2,270))
        self.screen.blit(text3, (WIDTH//2-text3.get_width()//2,320))
        btn_rect = pygame.Rect(WIDTH//2 - 100, 420, 200, 60)
        pygame.draw.rect(self.screen, BLUE, btn_rect, border_radius=8)
        btn_text = self.font_mid.render("开始游戏", True, WHITE)
        self.screen.blit(btn_text, (btn_rect.centerx-btn_text.get_width()//2, btn_rect.centery-btn_text.get_height()//2))
        return btn_rect

    def draw_game_screen(self):
        self.screen.fill(WHITE)
        lv = LEVELS[self.current_level_idx]
        board_size = lv["size"]
        # 顶部信息
        info1 = self.font_small.render(f"关卡：{self.current_level_idx+1}", True, BLACK)
        info2 = self.font_small.render(f"剩余箭头：{len(self.arrows)}", True, BLACK)
        info3 = self.font_small.render(f"剩余失误：{self.mistake_left}", True, RED)
        self.screen.blit(info1, (20, 10))
        self.screen.blit(info2, (160, 10))
        self.screen.blit(info3, (320, 10))
        # 重新开始按钮
        pygame.draw.rect(self.screen, GRAY, self.restart_rect, border_radius=6)
        restart_text = self.font_small.render("重新开始", True, WHITE)
        self.screen.blit(restart_text, (self.restart_rect.centerx-restart_text.get_width()//2, self.restart_rect.centery-restart_text.get_height()//2))
        # 绘制棋盘格子
        for y in range(board_size):
            for x in range(board_size):
                rect = pygame.Rect(self.offset_x + x*CELL_SIZE, self.offset_y + y*CELL_SIZE, CELL_SIZE-MARGIN, CELL_SIZE-MARGIN)
                pygame.draw.rect(self.screen, GRAY, rect, border_radius=4)
        # 绘制箭头 + 动画
        for arr in self.arrows:
            ax, ay = arr["x"], arr["y"]
            rect = pygame.Rect(self.offset_x + ax*CELL_SIZE, self.offset_y + ay*CELL_SIZE, CELL_SIZE-MARGIN, CELL_SIZE-MARGIN)
            color = BLACK
            # 抖动动画
            if self.animating and self.anim_type == "bump" and self.anim_target == arr:
                shake = int(math.sin(self.anim_timer*0.3)*6)
                rect.x += shake
                color = RED
            # 飞行动画
            if self.animating and self.anim_type == "fly" and self.anim_target == arr:
                dx, dy = DIR_VEC[arr["dir"]]
                rect.x += dx * self.anim_timer * 3
                rect.y += dy * self.anim_timer * 3
                color = (100,100,100)
            text = self.font_big.render(arr["dir"], True, color)
            self.screen.blit(text, (rect.centerx-text.get_width()//2, rect.centery-text.get_height()//2))

    def draw_modal(self, is_win):
        """通关/失败弹窗"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))
        box_rect = pygame.Rect(120,200,460,280)
        pygame.draw.rect(self.screen, WHITE, box_rect, border_radius=12)
        if is_win:
            title = self.font_big.render("🎉 本关通关！", True, GREEN)
            msg = self.font_mid.render("所有箭头已飞出", True, BLACK)
            btn1_text = "下一关"
            btn2_text = "重玩本关"
        else:
            title = self.font_big.render("💥 挑战失败", True, RED)
            msg = self.font_mid.render("失误次数耗尽", True, BLACK)
            btn1_text = ""
            btn2_text = "重玩本关"
        self.screen.blit(title, (box_rect.centerx-title.get_width()//2, box_rect.y+30))
        self.screen.blit(msg, (box_rect.centerx-msg.get_width()//2, box_rect.y+90))
        btn1 = pygame.Rect(160, box_rect.y+160, 140,50)
        btn2 = pygame.Rect(380, box_rect.y+160,140,50)
        if is_win:
            pygame.draw.rect(self.screen, GREEN, btn1, border_radius=8)
            t1 = self.font_mid.render(btn1_text, True, WHITE)
            self.screen.blit(t1, (btn1.centerx-t1.get_width()//2, btn1.centery-t1.get_height()//2))
        pygame.draw.rect(self.screen, BLUE, btn2, border_radius=8)
        t2 = self.font_mid.render(btn2_text, True, WHITE)
        self.screen.blit(t2, (btn2.centerx-t2.get_width()//2, btn2.centery-t2.get_height()//2))
        return btn1, btn2

    def run(self):
        while True:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = event.pos
                    if self.state == "start":
                        btn = self.draw_start_screen()
                        if btn.collidepoint(click_pos):
                            self.state = "game"
                            self.load_level()
                    # =========【重点修改：右上角重新开始，不管当前是什么状态都生效！】=========
                    # 不管是 game / win / lose，点击右上角按钮，统一执行：切回game + 加载关卡
                    if self.restart_rect.collidepoint(click_pos):
                        self.state = "game"
                        self.load_level()
                        continue

                    if self.state == "game":
                        # 动画播放时禁止点击箭头
                        if not self.animating:
                            lv = LEVELS[self.current_level_idx]
                            board_size = lv["size"]
                            for arr in self.arrows:
                                cx = self.offset_x + arr["x"] * CELL_SIZE
                                cy = self.offset_y + arr["y"] * CELL_SIZE
                                rect = pygame.Rect(cx, cy, CELL_SIZE-MARGIN, CELL_SIZE-MARGIN)
                                if rect.collidepoint(click_pos):
                                    # 点击箭头
                                    block = self.check_block(arr["x"], arr["y"], arr["dir"])
                                    if block:
                                        # 碰撞抖动
                                        self.animating = True
                                        self.anim_type = "bump"
                                        self.anim_target = arr
                                        self.anim_timer = 0
                                        self.mistake_left -=1
                                    else:
                                        # 飞出动画
                                        self.animating = True
                                        self.anim_type = "fly"
                                        self.anim_target = arr
                                        self.anim_timer = 0
                    elif self.state in ("win", "lose"):
                        btn1, btn2 = self.draw_modal(self.state=="win")
                        if btn2.collidepoint(click_pos):
                            self.state = "game"
                            self.load_level()
                        if self.state == "win" and btn1.collidepoint(click_pos):
                            if self.current_level_idx + 1 < len(LEVELS):
                                self.current_level_idx +=1
                                self.state = "game"
                                self.load_level()
            # 动画更新
            if self.animating:
                self.anim_timer += 1
                if self.anim_timer > 25:
                    # 动画结束
                    if self.anim_type == "fly":
                        self.arrows.remove(self.anim_target)
                        if len(self.arrows) == 0:
                            self.state = "win"
                    self.animating = False
                    self.anim_timer =0
                    self.anim_target = None
                    # 失误判断
                    if self.mistake_left <= 0:
                        self.state = "lose"
            # 绘制逻辑
            if self.state == "start":
                self.draw_start_screen()
            elif self.state == "game":
                self.draw_game_screen()
            elif self.state in ("win", "lose"):
                self.draw_game_screen()
                self.draw_modal(self.state=="win")
            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()

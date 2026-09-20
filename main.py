import pygame
import sys
import math

# -------------------------- 常量配置 --------------------------
WIDTH = 700
HEIGHT = 750
FPS = 60
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (150,150,150)
BLACK = (0, 0, 0)
RED = (200, 30, 30)
GREEN = (30, 180, 60)
BLUE = (30, 80, 200)
ORANGE = (255, 140, 0)
CELL_SIZE = 80
MARGIN = 10

# 方向字符和向量
DIR_VEC = {
    "↑": (0, -1),
    "↓": (0, 1),
    "←": (-1, 0),
    "→": (1, 0)
}

# 关卡（一共5关，4、5为新增嵌套高难度关卡，解法单一）
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
        self.font_tiny = pygame.font.SysFont("simhei", 20)

        self.state = "start"  # start / game / win / lose / level_select
        self.current_level_idx = 0
        self.unlocked_levels = {0} # 已通关解锁的关卡集合，初始解锁第0关（关卡1）
        self.mistake_left = 3
        self.arrows = []
        self.animating = False
        self.anim_timer = 0
        self.anim_type = None
        self.anim_target = None

        self.restart_rect = pygame.Rect(520, 8, 140, 36)
        self.restart_pressed = False
        self.offset_x = 0
        self.offset_y = 0

        # 关卡选择面板按钮
        self.level_btns = []
        self.exit_btn = pygame.Rect(260, 620, 180, 50) # 退出游戏按钮

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
        info1 = self.font_small.render(f"关卡：{self.current_level_idx+1}", True, BLACK)
        info2 = self.font_small.render(f"剩余箭头：{len(self.arrows)}", True, BLACK)
        info3 = self.font_small.render(f"剩余失误：{self.mistake_left}", True, RED)
        self.screen.blit(info1, (20, 10))
        self.screen.blit(info2, (160, 10))
        self.screen.blit(info3, (320, 10))

        # 绘制重新开始按钮
        if self.restart_pressed:
            restart_color = ORANGE
        else:
            restart_color = GREEN
        pygame.draw.rect(self.screen, restart_color, self.restart_rect, border_radius=6)
        restart_text = self.font_small.render("重新开始", True, WHITE)
        self.screen.blit(restart_text, (self.restart_rect.centerx-restart_text.get_width()//2, self.restart_rect.centery-restart_text.get_height()//2))

        # 棋盘格子
        for y in range(board_size):
            for x in range(board_size):
                rect = pygame.Rect(self.offset_x + x*CELL_SIZE, self.offset_y + y*CELL_SIZE, CELL_SIZE-MARGIN, CELL_SIZE-MARGIN)
                pygame.draw.rect(self.screen, GRAY, rect, border_radius=4)
        # 绘制箭头
        for arr in self.arrows:
            ax, ay = arr["x"], arr["y"]
            rect = pygame.Rect(self.offset_x + ax*CELL_SIZE, self.offset_y + ay*CELL_SIZE, CELL_SIZE-MARGIN, CELL_SIZE-MARGIN)
            color = BLACK
            if self.animating and self.anim_type == "bump" and self.anim_target == arr:
                shake = int(math.sin(self.anim_timer*0.3)*6)
                rect.x += shake
                color = RED
            if self.animating and self.anim_type == "fly" and self.anim_target == arr:
                dx, dy = DIR_VEC[arr["dir"]]
                rect.x += dx * self.anim_timer * 3
                rect.y += dy * self.anim_timer * 3
                color = (100,100,100)
            text = self.font_big.render(arr["dir"], True, color)
            self.screen.blit(text, (rect.centerx-text.get_width()//2, rect.centery-text.get_height()//2))

    def draw_modal(self, is_win):
        """通关/失败弹窗：增加选择关卡、结束游戏按钮"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(160)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))
        box_rect = pygame.Rect(100,160,500,340)
        pygame.draw.rect(self.screen, WHITE, box_rect, border_radius=12)

        is_all_clear = is_win and (self.current_level_idx == len(LEVELS)-1)
        if is_all_clear:
            title = self.font_big.render("🎉 恭喜！通关所有关卡！", True, GREEN)
            msg = self.font_mid.render("你完成全部挑战！", True, BLACK)
            btn1_text = ""
        elif is_win:
            title = self.font_big.render("🎉 本关通关！", True, GREEN)
            msg = self.font_mid.render("所有箭头已飞出", True, BLACK)
            btn1_text = "下一关"
        else:
            title = self.font_big.render("💥 挑战失败", True, RED)
            msg = self.font_mid.render("失误次数耗尽", True, BLACK)
            btn1_text = ""

        self.screen.blit(title, (box_rect.centerx-title.get_width()//2, box_rect.y+20))
        self.screen.blit(msg, (box_rect.centerx-msg.get_width()//2, box_rect.y+70))

        btn1 = pygame.Rect(120, box_rect.y+130, 130,50)
        btn2 = pygame.Rect(270, box_rect.y+130, 130,50)
        btn_select = pygame.Rect(120, box_rect.y+200, 130,50)
        btn_exit = pygame.Rect(270, box_rect.y+200, 130,50)

        if is_win and not is_all_clear:
            pygame.draw.rect(self.screen, GREEN, btn1, border_radius=8)
            t1 = self.font_mid.render(btn1_text, True, WHITE)
            self.screen.blit(t1, (btn1.centerx-t1.get_width()//2, btn1.centery-t1.get_height()//2))

        pygame.draw.rect(self.screen, BLUE, btn2, border_radius=8)
        t2 = self.font_mid.render("重玩本关", True, WHITE)
        self.screen.blit(t2, (btn2.centerx-t2.get_width()//2, btn2.centery-t2.get_height()//2))

        pygame.draw.rect(self.screen, ORANGE, btn_select, border_radius=8)
        t_sel = self.font_mid.render("选择关卡", True, WHITE)
        self.screen.blit(t_sel, (btn_select.centerx-t_sel.get_width()//2, btn_select.centery-t_sel.get_height()//2))

        pygame.draw.rect(self.screen, RED, btn_exit, border_radius=8)
        t_e = self.font_mid.render("结束游戏", True, WHITE)
        self.screen.blit(t_e, (btn_exit.centerx-t_e.get_width()//2, btn_exit.centery-t_e.get_height()//2))
        return btn1, btn2, btn_select, btn_exit

    def draw_level_select(self):
        """关卡选择面板：仅已通关关卡可点击"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0,0))
        panel_rect = pygame.Rect(80,120,540,500)
        pygame.draw.rect(self.screen, WHITE, panel_rect, border_radius=12)
        title = self.font_big.render("选择关卡", True, BLACK)
        self.screen.blit(title, (panel_rect.centerx-title.get_width()//2, panel_rect.y+20))

        self.level_btns = []
        btn_w = 120
        btn_h = 60
        start_x = 110
        start_y = 100 + 80
        for i in range(len(LEVELS)):
            bx = start_x + (i % 3)*(btn_w + 20)
            by = start_y + (i // 3)*(btn_h + 20)
            rect = pygame.Rect(bx,by,btn_w,btn_h)
            self.level_btns.append(rect)
            if i in self.unlocked_levels:
                color = GREEN
            else:
                color = LIGHT_GRAY
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            txt = self.font_mid.render(f"关卡{i+1}", True, WHITE)
            self.screen.blit(txt, (rect.centerx-txt.get_width()//2, rect.centery-txt.get_height()//2))

        # 返回按钮
        self.exit_btn = pygame.Rect(260, 620, 180, 50)
        pygame.draw.rect(self.screen, BLUE, self.exit_btn, border_radius=8)
        back_txt = self.font_mid.render("返回", True, WHITE)
        self.screen.blit(back_txt, (self.exit_btn.centerx-back_txt.get_width()//2, self.exit_btn.centery-back_txt.get_height()//2))

    def run(self):
        while True:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # 重新开始按钮鼠标按下松开变色
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.restart_rect.collidepoint(event.pos):
                        self.restart_pressed = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.restart_pressed:
                        self.restart_pressed = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = event.pos
                    if self.state == "start":
                        btn = self.draw_start_screen()
                        if btn.collidepoint(click_pos):
                            self.state = "game"
                            self.load_level()

                    # 右上角重新开始按钮
                    if self.restart_rect.collidepoint(click_pos):
                        self.state = "game"
                        self.load_level()
                        continue

                    if self.state == "game":
                        if not self.animating:
                            lv = LEVELS[self.current_level_idx]
                            board_size = lv["size"]
                            for arr in self.arrows:
                                cx = self.offset_x + arr["x"] * CELL_SIZE
                                cy = self.offset_y + arr["y"] * CELL_SIZE
                                rect = pygame.Rect(cx, cy, CELL_SIZE-MARGIN, CELL_SIZE-MARGIN)
                                if rect.collidepoint(click_pos):
                                    block = self.check_block(arr["x"], arr["y"], arr["dir"])
                                    if block:
                                        self.animating = True
                                        self.anim_type = "bump"
                                        self.anim_target = arr
                                        self.anim_timer = 0
                                        self.mistake_left -=1
                                    else:
                                        self.animating = True
                                        self.anim_type = "fly"
                                        self.anim_target = arr
                                        self.anim_timer = 0

                    elif self.state in ("win", "lose"):
                        btn1, btn2, btn_sel, btn_exit = self.draw_modal(self.state=="win")
                        if btn2.collidepoint(click_pos):
                            self.state = "game"
                            self.load_level()
                        if btn_sel.collidepoint(click_pos):
                            self.state = "level_select"
                        if btn_exit.collidepoint(click_pos):
                            pygame.quit()
                            sys.exit()
                        # 下一关
                        if self.state == "win" and btn1.collidepoint(click_pos):
                            if self.current_level_idx +1 < len(LEVELS):
                                self.current_level_idx +=1
                                self.state = "game"
                                self.load_level()

                    elif self.state == "level_select":
                        # 点击关卡按钮，仅解锁关卡生效
                        for idx, rect in enumerate(self.level_btns):
                            if rect.collidepoint(click_pos):
                                if idx in self.unlocked_levels:
                                    self.current_level_idx = idx
                                    self.state = "game"
                                    self.load_level()
                        # 返回按钮
                        if self.exit_btn.collidepoint(click_pos):
                            self.state = "game"

            # 动画更新逻辑
            if self.animating:
                self.anim_timer += 1
                if self.anim_timer > 25:
                    if self.anim_type == "fly":
                        self.arrows.remove(self.anim_target)
                        if len(self.arrows) == 0:
                            self.state = "win"
                            # 通关，解锁当前关卡
                            self.unlocked_levels.add(self.current_level_idx)
                    self.animating = False
                    self.anim_timer =0
                    self.anim_target = None
                    if self.mistake_left <= 0:
                        self.state = "lose"

            # 绘制
            if self.state == "start":
                self.draw_start_screen()
            elif self.state == "game":
                self.draw_game_screen()
            elif self.state in ("win", "lose"):
                self.draw_game_screen()
                self.draw_modal(self.state=="win")
            elif self.state == "level_select":
                self.draw_level_select()

            pygame.display.update()

if __name__ == "__main__":
    game = Game()
    game.run()

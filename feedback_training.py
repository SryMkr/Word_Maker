'''
第一，每一轮结束之后要清空finished task里面的记录
第二 为什么下一轮的进度条不变化了
'''

from game_level_function import *


class GameFeedback(object):
    # 初始化一些参数
    def __init__(self, word_maker):
        self.word_maker = word_maker  # 得到主游戏
        self.surface_width, self.surface_height = self.word_maker.window.get_size()  # 得到主游戏的屏幕的长和宽
        # 创建一个和主屏幕大小一样的Surface
        self.feedback_surface = pygame.Surface((self.surface_width, self.surface_height))
        # 要从游戏主题内容继承到玩家的拼写记录
        self.finished_tasks = self.word_maker.finished_tasks
        self.start_time = datetime.now()  # 玩游戏开始的时间  # 记录什么时候开始看反馈的
        self.countdown = 60  # 初始化倒计时，用来记录已经过了多久
        self.feedback_time = 60  # 反馈展示60秒
        self.decrease_width = self.surface_width / self.feedback_time  # 1秒减少多少宽度

        self.x_increase = 250  # 横坐标的增量
        self.y_increase = 50  # 纵坐标的增量

    # 写字功能
    def draw_Left_Text(self, font, text, size, x, y, COLOR=(0, 0, 0)):
        font = pygame.font.Font(font, size)  # 文本的字体及大小
        text_surface = font.render(text, True, COLOR)  # 默认文本为黑色
        text_rect = text_surface.get_rect()  # 相当于给当前的surface 框起来 这样比较容易获得和使用参数
        text_rect.topleft = (x, y)  # 文本的中心点的坐标
        self.feedback_surface.blit(text_surface, text_rect)  # 左对齐

    # 展示玩家的拼写记录
    def finished_Tasks(self):
        x_coordinate = 0  # 初始横坐标
        y_coordinate = 100  # 初始纵坐标
        # 先展示一句话
        self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '你有60秒时间查看反馈', 40, 300, 0)
        # 在展示每一列的列标题
        self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '单词', 40, 0, 50)
        self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '音标', 40, 250, 50)
        self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '汉语', 40, 500, 50)
        self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '你的拼写', 40, 750, 50)
        # 展示完成任务里面的内容，这是一个字典
        for key, items in self.finished_tasks.items():
            # 先画单词
            self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", key, 40, x_coordinate, y_coordinate)
            for index in range(len(items)):
                if index == 0:  # 音标
                    # 音标
                    self.draw_Left_Text("Game_Fonts/phonetic.ttf", items[index], 30, x_coordinate+(index+1)*self.x_increase, y_coordinate)
                elif index == 1:  # 汉语
                    self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", items[index], 40,\
                                        x_coordinate+(index+1)*self.x_increase, y_coordinate)
                else:
                    self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", items[index], 40,
                                        x_coordinate + (index+1) * self.x_increase, y_coordinate)
            y_coordinate += self.y_increase  # 每一个单词内容展示完以后，将纵坐标增加

    # 展示进度条
    def draw_progress_bar(self):
        self.finished_Tasks()  # 展示所有的内容
        # 画一个progress bar，控制展示反馈的时间
        pygame.draw.rect(self.feedback_surface, (0, 0, 0),
                         ((0, self.surface_height - 60), (self.surface_width, 50)),
                         width=4)  # 首先画一个边框
        self.task_second = self.feedback_time - self.countdown  # 记录已经过了多少秒
        if 0 <= self.task_second <= 20:
            pygame.draw.rect(self.feedback_surface, (190, 190, 190),
                             ((self.task_second * self.decrease_width, self.surface_height - 56),
                              (self.surface_width - self.task_second * self.decrease_width, 42)))  # 画进度条
        elif 20 <= self.task_second <= 40:
            pygame.draw.rect(self.feedback_surface, (180, 180, 180),
                             ((self.task_second * self.decrease_width, self.surface_height - 56),
                              (self.surface_width - self.task_second * self.decrease_width, 42)))  # 画进度条
        else:
            pygame.draw.rect(self.feedback_surface, (170, 170, 170),
                             ((self.task_second * self.decrease_width, self.surface_height - 56),
                              (self.surface_width - self.task_second * self.decrease_width, 42)))  # 画进度条
        # 控制单词展示的时间
        if datetime.now() > self.start_time + timedelta(seconds=1):  # 如果时间间隔相差一秒
            self.start_time = datetime.now()  # 将现在的时间给过去的时间
            self.countdown -= 1
            if self.countdown == -1:  # 如果时间结束，则进入游戏界面
                self.word_maker.finished_tasks = {}  # 每一轮结束以后，要将这轮的记录清零
                self.word_maker.current_menu = self.word_maker.game_level_menu

    # 展示所有的元素
    def display_menu(self):
        self.feedback_surface.fill(self.word_maker.BGC)  # 游戏的背景颜色
        self.draw_progress_bar()
        self.word_maker.window.blit(self.feedback_surface, (0, 0))  # 将游戏界面的内容画到游戏主题上
'''
1：已经学会的单词要加入对应的deck，并且根据第几次学习改变其对应的deck
2：选择10个单词要有一个合理的逻辑
3：一轮结束以后  如果单词已经完成到了最难的一关 标记为4的一关，将本次学习的单词移除单词库 并且加入到对应的库中 并且要重写单词库中的内容让后续可以继续读取


'''

import pygame
from datetime import datetime, timedelta
from Common_Functions import remove_tasks_xls


class GameFeedback(object):
    # 初始化一些参数
    def __init__(self, word_maker):
        self.word_maker = word_maker  # 得到主游戏
        self.surface_width, self.surface_height = self.word_maker.window.get_size()  # 得到主游戏的屏幕的长和宽
        # 创建一个和主屏幕大小一样的Surface
        self.feedback_surface = pygame.Surface((self.surface_width, self.surface_height))
        # 要从游戏主题内容继承到玩家的拼写记录，这是记录测试内容
        self.finished_tasks = self.word_maker.finished_tasks
        # 这是feedback给所有的内容
        self.all_tasks = self.word_maker.all_tasks
        self.start_time = datetime.now()  # 玩游戏开始的时间  # 记录什么时候开始看反馈的
        self.countdown = 3  # 初始化倒计时，用来记录已经过了多久
        self.feedback_time = 3  # 反馈展示60秒
        self.decrease_width = self.surface_width / self.feedback_time  # 1秒减少多少宽度
        self.learned_words = [] # 用来记录玩家已经记住的单词
        self.x_increase = 250  # 横坐标的增量
        self.y_increase = 50  # 纵坐标的增量

    # 写字功能
    def draw_Left_Text(self, font, text, size, x, y, COLOR=(0, 0, 0)):
        font = pygame.font.Font(font, size)  # 文本的字体及大小
        text_surface = font.render(text, True, COLOR)  # 默认文本为黑色
        text_rect = text_surface.get_rect()  # 相当于给当前的surface 框起来 这样比较容易获得和使用参数
        text_rect.topleft = (x, y)  # 文本的中心点的坐标
        self.feedback_surface.blit(text_surface, text_rect)  # 左对齐

    # 匹配玩家已经学会的单词，并在测试列表中删除
    def remove_learned_words(self):
        # {单词，[音标，汉语，玩家拼写，任务难度]}
        for key, items in self.finished_tasks.items():
            # 条件1：如果正确拼写和玩家的拼写一样 条件2：本次任务的难度是最高难度
            if key == items[2] and str(items[3]) == '4':
                self.learned_words.append(key)
        # 将已经记住的单词移除单词库
        remove_tasks_xls('Word_Pool/game_level_'+str(self.word_maker.current_loop)+'.xls', self.learned_words)
        print(self.learned_words)

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
        # 展示完成任务里面的内容，这是一个字典{单词：[音标，汉语，玩家拼写]}
        for key, items in self.all_tasks.items():
            # 先画单词
            self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", key, 40, x_coordinate, y_coordinate)
            for index in range(len(items)):
                if index == 0:  # 音标
                    # 音标
                    self.draw_Left_Text("Game_Fonts/phonetic.ttf", items[index], 30, x_coordinate+(index+1)*self.x_increase, y_coordinate)
                elif index == 1:  # 汉语
                    self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", items[index], 40,\
                                        x_coordinate+(index+1)*self.x_increase, y_coordinate)
                else: # 玩家拼写
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
                # 在这里要完成删除已经完成的任务，但是feedback还是展示所有的单词
                self.remove_learned_words()  # 从列表中删除已经学会的单词
                self.word_maker.finished_tasks = {}  # 每一轮结束以后，要将这轮的记录清零，保存了{单词，[音标，汉语，玩家拼写，单词难度]}
                self.word_maker.current_loop += 1  # 将当前的轮数加一
                if self.word_maker.current_loop == 3:  # 如果已经超出了轮数
                    self.word_maker.all_tasks = {}  # 每次所有的单词学习结束，都要将里面的内容清空，因为会读取新的单词
                    self.word_maker.current_menu = self.word_maker.main_menu  # 重新回到主菜单，相当于本次的学习已经结束
                else:
                    from game_level_function import GameLevel  # python无法重复导入，所以只能在使用的地方再导入
                    self.word_maker.game_level_menu = GameLevel(self.word_maker)  # 重新读取游戏文件
                    self.word_maker.current_menu = self.word_maker.game_level_menu  # 重新回到游戏界面

    # 展示所有的元素
    def display_menu(self):
        self.feedback_surface.fill(self.word_maker.BGC)  # 游戏的背景颜色
        self.draw_progress_bar()
        self.word_maker.window.blit(self.feedback_surface, (0, 0))  # 将游戏界面的内容画到游戏主题上
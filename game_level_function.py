'''
该函数的主要功能是 实现动态化单词关卡
单词展示，有无迷惑字母，拖拽
'''
from Common_Functions import *
from datetime import datetime, timedelta


# 实例化肯定是直接实例化库里的所有单词，因为所有的参数都已经确定了
class GameLevel(object):
    # 单词，音标，汉语，机会次数，单词长度，时间，是否展示任务，是否展示英标 （应该是一个单词一组），有无迷惑字母
    tasks_parameters_list = read_tasks_parameters('Word_Pool/game_level.xls')

    # 游戏关卡里有几个重要的参数，第一个机会次数,第二个参数是单词的长度
    def __init__(self, word_maker):
        self.word_maker = word_maker  # 得到主游戏
        self.surface_width, self.surface_height = self.word_maker.window.get_size()  # 得到主游戏的屏幕的长和宽
        # 创建一个和主屏幕大小一样的Surface
        self.game_level_surface = pygame.Surface((self.surface_width, self.surface_height))
        # 这个字典用来选择迷惑字母
        self.letters_dic = {'a': ['e', 'i', 'o', 'u', 'y'], 'b': ['d', 'p', 'q', 't'], 'c': ['k', 's', 't', 'z'],
                            'd': ['b', 'p', 'q', 't'],
                            'e': ['a', 'o', 'i', 'u', 'y'], 'f': ['v', 'w'], 'g': ['h', 'j'], 'h': ['m', 'n'],
                            'i': ['a', 'e', 'o', 'y'],
                            'j': ['g', 'i'], 'k': ['c', 'g'], 'l': ['i', 'r'], 'm': ['h', 'n'], 'n': ['h', 'm'],
                            'o': ['a', 'e', 'i', 'u', 'y'],
                            'p': ['b', 'd', 'q', 't'], 'q': ['b', 'd', 'p', 't'], 'r': ['l', 'v'], 's': ['c', 'z'],
                            't': ['c', 'd'], 'u': ['v', 'w'],
                            'v': ['f', 'u', 'w'], 'w': ['f', 'v'], 'x': ['s', 'z'], 'y': ['e', 'i'], 'z': ['c', 's']}
        self.BLOCK_SIZE = 90  # 设置框的大小
        self.task_index = 0  # 追踪当前是第几个任务
        self.start_time = datetime.now()  # 玩游戏开始的时间
        self.task_second = 0  # 记录玩家用了多少时间记住这个单词
        self.time_change = True  # 每换一个单词，需要重新记录时间
        self.countdown = 0  # 初始化倒计时
        self.letter_coordinate = {}  # 创建一个字典{字母_顺序：坐标}，为了避免某个单词有重复字母，导致字典重复赋值
        self.BLACK = (0, 0, 0)  # 字母是黑色的
        self.font = pygame.font.Font("Game_Fonts/chinese_pixel_font.TTF", 50)  # 字母的字体，大小
        self.task_change = True  # 控制切换任务的开关

    # 该函数的作用是将单词拆分为字母，并固定其初始的位置
    def split_Word(self, word):  # 首先输入一个单词
        letter_list = []  # 创建一个列表准备读取单词的字母
        self.letter_coordinate = {}  # 每次拆分单词都要归0，不然保持以前的记录
        self.current_word_length = len(word)  # 获得当前单词的长度
        self.current_word = word  # 获得当前字母的拼写
        if self.tasks_parameters_list[self.task_index][9]:  # 需要加一个判断，本难度需不需要迷惑字母
            for letter in word:  # 循环读取字母
                confusing_letter = random.choice(self.letters_dic[letter])  # 随机挑选一个迷惑字母
                letter_list.append(confusing_letter)  # 将迷惑字谜加到列表中
                letter_list.append(letter)  # 将字母加入到列表中
        else:
            for letter in word:  # 循环读取字母
                letter_list.append(letter)  # 将字母加入到列表中
        random.shuffle(letter_list)  # 将里面加入列表的字母的顺序随机打乱
        letter_x_coordinate = 0  # 横坐标从0开始
        letter_y_coordinate = 50  # 纵坐标从30开始
        increase = 70  # 字母与字母之间的间距为70
        for i in range(len(letter_list)):  # 循环字母的个数
            coordinate = [letter_x_coordinate, letter_y_coordinate]  # 每个字母的坐标都需要重新刷新
            letter_x_coordinate += increase
            self.letter_coordinate[letter_list[i] + '_' + str(i)] = coordinate  # 因为重复字母在字典里不能存在
            if len(self.letter_coordinate) == len(self.current_word):
                letter_x_coordinate = 0  # 横坐标从0开始
                letter_y_coordinate = 120  # 纵坐标从120开始

    # 该函数的作用是将所有的字母画到主屏幕上
    def draw_Letters(self):
        for key, coordinate in self.letter_coordinate.items():  # 循环读取{字母_顺序：坐标}
            letter_surface = pygame.Surface((60, 60))  # 创建一个字母surface，背景颜色
            letter_surface.fill((210, 210, 210))  # 将背景填充为表格中的颜色
            letter = key.split('_')[0]  # 获得字母
            text_surface = self.font.render(letter, True, self.BLACK)  # 要写的文本，以及字体颜色
            text_rect = text_surface.get_rect()  # 相当于给当前的surface 框起来 这样比较容易获得和使用参数
            letter_surface.blit(text_surface, (30 - text_rect.width / 2, 30 - text_rect.height / 2))  # 将字母放在中间
            self.game_level_surface.blit(letter_surface, (coordinate[0], coordinate[1]))  # 控制画到游戏屏幕的位置

    # 实现画表格的功能, 在画线之前，要判断本次的单词的字母数，以及本关的难度
    def draw_Blocks(self, chance, word_length):
        self.Blocks_Rect = [[] for i in range(chance)]  # 按照行和列把每一个格都框起来
        self.Blocks_Surface = pygame.Surface(
            (word_length * self.BLOCK_SIZE, chance * self.BLOCK_SIZE))  # 创建一个屏幕
        self.Blocks_Surface.fill((210, 210, 210))  # 填充屏幕的颜色

        # 这个循环是画横线的，代表的是给多少次机会
        for j in range(1, chance, 1):
            pygame.draw.line(self.Blocks_Surface, (0, 0, 0), (0, j * self.BLOCK_SIZE),
                             (word_length * self.BLOCK_SIZE, j * self.BLOCK_SIZE), 1)
        # 这个循环是画竖线的，代表的是这个单词有多少个字母
        for i in range(1, word_length, 1):
            pygame.draw.line(self.Blocks_Surface, (0, 0, 0), (i * self.BLOCK_SIZE, 0),
                             (i * self.BLOCK_SIZE, chance * self.BLOCK_SIZE), 1)
        # 获得每一个格子的Rect并存入列表中
        for j in range(chance):
            for i in range(word_length):
                self.Blocks_Rect[j].append(
                    pygame.Rect(i * self.BLOCK_SIZE, j * self.BLOCK_SIZE, self.BLOCK_SIZE, self.BLOCK_SIZE))
        self.game_level_surface.blit(self.Blocks_Surface, (0, 200))

    # 写字功能
    def draw_Menu_Text(self, font, text, size, x, y, COLOR=(0, 0, 0)):
        font = pygame.font.Font(font, size)  # 文本的字体及大小
        text_surface = font.render(text, True, COLOR)  # 默认文本为黑色
        text_rect = text_surface.get_rect()  # 相当于给当前的surface 框起来 这样比较容易获得和使用参数
        text_rect.center = (x, y)  # 文本的中心点的坐标
        self.game_level_surface.blit(text_surface, text_rect)  # 居中对齐
        return text_rect

    # 写字功能
    def draw_Left_Text(self, font, text, size, x, y, COLOR=(0, 0, 0)):
        font = pygame.font.Font(font, size)  # 文本的字体及大小
        text_surface = font.render(text, True, COLOR)  # 默认文本为黑色
        text_rect = text_surface.get_rect()  # 相当于给当前的surface 框起来 这样比较容易获得和使用参数
        text_rect.topleft = (x, y)  # 文本的中心点的坐标
        self.game_level_surface.blit(text_surface, text_rect)  # 左对齐

    # 是否展示汉语翻译以及音标
    def draw_word_parameters(self):
        #  是否展示任务
        if self.tasks_parameters_list[self.task_index][6]:
            self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '当前任务:' +
                                self.tasks_parameters_list[self.task_index][2], 40, 0, 0)
        else:
            pass
        # 是否展示音标
        if self.tasks_parameters_list[self.task_index][7]:
            self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '音标:', 40, 340, 0)
            self.draw_Left_Text("Game_Fonts/phonetic.ttf", self.tasks_parameters_list[self.task_index][1],
                                30, 440, 0)
        else:
            pass
        # 如果玩家按下了Q键，则单词发音
        if self.word_maker.pronunciation:
            game_Sound('UK_Pronunciation/' + self.tasks_parameters_list[self.task_index][0] + '.mp3')

        # 右边的线
        pygame.draw.line(self.game_level_surface, (0, 0, 0), (720, 0), (720, 743), 2)

    # 画当前的关卡需要的时间
    def draw_progress_bar(self, time):
        # 画一个progress bar，控制学习时间，实现2分钟倒计时按钮
        pygame.draw.rect(self.game_level_surface, (0, 0, 0),
                         ((0, self.surface_height - 60), (self.surface_width, 50)),
                         width=4)  # 首先画一个边框
        if self.time_change:
            self.countdown = time  # 将这个单词的任务时间给一个常数
            self.decrease_width = self.surface_width / time  # 1秒减少多少宽度
            self.time_change = False  # 将开关关闭
        self.task_second = time - self.countdown  # 记录学生玩这一关用了多少秒
        if 0 <= self.task_second <= 20:
            pygame.draw.rect(self.game_level_surface, (190, 190, 190),
                             ((self.task_second * self.decrease_width, self.surface_height - 56),
                              (self.surface_width - self.task_second * self.decrease_width, 42)))  # 画进度条
        elif 20 <= self.task_second <= 40:
            pygame.draw.rect(self.game_level_surface, (180, 180, 180),
                             ((self.task_second * self.decrease_width, self.surface_height - 56),
                              (self.surface_width - self.task_second * self.decrease_width, 42)))  # 画进度条
        else:
            pygame.draw.rect(self.game_level_surface, (170, 170, 170),
                             ((self.task_second * self.decrease_width, self.surface_height - 56),
                              (self.surface_width - self.task_second * self.decrease_width, 42)))  # 画进度条

        # 展示任务时长
        self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '任务时长:' +
                            str(self.tasks_parameters_list[self.task_index][5])+'秒', 40, 720, 0)
        # 当前任务难度
        self.draw_Left_Text("Game_Fonts/chinese_pixel_font.TTF", '任务难度:'+str(self.tasks_parameters_list[self.task_index][8])+'级'
                            , 40, 720, 50)
        # 控制单词展示的时间
        if datetime.now() > self.start_time + timedelta(seconds=1):  # 如果时间间隔相差一秒
            self.start_time = datetime.now()  # 将现在的时间给过去的时间
            self.countdown -= 1
            if self.countdown == -1:  # 如果时间结束，则进入游戏界面
                self.time_change = True  # 将开关打开
                self.task_index += 1  # 并且进行到下一个任务
                self.task_change = True  # 时间结束了需要切换单词

    # 展示所有的元素
    def display_menu(self):
        self.game_level_surface.fill(self.word_maker.BGC)  # 游戏的背景颜色
        self.draw_Blocks(self.tasks_parameters_list[self.task_index][3],
                         self.tasks_parameters_list[self.task_index][4])  # 将答题框画到游戏界面上
        self.draw_progress_bar(self.tasks_parameters_list[self.task_index][5])
        if self.task_change:  # 如果时间改变，代表单词改变，所以要重新读取单词
            self.split_Word(self.tasks_parameters_list[self.task_index][0])  # 拆分单词
            self.task_change = False  # 关闭切换任务开关
        self.draw_Letters()  # 往频幕上画字母
        # 展示字母及混淆字母
        self.draw_word_parameters()  # 展示音标和任务
        if self.task_index == len(self.tasks_parameters_list):
            self.task_index = 0
        self.word_maker.window.blit(self.game_level_surface, (0, 0))  # 将游戏界面的内容画到游戏主题上

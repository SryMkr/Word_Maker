import xlrd, xlwt  # 操作excel表格
from numpy import random  # 导入随即包
import pygame


# 获得词库中的所有单词，音标和翻译
def read_xls_shuffle(path):
    task_list = []  # 存放所有任务的英文，音标，中文
    words = []  # 存放单词
    phonetics = []  # 存放音标
    chinese_characters = []  # 存放中文翻译
    workbook = xlrd.open_workbook(path)  # 打开一个workbook
    sheets = workbook.sheet_names()  # 获得工作簿中的所有名字
    worksheet = workbook.sheet_by_name(sheets[0])  # 得到工作簿的第一页
    words_numbers = worksheet.nrows  # 获得第一页的行数
    for word_index in range(words_numbers):
        word_List = [worksheet.cell_value(word_index, 0), worksheet.cell_value(word_index, 1),
                     worksheet.cell_value(word_index, 2)]  # 顺序获得选中单词的英文，音标，和中文
        task_list.append(word_List)  # 将每一行存入到任务列表中
    random.shuffle(task_list)  # 随机每一行的单词顺序
    for i in range(len(task_list)):
        words.append(task_list[i][0])  # 得到英语单词
        phonetics.append(task_list[i][1])  # 得到单词的音标
        chinese_characters.append(task_list[i][2])  # 得到单词的翻译
    return words, phonetics, chinese_characters  # 返回英文，音标，和中文


# pygame.mixer.sound 是用来控制极短的声音，属于独立的游戏模块
def game_Sound(game_sound_path, volume=0.5):
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    sound = pygame.mixer.Sound(game_sound_path)
    sound.set_volume(volume)
    sound.play()


# 获取单词库中的英文，音标，汉语，机会次数，单词长度
def read_tasks_parameters(path):
    task_parameters_list = []  # 存放单词的参数，按照单词一组一个的来
    workbook = xlrd.open_workbook(path)  # 打开一个workbook
    sheets = workbook.sheet_names()  # 获得工作簿中的所有名字
    worksheet = workbook.sheet_by_name(sheets[0])  # 得到工作簿的第一页
    words_numbers = worksheet.nrows  # 获得第一页的行数
    # 英文，音标，汉语，单词长度，机会次数,时间
    for word_index in range(words_numbers):
        parameters_list = [worksheet.cell_value(word_index, 0), worksheet.cell_value(word_index, 1),
                           worksheet.cell_value(word_index, 2), int(worksheet.cell_value(word_index, 3)),
                           int(worksheet.cell_value(word_index, 4)), int(worksheet.cell_value(word_index, 5)),
                           int(worksheet.cell_value(word_index, 6)), int(worksheet.cell_value(word_index, 7)),
                           int(worksheet.cell_value(word_index, 8)), int(worksheet.cell_value(word_index, 9))]
        task_parameters_list.append(parameters_list)
    print(task_parameters_list)
    return task_parameters_list


# 如果玩家最难的的关过了，那么将该单词删除任务库
def remove_tasks_xls(path, wordlist):
    i = 0
    # open workbook
    workbook = xlrd.open_workbook(path)
    # get all sheets by sheet names
    sheets = workbook.sheet_names()
    # get the first sheet
    worksheet = workbook.sheet_by_name(sheets[0])
    # 创建一个空的表格
    new_workbook = xlwt.Workbook()
    # 创建一个空的表单
    new_worksheet = new_workbook.add_sheet('sheet1')
    # 得到所有单词
    words = worksheet.col_values(0)
    # 如果已经记住的单词在原来的单词表中
    for word in words:
        if word not in wordlist:
            # 取得这个单词在原单词表中的索引
            word_index = words.index(word)
            # 根据索引得到这个值
            values = worksheet.row_values(word_index)
            # 将这个单词所有参数写入新的表格中
            for value_index in range(len(values)):
                new_worksheet.write(i, value_index, values[value_index])
            i = i + 1
    # save file
    new_workbook.save(path)

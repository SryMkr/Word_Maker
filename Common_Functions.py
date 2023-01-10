'''
定义难度关卡，将单词和难度关卡进行组合，自动化生成关卡

'''


import xlrd, xlwt  # 操作excel表格
from numpy import random  # 导入随即包
import pygame
from xlutils.copy import copy
import numpy as np


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


# 获取单词库中的英文，音标，汉语，机会次数，单词长度，以及标记,各种参数
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
                           int(worksheet.cell_value(word_index, 8)), int(worksheet.cell_value(word_index, 9)),
                           str(worksheet.cell_value(word_index, 10))]
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


# 首先读取游戏的学习参数（session的标记代码）,并读取到游戏中以方便修改
def read_excel_game_record(path):
    game_record_list = []  # create a empty list
    workbook = xlrd.open_workbook(path)  # open workbook
    sheets = workbook.sheet_names()  # get all sheets by sheet names
    worksheet = workbook.sheet_by_name(sheets[0])  # get the first sheet
    # get the correspond content
    session_number = worksheet.cell_value(1, 0)  # （1，0）代表session number
    game_record_list.append(session_number)  # add the record into the list
    # return the record list
    return game_record_list


# 写入游戏的学习参数（session的标记代码）,每次结束游戏都要写入，values是一个list
def write_excel_game_record(path, values):
    workbook = xlrd.open_workbook(path)  # open a workbook
    new_workbook = copy(workbook)  # copy the workbook
    new_worksheet = new_workbook.get_sheet(0)  # get the first worksheet
    new_worksheet.write(1, 0, values[0])  # 第二行第一列是session number
    # 每次写文件都需要创建新文件然后覆盖原文件
    new_workbook.save(path)


# 将已经记住的单词添加到对应的表单中,第一个参数到底是哪个文件,第二个参数写入 英文，音标，汉语，单词的label，逐个单词输入
def write_leaned_words_xls(session_label, word_parameters):
    path = 'Word_Pool/session_' + str(session_label) + '.xls' # 说先确定path是什么，应该写入到哪个文件
    workbook = xlrd.open_workbook(path)  # 打开这个文件
    sheets = workbook.sheet_names()  # get all sheet names
    worksheet = workbook.sheet_by_name(sheets[0])  # get the first sheet
    rows_old = worksheet.nrows  # get the rows of sheet # 这个值就是紧接着的那个空位
    # 得到第一列的值，第一列是单词 用来判断学会的单词在不在这个单词库中
    words = worksheet.col_values(0)
    new_workbook = copy(workbook)  # copy the workbook
    new_worksheet = new_workbook.get_sheet(0)  # get the first worksheet
    # 如果单词不在单词库中
    if word_parameters[0] not in words:
        for index in range(len(word_parameters)):
            new_worksheet.write(rows_old, index, word_parameters[index])
    else:  # 如果已经在单词库中，找到对应的那行索引，然后修改
        # 取得这个单词在原单词表中的索引
        word_index = words.index(word_parameters[0])
        # 第三列是标记
        new_worksheet.write(word_index, 3, word_parameters[3])
    # save file
    new_workbook.save(path)


# 将已经学会的单词移入到对应的单词库 (单词，音标，汉语，标记)
def write_learned_words_to_file(learned_tasks, current_session_label):
    # 定义一个所有文件的文件label
    file_label_list = ['0259', '1360', '2471', '3582', '4693', '5704', '6815', '7962', '8037', '9148']
    session_label = ''  # 随便初始化参数
    # 取得文件的最后一位字母看看是不是已经学习结束
    if learned_tasks[3] != 'new':
        final_label_split = learned_tasks[3].split('_')
        final_number = final_label_split[0][3]  # 取得最后一位数字
    #  第一新单词添加到session开头的文件,第十个是标记
    if learned_tasks[3] == 'new':
       # 接下来要找到底是哪个文件
        for file_label in file_label_list:
            if current_session_label == str(file_label[0]):  # 如果当前这个session和文件名的第一个相等
                session_label = file_label  # 就把当前的这个文件民给session label
                learned_tasks[3] = file_label + '_' + file_label[0]
        # 并将不会的从不会的库里的单词删除
        remove_task_from_original('Word_Pool/unknown_deck.xls', learned_tasks[0])
    elif str(final_number) == str(current_session_label):  # 也就是说已经复习过三次了
        session_label = 'retired'  # 直接移动到淘汰库，保存learned task里面的所有数据
        remove_task_from_original('Word_Pool/session_' + final_label_split[0] + '.xls', learned_tasks[0])
        # 并将已经学会的单词从那个session删除
    else:  # 如果处于中间阶段
        session_label = final_label_split[0]  # 如果还没学习结束，则还在这个文件中
        # 还要将标记修改为下一位数字 找到当前的这个session在文件名中的索引，并修改为下一位
        index = final_label_split[0].find(final_label_split[1])
        learned_tasks[3] = session_label + '_' + final_label_split[0][index+1]
    print(session_label, learned_tasks)
    return session_label, learned_tasks


# 要找到这个单词的原始文件，然后将这个单词从文件中删除，因为已经移到了另外一个库
def remove_task_from_original(path, remembered_word):
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
    # 删除这行的所有数据
    for word in words:
        if word != remembered_word:
            # 直接找到对应的单词的索引
            word_index = words.index(word)
            # 根据索引得到这个值
            values = worksheet.row_values(word_index)
            # 将这个单词所有参数写入新的表格中
            for value_index in range(len(values)):
                new_worksheet.write(i, value_index, values[value_index])
            i = i + 1
    # save file
    new_workbook.save(path)


#  首先往current_deck里面写单词 以及往game_level里面写单词
def select_tasks(current_session_label):
    # 定义一个所有文件的文件label,因为要找到所有对应的文件
    file_label_list = ['0259', '1360', '2471', '3582', '4693', '5704', '6815', '7962', '8037', '9148']
    tasks_list = []  # 存放所有的任务单词
    for file_label in file_label_list:  # 遍历列表
        if str(current_session_label) in file_label:  # 如果文件包含当前的session_label
            path = 'Word_Pool/session_' + file_label + '.xls'  # 直接组成对应path
            workbook = xlrd.open_workbook(path)  # 打开一个对应workbook
            sheets = workbook.sheet_names()  # 获得工作簿中的所有名字
            worksheet = workbook.sheet_by_name(sheets[0])  # 得到工作簿的第一页
            nrows = worksheet.nrows  # 获取该表总行数
            if nrows != 0:  # 如果这个文件中有单词，如果小于三就全部读取，如果大于三，则随机挑选三个
                if 0 <nrows <= 3:
                    for i in range(nrows):
                            tasks_list.append(worksheet.row_values(i)) # 将该行所有元素添加到列表中
                else: # 随机选择三行添加到任务列表中
                   a = [i for i in range(nrows)]  # 将行数弄成一个列表
                   index_review_list = np.random.choice(a, 3, replace = False)  # 不重复抽验
                   for index in index_review_list:
                       tasks_list.append(worksheet.row_values(index))
    # 以上是先从复习的模式中挑选，接下来要从不会的库中挑选
    review_number = len(tasks_list)  # 看复习模式中有几个单词
    learn_number = 10 - review_number  # 每次学习10个单词，减去复习模式，就是新学习的单词数量
    path = 'Word_Pool/unknown_deck.xls'  # 直接是对应的不会的单词库
    workbook = xlrd.open_workbook(path)  # 打开一个对应workbook
    sheets = workbook.sheet_names()  # 获得工作簿中的所有名字
    worksheet = workbook.sheet_by_name(sheets[0])  # 得到工作簿的第一页
    nrows = worksheet.nrows  # 获取该表总行数
    # 万一学习库中的单词不够数量，就全部提取
    if 0 < nrows < learn_number:
        for i in range(nrows):
            tasks_list.append(worksheet.row_values(i))
    else:  # 如果数量充足
        b = [i for i in range(nrows)]  # 将行数弄成一个列表
        index_list = np.random.choice(b, learn_number, replace=False)  # 不重复抽验
        for index in index_list:
            tasks_list.append(worksheet.row_values(index))
    print(tasks_list)
    # 将tasks_list文件中的内容存入到current_deck中
    path = 'Word_Pool/Current_Deck.xls'  # 要保存的列表
    task_workbook = xlrd.open_workbook(path)  # 打开一个对应workbook
    new_workbook = copy(task_workbook)  # copy the workbook
    new_worksheet = new_workbook.get_sheet(0)  # get the first worksheet
    word_index = 0
    for task in tasks_list:
        new_worksheet.write(word_index, 0, task[0])
        new_worksheet.write(word_index, 1, task[1])
        new_worksheet.write(word_index, 2, task[2])
        word_index += 1
        # save file
    new_workbook.save(path)
    # 将tasks_list文件中的内容存入到game_level里面写任务
    path = 'Word_Pool/Current_Deck.xls'  # 要保存的列表
    task_workbook = xlrd.open_workbook(path)  # 打开一个对应workbook
    new_workbook = copy(task_workbook)  # copy the workbook
    new_worksheet = new_workbook.get_sheet(0)  # get the first worksheet
    word_index = 0
    for task in tasks_list:
        new_worksheet.write(word_index, 0, task[0])
        new_worksheet.write(word_index, 1, task[1])
        new_worksheet.write(word_index, 2, task[2])
        word_index += 1
        # save file
    new_workbook.save(path)

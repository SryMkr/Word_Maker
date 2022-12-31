'''
只提供打分，要求音频格式为.WAV
'''


# 导入所需要的包
import sys
import uuid
import requests
import wave
import base64
import hashlib
import json
from importlib import reload
import time

reload(sys)  # 重新加载之前载入的模块 但是不重新载入会怎么样了？

YouDao_URL = "https://openapi.youdao.com/iseapi"  # 要使用的有道API网址
APP_KEY = '3d96861d86e5d1eb'  # 我的应用ID
APP_SECRET = '0wq0M3dYpvMhlgpzgcTv6MyWLCn7ou0A'  # 我的应用密钥


# 要评测的音频文件的Base64编码字符串 [.wav→编码]
def truncate(q):
    # 如果字符串为空值，那么返回空值
    if q is None:
        return None
    # 然后判断字符串的长度
    size = len(q)
    # 如果长度小于20 input直接为20 如果字符串长度大于20 字符串等于【前十个字符】+【字符串的长度】+【后10个字符串】
    return q if size <= 20 else q[0:10] + str(size) + q[size-10:size]


# 将字符串用hash算法加密
def encrypt(signStr):
    hash_algorithm = hashlib.sha256()  # 生成一个公式
    hash_algorithm.update(signStr.encode('utf-8'))  # 用上面的公式将字符串编码
    return hash_algorithm.hexdigest()  # 返回编码后的一串字符串


# 发送请求有一系列固定的东西
def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}  # 这个头部是固定的东西
    # 第一个参数发送的URL,第二个参数data里一些固定的东西，第三个就是头部一些参数 就是将各部分链接起来，发送URL链接
    return requests.post(YouDao_URL, data=data, headers=headers)


# 这个是主要的代码 输入的参数是 第一个参数是玩家的发音路径，第二个单词的的字符串
def connect(audio_file_path, word_text):
    audio_file_path = audio_file_path  # 玩家发音文件的路径
    lang_type = 'en'  # 源语言类型，就是英文
    #  rindex() 返回子字符串 str 在字符串中最后出现的位置 其实就是获得文件的拓展名 可是不就是 .wav么
    extension = audio_file_path[audio_file_path.rindex('.')+1:]
    if extension != 'wav':
        print('不支持的音频类型')
        sys.exit(1)
    wav_info = wave.open(audio_file_path, 'rb')  # 打开音频文件
    sample_rate = wav_info.getframerate()  # 获得音频的采样率
    nchannels = wav_info.getnchannels()  # 获得音频的声道
    wav_info.close()  # 关闭文件
    with open(audio_file_path, 'rb') as file_wav:
        q = base64.b64encode(file_wav.read()).decode('utf-8')  # 要评测的音频文件的Base64编码字符串
    data = {}  # 创建一个data的字典，要发送到url进行打分
    data['text'] = word_text  # 要评测的音频文件对应的拼写
    curtime = str(int(time.time()))  # 获得当前开始的时间戳（秒）
    data['curtime'] = curtime  # # 获得当前开始的时间戳（秒）
    salt = str(uuid.uuid1())  # 唯一通用识别码 就是全球唯一的一个标志而已
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET  # 一个签名的原始组成
    sign = encrypt(signStr)  # 将这个签名使用hash算法编码
    data['appKey'] = APP_KEY # 应用ID
    data['q'] = q  # 就是q的值
    data['salt'] = salt  # 唯一通用识别码
    data['sign'] = sign  # hash转换后的值
    data['signType'] = "v2"  # 签名类型
    data['langType'] = lang_type  # 语言类型，只支持英文
    data['rate'] = sample_rate  # 采样率16000
    data['format'] = 'wav'  # 文件类型wav
    data['channel'] = nchannels  # 声道数， 仅支持单声道，请填写固定值1
    data['type'] = 1  # 上传类型， 仅支持base64上传，请填写固定值1

    response = do_request(data)  # 发送打分请求
    j = json.loads(str(response.content, encoding="utf-8"))  # 返回一个json文件，就是返回的结果
    word = j["words"]  # 获得有关单词的所有信息，返回的是个列表
    word = word[0]  # 0代表去除列表，我就只有一个单词
    word_information_list = []   # 创建一个列表顺序保存所有的数据
    pronunciation_score = int(word['pronunciation'])  # 单词的整体发音分数
    word_information_list.append(pronunciation_score)
    word_phonemes = word['phonemes']  # 获得单词的因素
    for phonemes_index in range(len(word_phonemes)):  # 顺序循环单词的所有音素
        phonemes_list = []
        current_phoneme = word_phonemes[phonemes_index]["phoneme"]  # 当前的音素
        phonemes_list.append(current_phoneme)
        phoneme_pronunciation = int(word_phonemes[phonemes_index]['pronunciation'])  # 获得这个音素的发音分数
        phonemes_list.append(phoneme_pronunciation)
        phoneme_judge = word_phonemes[phonemes_index]["judge"]  # 判断当前的音素发音是否正确
        phonemes_list.append(phoneme_judge)
        word_information_list.append(phonemes_list)
    # 【word,[w,12,True],[o,11,False],.......】
    return word_information_list

# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/21 16:01
# @File    : logger_config.py
# @Software: PyCharm
# logger_config.py 中心化配置日志

import logging

import colorlog
from colorlog import ColoredFormatter

# 创建一个logger
logger = logging.getLogger('IH-monitor-log')
logger.setLevel(logging.DEBUG)

# 创建一个handler，将日志写入到文件中
file_handler = logging.FileHandler('IH-monitor-log.log')
file_handler.setLevel(logging.DEBUG)

# 创建一个handler，用于在控制台中输出日志
console_handler = colorlog.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 设置日志格式
# 日志格式还得加一个线程名字
formatter = ColoredFormatter('%(asctime)s - %(threadName)s - %(filename)s - %(levelname)s - %(message)s',
                             )

formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(threadName)s - %(filename)s - %(levelname)s - %(message)s",
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
# 将handler添加到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

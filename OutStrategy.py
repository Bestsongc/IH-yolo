# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/19 11:29
# @File    : OutStrategy.py
# @Software: PyCharm
# 步骤1：定义策略接口
import threading
from abc import ABC, abstractmethod
import time
import cv2

from main import logger


class VideoOutStrategy(ABC):
    @abstractmethod
    def execute(self, frame):
        pass


# 步骤2：创建具体策略类
'''
写入本地flv
'''


class VideoOutStrategy_write_local_flv(VideoOutStrategy):
    # 用构造函数初始化时候传入out
    def __init__(self, out):
        self.out = out

    def execute(self, frame):
        # 写入flv作为本地视频
        self.out.write(frame)


'''
在本机实时显示
'''


class VideoOutStrategy_showCV2(VideoOutStrategy):
    def execute(self, frame):
        cv2.imshow('window_' + str(threading.current_thread().name), frame)


'''
推流rtmp流
'''


class VideoOutStrategy_push_rtmp(VideoOutStrategy):
    def __init__(self, pipe_ffmpeg):
        self.pipe_ffmpeg = pipe_ffmpeg

    def execute(self, frame):
        try:
            self.pipe_ffmpeg.stdin.write(frame.tobytes())
        except BrokenPipeError as e:
            print('捕捉到BrokenPipeError，退出程序')
            logger.critical('捕捉到BrokenPipeError，退出程序')
            exit()


# 自动关闭策略
class AutoCloseStrategy(VideoOutStrategy):
    def __init__(self, start_time, auto_close_time):
        self.start_time = start_time
        self.auto_close_time = auto_close_time

    def execute(self, frame):
        if time.time() - self.start_time > self.auto_close_time:
            print('超过30s，自动关闭')
            logger.critical('超过30s，自动关闭')
            exit()



# 步骤3：创建上下文类
class VideoOutContext:
    def __init__(self):
        self.strategies = []

    def add_strategy(self, strategy: VideoOutStrategy):
        self.strategies.append(strategy)

    def handle_frame(self, frame):
        for strategy in self.strategies:
            strategy.execute(frame)

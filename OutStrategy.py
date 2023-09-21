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
    def do_out(self, frame):
        pass

# 步骤2：创建具体策略类
'''
写入本地flv
'''
class VideoOutStrategy_write_local_flv(VideoOutStrategy):
    # 用构造函数初始化时候传入out
    def __init__(self,out):
        self.out = out
    def do_out(self, frame):
        # 写入flv作为本地视频
        self.out.write(frame)
'''
在本机实时显示
'''
class VideoOutStrategy_showCV2(VideoOutStrategy):
    def do_out(self, frame):
        cv2.imshow('window_' + str(threading.current_thread().name), frame)

'''
推流rtmp流
'''
class VideoOutStrategy_push_rtmp(VideoOutStrategy):
    def __init__(self,pipe_ffmpeg):
        self.pipe_ffmpeg = pipe_ffmpeg
    def do_out(self, frame):
        self.pipe_ffmpeg.stdin.write(frame.tobytes())

# 自动关闭策略
class AutoCloseStrategy(VideoOutStrategy):
    def __init__(self, start_time, close_time):
        self.start_time = start_time
        self.close_time = close_time

    def execute(self, frame):
        if time.time() - self.start_time > self.close_time:
            print('超过30s，自动关闭')
            logger.critical('超过30s，自动关闭')
            raise AutoCloseException("Time Exceeded!")

class AutoCloseException(Exception):
    pass

# 步骤3：创建上下文类
class VideoOutContext:
    def __init__(self):
        self.strategies = []

    def add_strategy(self, strategy: VideoOutStrategy):
        self.strategies.append(strategy)

    def handle_frame(self, frame):
        for strategy in self.strategies:
            try:
                strategy.execute(frame)
            except AutoCloseException:
                raise



# 客户端代码
if __name__ == "__main__":

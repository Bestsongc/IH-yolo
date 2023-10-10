# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/10 9:27
# @File    : handler_abnormal_strategy.py
# @Software: PyCharm
from abc import ABC, abstractmethod


class HandlerAbnormalStrategy(ABC):
    '''
    处理异常策略
    '''

    @abstractmethod
    def execute(self, frame):
        pass

class HandlerAbnormalStrategyUploadScreenshot(HandlerAbnormalStrategy):
    '''
    上传异常的视频截图至服务器
    '''
    def execute(self, frame):
        # TODO
        pass


class HandlerAbnormalStrategyNewIdentifier(HandlerAbnormalStrategy):
    '''
    单独新开辟一条推理线程，并作为一条视频数据源不断输出到SRS
    '''
    def execute(self, frame):
        # TODO
        pass


class HandlerAbnormalStrategyUploadInformation(HandlerAbnormalStrategy):
    '''
    上传异常信息至服务器
    '''
    def execute(self, frame):
        # TODO
        pass


class HandlerAbnormalContext:
    def __init__(self):
        self.strategy = []

    def add_strategy(self, strategy):
        '''
        添加策略
        Args:
            strategy ():

        Returns:

        '''
        self.strategy.append(strategy)

    def execute(self, frame):
        '''
        执行策略
        Args:
            frame ():

        Returns:

        '''
        for strategy in self.strategy:
            strategy.execute(frame)

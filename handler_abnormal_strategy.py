# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/10 9:27
# @File    : handler_abnormal_strategy.py
# @Software: PyCharm
import threading
import time
from abc import ABC, abstractmethod
from rtmp_pusher import RtmpPusher
from rtsp_receiver import RtspReceiver
from logger_config import logger
from yolo_inductor import YoloInductor
from yolo_identifier import YoloIdentifier

class HandlerAbnormalStrategy(ABC):
    '''
    处理异常策略
    '''

    @abstractmethod
    def execute(self, frame, source_receiver: RtspReceiver, target_rtmp):
        pass


class HandlerAbnormalStrategyUploadScreenshot(HandlerAbnormalStrategy):
    '''
    上传异常的视频截图至服务器
    '''

    def execute(self, frame, source_receiver, target_rtmp):
        # TODO
        pass


class HandlerAbnormalStrategyNewIdentifier(HandlerAbnormalStrategy):
    '''
    新建一个识别线程
    '''
    def __init__(self,args):
        self.args = args

    def execute(self, frame, source_receiver, target_rtmp):
        '''
        单独新开辟一条推理线程，并作为一条视频数据源不断输出到SRS
        1.如果这个receiver对应的camera_id还没有被单独开辟过推理线程，则新开辟
        2.如果这个receiver对应的camera_id已经被单独开辟过推理线程，则不新开辟
        Args:
            frame ():
            source_receiver ():
            target_rtmp ():

        Returns:

        '''
        if(True):#TODO 判断这个receiver对应的camera_id还没有被单独开辟过推理线程
            identifier_thread = threading.Thread(target=lambda: YoloIdentifier(self.args,source_receiver, target_rtmp).process_stream_and_push())
            identifier_thread.name = f'identifier_camera{source_receiver.get_camera_id()}_thread'
            identifier_thread.start()
            logger.info(f'---新启动一条推理线程{source_receiver.get_source()}->{target_rtmp}---')
        #TODO 也许可以通过修改对象引用identifiers[]来实现删除线程的功能

class HandlerAbnormalStrategyUploadInformation(HandlerAbnormalStrategy):
    '''
    上传异常信息至服务器
    '''

    def execute(self, frame, source_receiver, target_rtmp):
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

    def execute(self, frame, source_receiver, target_rtmp):
        '''
        执行策略
        Args:
            frame ():

        Returns:

        '''
        for strategy in self.strategy:
            strategy.execute(frame, source_receiver, target_rtmp)

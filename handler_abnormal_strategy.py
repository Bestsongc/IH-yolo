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
    def execute(self, frame, **kwargs):
        pass


class HandlerAbnormalStrategyUploadScreenshot(HandlerAbnormalStrategy):
    '''
    上传异常的视频截图至服务器
    '''

    def execute(self, frame, **kwargs):
        # TODO
        pass


class HandlerAbnormalStrategyNewIdentifier(HandlerAbnormalStrategy):
    '''
    新建一个识别线程
    '''

    def __init__(self, args,abnormal_items):
        self.args = args
        self.abnormal_items = abnormal_items

    def execute(self, frame, **kwargs):
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
        source_receiver : RtspReceiver = kwargs['source_receiver']
        target_rtmp = kwargs['target_rtmp']
        identifier_poll= kwargs['identifier_poll']
        identifiers: dict = kwargs['identifiers']
        # 判断这个receiver对应的camera_id还没有被单独开辟过推理线程
        if source_receiver.get_camera_id() not in identifiers:
            logger.info(f'---开始启动camera_id:{source_receiver.get_camera_id()}的identifier---')
            # 1.初始化
            identifier  = YoloIdentifier(self.args, self.abnormal_items,source_receiver, target_rtmp)
            # 2.将这个对象入到字典中
            identifiers[source_receiver.get_camera_id()] = identifier
            # 3.启动这个推理进程
            # identifier_poll.apply_async(func=identifier.process_stream_and_push())#TODO
            identifier_poll.submit(identifier.process_stream_and_push())
            logger.info(f'---成功启动camera_id:{source_receiver.get_camera_id()}的identifier---')


class HandlerAbnormalStrategyUploadInformation(HandlerAbnormalStrategy):
    '''
    上传异常信息至服务器
    '''

    def execute(self, frame, **kwargs):
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

    def execute(self, frame, **kwargs):
        '''
        执行策略
        Args:
            frame ():

        Returns:

        '''
        for strategy in self.strategy:
            strategy.execute(frame, **kwargs)

if __name__ == '__main__':
    pass
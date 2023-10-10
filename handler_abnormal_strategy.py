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
        threading.Thread(target=lambda: self.process_stream_and_push(args, source_rtsp, target_rtmp)).start()



    def process_stream_and_push(self, args, receiver: RtspReceiver, target_rtmp):
        yolo_inductor = YoloInductor(args)
        # 最大持续识别时间(单位:秒)
        identifier_max_duration = args.IDENTIFIER_MAX_DURATION
        rtmp_pusher = RtmpPusher(args,target_rtmp) #TODO
        start_time = time.time()
        try:
            while True:
                is_abnormal = False
                # 获取画面
                status, frame = receiver.read()

                if not status:  # 如果获取画面不成功，则退出
                    logger.error('status is false,need waiting')
                    time.sleep(1)
                    continue
                # 逐帧处理
                try:
                    frame, is_abnormal = yolo_inductor.process_frame(frame)
                except Exception as error:
                    logger.error('process_frame报错！', error)


                # 将frame推送到rtmp
                    rtmp_pusher.push() #TODO

                # 自动退出功能
                # 如果此后identifier_max_duration内没有异常，则退出
                if not is_abnormal:
                    if time.time() - start_time > identifier_max_duration:
                        break
                else:
                    start_time = time.time()

        except Exception as error:
            print('中途中断 %s', str(error))
            logger.error('中途中断:%s', str(error))



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

# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/8 15:47
# @File    : yolo_manager.py
# @Software: PyCharm
import concurrent.futures

import cv2

from handler_abnormal_strategy import HandlerAbnormalContext, HandlerAbnormalStrategyUploadScreenshot, \
    HandlerAbnormalStrategyNewIdentifier, HandlerAbnormalStrategyUploadInformation
from logger_config import logger
from rtsp_receiver import RtspReceiver
from yolo_inductor import YoloInductor
import yolo_config

class YoloManager:
    def verify_args(self, args):
        '''
        验证参数
        Returns:

        '''
        if not (0 < args.CONF_THRES <= 1):
            logger.error("--CONF_THRES 请输入0~1的数！")
            exit(0)

        if not (0 < args.IOU_THRES <= 1):
            logger.error("--IOU_THRES 请输入0~1的数！")
            exit(0)


    def __init__(self):
        # self.verify_args(args)
        logger.info('---YoloManager初始化---')
        logger.info('yolo_config.arguments:'+str(yolo_config.arguments))
        logger.info('yolo_config.url_list:'+str(yolo_config.url_list))
        self.args = yolo_config.arguments
        self.url_list = yolo_config.url_list
        self.rtsp_list = []
        for url in yolo_config.url_list:
            self.rtsp_list.append(url['camera_rtsp_url'])

        self.receivers = self.start_receivers(self.rtsp_list)


    def start_receivers(self, rtsp_list, max_workers=10):
        """
        启动接收器
        :param rtsp_list: rtsp地址列表
        :return:

        Args:
            max_workers ():
        """
        # TODO 创建一个线程池来优化
        # with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        #     # 使用线程池实例化多个 RtspReceiver 对象
        #     receivers = [executor.submit(RtspReceiver, url) for url in rtsp_list]
        #     # 等待所有线程完成
        # return receivers

        # 法2.简单多线程
        receivers = []
        for url in rtsp_list:
            receiver = RtspReceiver(url)
            receivers.append(receiver)
        return receivers
    def update_receivers(self,rtsp_list,max_workers=10):
        # TODO
        pass

    def start_detect(self):
        """
        启动轮询检测器
        将轮询检查每个接收器的状态，如果有异常则启动单独的持续推理
        :return:
        """
        yoloInductor = YoloInductor()
        #设置处理异常策略
        # 2.1.上传异常的视频截图至服务器，
        # 2.2.单独新开辟一条推理线程，并作为一条视频数据源不断输出到SRS
        # 2.3.需要异常信息放入数据库
        handler_abnormal_context = HandlerAbnormalContext()
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyUploadScreenshot())
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyNewIdentifier())
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyUploadInformation())
        while True:
            for i, receiver in self.receivers:
                status, frame = receiver.read()
                logger.info(f'---{i}:收到frame--')
                if status:
                    # 1.使用yolo推理
                    frame , is_abnormal = yoloInductor.process_frame(frame)
                    # 2.如果出现异常
                    if is_abnormal:
                        handler_abnormal_context.execute(frame)
                    # 3.如果没有异常则跳过
                    else:
                        pass
                else:
                    logger.error(f'---{i}:收到frame失败--')
                    pass

if __name__ == '__main__':
    manager = YoloManager()
    manager.start_detect()
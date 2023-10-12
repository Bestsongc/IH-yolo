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
import sys


class YoloManager:
    def verify_args(self, args):
        '''
        验证参数
        Returns:

        '''

        if (not (0 < args['CONF_THRES'] <= 1)) or (not isinstance(args['CONF_THRES'], float)):  # 条件2判断为浮点数
            logger.error("--CONF_THRES 请输入0~1的数！")
            sys.exit()

        if (not (0 < args['IOU_THRES'] <= 1)) or (not isinstance(args['IOU_THRES'], float)):  # 条件2判断为浮点数
            logger.error("--IOU_THRES 请输入0~1的数！")
            sys.exit()

        if (not isinstance(args['OUTPUT_FRAME_WIDTH'], int)):
            logger.error("--OUTPUT_FRAME_WIDTH 请输入整数！")
            sys.exit()
        if (not isinstance(args['OUTPUT_FRAME_HEIGHT'], int)):
            logger.error("--OUTPUT_FRAME_HEIGHT 请输入整数！")
            sys.exit()
        if (not isinstance(args['IDENTIFIER_MAX_DURATION'], int)):
            logger.error("--IDENTIFIER_MAX_DURATION 请输入整数！")
            sys.exit()

        logger.info('---参数验证通过---')

    def __init__(self):
        # self.verify_args(args)
        logger.info('---YoloManager初始化---')
        logger.info('yolo_config.arguments:' + str(yolo_config.arguments))
        logger.info('yolo_config.cameras:' + str(yolo_config.cameras))
        self.args = yolo_config.arguments
        self.cameras = yolo_config.cameras
        # self.rtsp_list = []
        # for url in yolo_config.cameras:
        #     self.rtsp_list.append(url['camera_rtsp_url'])
        self.rtmp_list = []
        for url in yolo_config.cameras:
            self.rtmp_list.append(url['srs_rtmp_url'])
        self.receivers = self.init_receivers(self.cameras)
        self.identifiers = []

    def init_receivers(self, cameras, max_workers=10):
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
        for camera in cameras:
            camera_id=None
            try:
                camera_rtsp_url = camera['camera_rtsp_url']
                camera_id = camera['camera_id']
                receivers.append(RtspReceiver(camera_rtsp_url, camera_id))
                logger.info(f'---成功添加camera_id:{camera_id}的接收器---')
            except Exception as e:
                logger.error(f'---camera_id:{camera_id}的接收器启动失败---')
                logger.error(f'---{e}---')
                continue
        logger.info(f'---成功启动{len(receivers)}个接收器---')
        return receivers

    def add_receivers(self, camera)->str:
        '''
        添加接收器
        Args:
            camera ():

        Returns:

        '''
        camera_id=None
        try:
            camera_rtsp_url = camera['camera_rtsp_url']
            camera_id = camera['camera_id']
            self.receivers.append(RtspReceiver(camera_rtsp_url, camera_id))
            logger.info(f'---成功添加camera_id:{camera_id}的接收器---')
            return "success"
        except Exception as e:
            logger.error(f'---camera_id:{camera_id}的接收器启动失败---')
            logger.error(f'---{e}---')
            return "fail"

    def update_receivers(self, rtsp_list, max_workers=10):
        # TODO
        pass

    def start_detect(self):
        """
        启动轮询检测器
        将轮询检查每个接收器的状态，如果有异常则启动单独的持续推理
        :return:
        """
        yoloInductor = YoloInductor(yolo_config.arguments)
        # 设置处理异常策略
        # 2.1.上传异常的视频截图至服务器，
        # 2.2.单独新开辟一条推理线程，并作为一条视频数据源不断输出到SRS
        # 2.3.需要异常信息放入数据库
        handler_abnormal_context = HandlerAbnormalContext()
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyUploadScreenshot())
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyNewIdentifier(yolo_config.arguments))
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyUploadInformation())
        logger.info('---成功创建YoloInductor,开始轮询检测异常---')
        while True:
            for i, receiver in enumerate(self.receivers):
                status, frame = receiver.read()
                logger.info(f'---receiver:{i}:收到frame--')
                if status:
                    # 1.使用yolo推理
                    frame, is_abnormal = yoloInductor.process_frame(frame)
                    # 2.如果出现异常
                    if is_abnormal:
                        rtmp_url = self.rtmp_list[i]
                        handler_abnormal_context.execute(frame, receiver, rtmp_url)
                    # 3.如果没有异常则跳过
                    else:
                        pass
                else:
                    logger.error(f'---{i}:收到frame失败--')
                    pass


if __name__ == '__main__':
    manager = YoloManager()
    manager.start_detect()

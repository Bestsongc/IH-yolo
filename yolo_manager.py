# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/8 15:47
# @File    : yolo_manager.py
# @Software: PyCharm
import concurrent.futures
import threading

import cv2

from handler_abnormal_strategy import HandlerAbnormalContext, HandlerAbnormalStrategyUploadScreenshot, \
    HandlerAbnormalStrategyNewIdentifier, HandlerAbnormalStrategyUploadInformation
from logger_config import logger
from rtsp_receiver import RtspReceiver
from yolo_inductor import YoloInductor
import yolo_config
import sys
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

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
        self.abnormal_items = yolo_config.abnormal_items
        # self.identifier_poll = multiprocessing.Pool(processes=self.args['MAX_IDENTIFIER_NUM']) 进程池太恶心了
        self.identifier_poll = ThreadPoolExecutor(max_workers = self.args['MAX_IDENTIFIER_NUM'])
        self.receiver_update_thread_pool = ThreadPoolExecutor(max_workers=self.args['MAX_RECEIVER_UPDATE_NUM'])  # TODO
        # 可重入锁
        self.receivers_lock = threading.RLock()
        self.receivers: dict = self.init_receivers(self.cameras)
        self.identifiers: dict = {}


    def init_receivers(self, cameras) -> dict:
        """
        启动接收器
        :param rtsp_list: rtsp地址列表
        :return:

        Args:
            cameras ():
            max_workers ():
        """
        # 优化法1.创建一个线程池来优化
        # 优化2.使用dict来存储receiver
        receivers = {}
        for camera in cameras:
            camera_id = None
            try:
                camera_rtsp_url = camera['camera_rtsp_url']
                camera_id = camera['camera_id']
                receivers[camera_id] = RtspReceiver(camera_rtsp_url, camera_id)
                self.receiver_update_thread_pool.submit(lambda r: r.update(), receivers[camera_id])
                logger.info(f'---成功添加camera_id:{camera_id}的接收器---')
            except Exception as e:
                logger.error(f'---camera_id:{camera_id}的接收器启动失败---')
                logger.error(f'---{e}---')
                continue
        return receivers
        # # 法2.简单多线程
        # receivers = []
        # for camera in cameras:
        #     camera_id = None
        #     try:
        #         camera_rtsp_url = camera['camera_rtsp_url']
        #         camera_id = camera['camera_id']
        #         receivers.append(RtspReceiver(camera_rtsp_url, camera_id))
        #         logger.info(f'---成功添加camera_id:{camera_id}的接收器---')
        #     except Exception as e:
        #         logger.error(f'---camera_id:{camera_id}的接收器启动失败---')
        #         logger.error(f'---{e}---')
        #         continue
        # logger.info(f'---成功启动{len(receivers)}个接收器---')
        # return receivers

    def add_receivers(self, camera) -> str:
        '''
        添加接收器
        Args:
            camera ():

        Returns:

        '''
        camera_id = None
        try:
            logger.info(f'---开始添加camera_id:{camera_id}的接收器---')
            # 加锁
            self.receivers_lock.acquire()
            camera_rtsp_url = camera['camera_rtsp_url']
            camera_id = camera['camera_id']
            self.receivers[camera_id] = RtspReceiver(camera_rtsp_url, camera_id)
            self.receiver_update_thread_pool.submit(lambda r: r.update(), self.receivers[camera_id])
            # 释放锁
            self.receivers_lock.release()
            logger.info(f'---成功添加camera_id:{camera_id}的接收器---')
            return "success"
        except Exception as e:
            logger.error(f'---camera_id:{camera_id}的接收器启动失败---')
            logger.error(f'---{e}---')
            return "fail"

    def update_receiver(self, camera) -> str:
        '''
        更新接收器
        Args:
            camera ():

        Returns:

        '''
        camera_id = None
        try:
            logger.info(f'---开始更新camera_id:{camera_id}的接收器---')
            # 加锁
            self.receivers_lock.acquire()
            camera_id = camera['camera_id']
            # 先删后加
            self.delete_receiver(camera_id)
            self.add_receivers(camera)
            # 释放锁
            self.receivers_lock.release()
            logger.info(f'---成功更新camera_id:{camera_id}的接收器---')
            return "success"
        except Exception as e:
            logger.error(f'---camera_id:{camera_id}的接收器更新失败---')
            logger.error(f'---{e}---')
            return "fail"

    def delete_receiver(self, camera_id) -> str:
        try:
            logger.info(f'---开始删除camera_id:{camera_id}的接收器---')
            # 加锁
            self.receivers_lock.acquire()
            # 1.让receiver停止
            self.receivers[camera_id].release()
            # 2.删除receiver
            self.receivers.pop(camera_id)
            # 3.如果有则停止与删除identifiers
            if camera_id in self.identifiers.keys():
                self.identifiers[camera_id].stop()
                self.identifiers.pop(camera_id)
            # 释放锁
            self.receivers_lock.release()
            logger.info(f'---成功删除camera_id:{camera_id}的接收器---')
            return "success"
        except Exception as e:
            logger.error(f'---camera_id:{camera_id}的接收器删除失败---')
            logger.error(f'---{e}---')
            return "fail"

    def add_identifier(self, camera_id, target_rtmp) -> str:
        pass
        #TODO
    def delete_identifier(self, camera_id) -> str:
        pass
        #TODO

    def start_detect(self):
        """
        启动轮询检测器
        将轮询检查每个接收器的状态，如果有异常则启动单独的持续推理
        :return:
        """
        yoloInductor = YoloInductor(self.args,self.abnormal_items)
        # 设置处理异常策略
        # 2.1.上传异常的视频截图至服务器，
        # 2.2.单独新开辟一条推理线程，并作为一条视频数据源不断输出到SRS
        # 2.3.需要异常信息放入数据库
        handler_abnormal_context = HandlerAbnormalContext()
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyUploadScreenshot())
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyNewIdentifier(self.args,self.abnormal_items))
        handler_abnormal_context.add_strategy(HandlerAbnormalStrategyUploadInformation())
        logger.info('---成功创建YoloInductor,开始轮询检测异常---')
        while True:
            #拿出self.receivers中的K，V
            for camera_id, receiver in self.receivers.items():
                status, frame = receiver.read()
                if status:
                    logger.info(f'---camera_id:{camera_id}:的receiver收到frame--')
                    # 1.使用yolo推理
                    frame, is_abnormal = yoloInductor.process_frame(frame)
                    # 2.如果出现异常
                    if True:#TODO if is_abnormal:
                        logger.info(f'---camera_id:{camera_id}:的receiver出现异常--')
                        rtmp_url = self.cameras[camera_id]['srs_rtmp_url']
                        # 2.1.处理异常
                        handler_abnormal_context.execute(frame, source_receiver=receiver, target_rtmp=rtmp_url,
                                                         identifier_poll=self.identifier_poll, identifiers=self.identifiers)
                    # 3.如果没有异常则跳过
                    else:
                        pass
                else:
                    logger.error(f'---{camera_id}:收到frame失败--')
                    pass




if __name__ == '__main__':
    manager = YoloManager()
    manager.start_detect()

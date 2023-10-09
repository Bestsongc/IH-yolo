# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/8 15:47
# @File    : YoloManager.py
# @Software: PyCharm
import concurrent.futures

import cv2
from logger_config import logger
from RtspReceiver import RtspReceiver
from YoloInductor import YoloInductor

class YoloManager:
    def verify_args(self, args):
        '''
        验证参数
        Returns:

        '''
        if not (0 < args.CONF_THRES <= 1):
            print("--CONF_THRES 请输入0~1的数！")
            exit(0)

        if not (0 < args.IOU_THRES <= 1):
            print("--IOU_THRES 请输入0~1的数！")
            exit(0)

    def __init__(self, args, url_list):
        # self.verify_args(args)
        self.args = args
        self.url_list = url_list
        self.rtsp_list = []
        for url in url_list:
            self.rtsp_list.append(url['camema_rtsp_url'])
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
        启动检测器
        :return:
        """
        yoloInductor = YoloInductor(args)
        while True:
            for i, receiver in self.receivers:
                status, frame = receiver.read()
                logger.info(f'---{i}:收到frame--')
                if status:
                    # 1.使用yolo推理
                    frame = yoloInductor.process_frame(frame)
                    # 2.如果是异常
                    # 2.1.保存异常的视频截图，
                    # 2.2.单独新开辟一条推理线程，并作为一条视频数据源不断输出到SRS
                    # 2.3.异常放入数据库
                    # 3.如果没有异常则跳过



    def start_pushers(self, rtmp):
        """
        启动导出器
        :param rtmp: rtmp地址
        :return:
        """
        pass
        # TODO
        # exporter = VideoExporter(rtmp)

    def start(self):
        self.start_detect()

if __name__ == '__main__':
    manager = YoloManager()
    manager.start_detect()
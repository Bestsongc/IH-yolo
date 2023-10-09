# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/8 15:47
# @File    : YoloManager.py
# @Software: PyCharm
import concurrent.futures

from RtspReceiver import RtspReceiver


class YoloManager:
    def verify_args(self,args):
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
    def __init__(self,args,rtmp,rtsp_list):
        self.verify_args(args)
        self.args = args
        self.rtmp = rtmp
        self.rtsp_list = rtsp_list
        self.receivers = self.start_receivers(self.rtsp_list)

    def start_receivers(self, rtsp_list,max_workers=10):
        """
        启动接收器
        :param rtsp_list: rtsp地址列表
        :return:

        Args:
            max_workers ():
        """
        # 创建一个线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 使用线程池实例化多个 RtspReceiver 对象
            receivers = [executor.submit(RtspReceiver, url) for url in rtsp_list]
            # 等待所有线程完成
        return receivers

    def start_pushers(self,rtmp):
        """
        启动导出器
        :param rtmp: rtmp地址
        :return:
        """
        pass
        # TODO
        # exporter = VideoExporter(rtmp)



if __name__ == '__main__':
     YoloManager()
     yolo.start_recveiver
     yolo.start
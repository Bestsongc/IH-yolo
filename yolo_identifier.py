# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/11 10:35
# @File    : yolo_identifier.py
# @Software: PyCharm
import threading
import time

import cv2

import yolo_config
from logger_config import logger
from rtmp_pusher import RtmpPusher
from rtsp_receiver import RtspReceiver
from yolo_inductor import YoloInductor


class YoloIdentifier:
    def __init__(self, args, abnormal_items, source_receiver: RtspReceiver, target_rtmp):
        self.args = args
        self.source_receiver = source_receiver
        self.target_rtmp = target_rtmp
        self.abnormal_items = abnormal_items
        logger.info(f'---camera_id:{source_receiver.get_camera_id()}的YoloIdentifier初始化---')
        self.running = True

    def stop(self):
        self.running = False

    def process_stream_and_push(self):
        yolo_inductor = YoloInductor(self.args, self.abnormal_items)
        # 最大持续识别时间(单位:秒)
        identifier_max_duration = self.args['IDENTIFIER_MAX_DURATION']
        # 初始化rtmp推送器
        rtmp_pusher = RtmpPusher(self.target_rtmp, self.args['OUTPUT_FRAME_WIDTH'],
                                 self.args['OUTPUT_FRAME_HEIGHT'], self.args['VIDEO_FPS'])

        start_time = time.time()
        logger.info(f'---camera_id:{self.source_receiver.get_camera_id()}的YoloIdentifier开始识别并推流---')
        logger.info(f'---camera_id:{self.source_receiver.get_camera_id()}的推流地址rtmp:{self.target_rtmp}-')
        try:
            write_time = 0
            while self.running:
                is_abnormal = False
                # 获取画面
                status, frame = self.source_receiver.read()
                if write_time < 4: #TODO 可删
                    # 写入origin文件夹
                    cv2.imwrite(f'./origin/{time.time()}.jpg', frame)
                    write_time += 1
                # frame 正常啊
                if not status:  # 如果获取画面不成功，则退出
                    logger.error('status is false,need waiting')
                    time.sleep(1)
                    continue

                # 逐帧处理
                try:
                    frame, is_abnormal = yolo_inductor.process_frame(frame)
                    if write_time < 4: #TODO 可删
                        cv2.imwrite(f'./processed/{time.time()}.jpg', frame)
                        write_time += 1
                    # 将frame推送到rtmp
                    rtmp_pusher.push(frame)
                    # 自动退出功能
                    # 如果某个时刻没有在发现异常，且此后identifier_max_duration内没有异常，则退出这条持续监视的进程
                    if not is_abnormal:
                        if time.time() - start_time > identifier_max_duration:
                            break
                    else:
                        start_time = time.time()
                except Exception as error:
                    logger.error('process_frame报错！', error)

            # 释放资源
            rtmp_pusher.stop()
            del rtmp_pusher

        except Exception as error:
            logger.error('中途中断:%s', str(error))


if __name__ == '__main__':
    source = "rtsp://admin:admin@192.168.3.104:8554/live"
    rtmp_url = "rtmp://localhost/live/1/livestream"
    receiver = RtspReceiver(source, 1)
    threading.Thread(target=lambda: receiver.update()).start()
    yolo_identifier = YoloIdentifier(yolo_config.arguments, yolo_config.abnormal_items, receiver, rtmp_url)
    yolo_identifier.process_stream_and_push()

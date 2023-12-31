# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/21 11:18
# @File    : rtsp_receiver.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/8/23 11:38
# @File    : IH_VideoCapture.py
# @Software: PyCharm
import threading
import time
from logger_config import logger
import cv2


class RtspReceiver(object):
    '''
    额外开一个线程，用于读取rtsp视频流
    参考：https://blog.csdn.net/weixin_43747857/article/details/121672730
    https://blog.csdn.net/a545454669/article/details/129469324?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522169275993716800182132210%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=169275993716800182132210&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-9-129469324-null-null.142^v93^chatgptT3_2&utm_term=%E8%AF%BBrtsp%E8%A7%86%E9%A2%91%E6%B5%81%E5%8D%A1%E6%AD%BB&spm=1018.2226.3001.4187
    '''
    # Deleting (Calling destructor)
    def __del__(self):
        logger.info(f'---del Receiver:{self.source}---')

    def __init__(self, source,camera_id):
        # Create a VideoCapture object
        self.source = source
        self.running = True
        try:
            if source == None:
                raise Exception(f'source:{source} is None')
            self.cap = cv2.VideoCapture()
            self.cap.setExceptionMode(True)
            self.cap.open(source)
        except  Exception as e:
            logger.error(f'打开{source}出现error:{e}')
            self.cap.release()
        self.camera_id = camera_id
        self.status = False
        self.frame = None
        # Default resolutions of the frame are obtained (system dependent)
        self.frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)


        # 运行时就开守护线程(如果不用线程池的话）
        # self.thread = threading.Thread(target=self.update, args=())
        # self.thread.daemon = True
        # self.thread.start()
        # 启动时必须需要等待1s，让守护进程接收rtsp加载完成，否则主线程提前出发拿到false
        # time.sleep(1)

        logger.info(f'---成功创建Receiver:{self.source}---')

    def get_camera_id(self):
        return self.camera_id
    def get_frame_width(self):
        return self.frame_width

    def get_frame_height(self):
        return self.frame_height

    def get_fps(self):
        return self.fps

    def update(self):
        # Read the next frame from the stream in a different thread
        while self.cap.isOpened():
            self.status, self.frame = self.cap.read()

    def isOpened(self):
        return self.cap.isOpened()

    def read(self):
        if self.status:
            return self.status, self.frame
        else:
            return self.status, None

    def release(self):
        self.cap.release()

    def get_source(self):
        return self.source

if __name__ == '__main__':
    source = "rtsp://admin:admin@192.168.3.104:8554/live"
    receiver = RtspReceiver(source, 1)
    threading.Thread(target=lambda : receiver.update()).start()
    while True:
        try:
            status, frame = receiver.read()
            if status:
                print('status is true')
                # 保存frame到本地
                # cv2.imwrite(f'./{time.time()}.jpg', frame)
            else:
                print('status is false,need wating')
                time.sleep(1)
        except AttributeError:
            print('error')

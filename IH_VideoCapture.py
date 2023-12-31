# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/8/23 11:38
# @File    : IH_VideoCapture.py
# @Software: PyCharm
import threading
import time

import cv2


class MyVideoCapture(object):
    '''
    额外开一个线程，用于读取rtsp视频流
    参考：https://blog.csdn.net/weixin_43747857/article/details/121672730
    https://blog.csdn.net/a545454669/article/details/129469324?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522169275993716800182132210%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=169275993716800182132210&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-9-129469324-null-null.142^v93^chatgptT3_2&utm_term=%E8%AF%BBrtsp%E8%A7%86%E9%A2%91%E6%B5%81%E5%8D%A1%E6%AD%BB&spm=1018.2226.3001.4187
    '''

    def __init__(self, source=0):
        # Create a VideoCapture object
        self.cap = cv2.VideoCapture(source)
        self.status = False
        self.frame = None
        # Default resolutions of the frame are obtained (system dependent)
        self.frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.frame_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        # Start the thread to read frames from the video stream
        # 运行时就开守护线程
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        # 启动时必须需要等待1s，让守护进程接收rtsp加载完成，否则主线程提前出发拿到false
        time.sleep(1)

    def get_frame_width(self):
        return self.frame_width

    def get_frame_height(self):
        return self.frame_height

    def get_fps(self):
        return self.fps

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.cap.isOpened():
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


if __name__ == '__main__':
    rtsp_stream_link = 'rtsp://admin:admin@192.168.3.111:8554/live'
    video_stream_widget = MyVideoCapture(rtsp_stream_link)
    while True:
        try:
            status, frame = video_stream_widget.read()
            if status:
                cv2.imshow('frame', frame)
                cv2.waitKey(1)
            else:
                print('status is false,need wating')
                time.sleep(1)
        except AttributeError:
            print('error')

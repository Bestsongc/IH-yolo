# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/21 11:20
# @File    : StreamHandler.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/21 11:18
# @File    : RtspReceiver.py
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
import subprocess

class StreamHandler(object):
    '''
    额外开一个线程，用于读取rtsp视频流
    参考：https://blog.csdn.net/weixin_43747857/article/details/121672730
    https://blog.csdn.net/a545454669/article/details/129469324?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522169275993716800182132210%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=169275993716800182132210&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-9-129469324-null-null.142^v93^chatgptT3_2&utm_term=%E8%AF%BBrtsp%E8%A7%86%E9%A2%91%E6%B5%81%E5%8D%A1%E6%AD%BB&spm=1018.2226.3001.4187
    '''

    def __init__(self,target_rtmp, source_rtsp=0):
        # Create a VideoCapture object
        try:
            if source_rtsp == None:
                raise Exception(f'source_rtsp:{source_rtsp} is None')
            self.cap = cv2.VideoCapture(source_rtsp)
        except  Exception as e:
            logger.error(f'cv2.VideoCapture(source_rtsp) error:{e}')
            exit(0)

        self.status = False
        self.frame = None
        # Default resolutions of the frame are obtained (system dependent)
        # self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_width = 640
        self.frame_height = 480
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.target_rtmp = target_rtmp
        logger.info(f'frame_width:{self.frame_width} frame_height:{self.frame_height} fps:{self.fps}')
        self.pipe_ffmpeg = self.start_ffmpeg(self.target_rtmp,self.frame_width, self.frame_height, self.fps)
        # Start the thread to read frames from the video stream
        # 运行时就开守护线程
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        # 启动时必须需要等待1s，让守护进程接收rtsp加载完成，否则主线程提前出发拿到false
        time.sleep(1)
        logger.info(f'rtsp:{source_rtsp} rtmp:{target_rtmp} start')

    def start_ffmpeg(self, target_rtmp,frame_width, frame_height, fps):
        """
        启动ffmpeg
        :param rtmp: rtmp地址
        :return:
        """
        # ffmpeg command
        # command = ['ffmpeg',
        #            '-y',
        #            '-vcodec', 'rawvideo',
        #            '-pix_fmt', 'bgr24',
        #            '-s', "{}x{}".format(frame_width, frame_height),
        #            '-r', str(fps),
        #            '-c:v', 'libx264',
        #            '-pix_fmt', 'yuv420p',
        #            '-preset', 'ultrafast',
        #            '-f', 'flv',
        #            '-flvflags', 'no_duration_filesize',
        #           target_rtmp]
        # ffmpeg -re -i ./doc/source.flv -c copy -f flv rtmp://localhost/live/livestream
        # command = ['ffmpeg',
        #            '-s', "{}x{}".format(frame_width, frame_height),
        #            '-r', str(fps),
        #            '-preset', 'ultrafast',
        #            '-f', 'flv',
        #           target_rtmp]
        command = [
            'ffmpeg',
            '-re',  # 实时输入（用于模拟直播流）
            '-f', 'rawvideo',  # 输入格式为原始视频
            '-vcodec', 'rawvideo',  # 视频编解码器为原始视频
            '-s', '640x480',  # 视频分辨率（根据需要修改）
            '-pix_fmt', 'bgr24',  # 输入像素格式（根据需要修改）
            '-i', '-',  # 从标准输入读取视频帧
            '-vf', 'format=yuv420p',  # 强制设置像素格式
            '-c:v', 'libx264',  # 视频编码器
            '-f', 'flv',  # 输出格式为 FLV

            target_rtmp  # RTMP 目标地址
        ]
        pipe_ffmpeg = subprocess.Popen(command, stdin=subprocess.PIPE)  # stdin=sp.PIPE表示将视频流作为管道输入
        return pipe_ffmpeg

    def get_frame_width(self):
        return self.frame_width

    def get_frame_height(self):
        return self.frame_height

    def get_fps(self):
        return self.fps

    def update(self):
        # Read the next frame from the stream in a different thread And push into RTMP
        while True:
            if self.cap.isOpened():
                self.status, self.frame = self.cap.read()
                self.push(self.frame)
    def push(self,frame):
        self.pipe_ffmpeg.stdin.write(frame.tobytes())
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
    rtsp = 'rtsp://admin:admin@192.168.3.113:8554/live'
    rtmp = 'rtmp://localhost/live/livestream'
    streamhandler = StreamHandler(rtmp,rtsp)


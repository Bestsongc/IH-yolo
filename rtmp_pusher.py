# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/21 11:21
# @File    : rtmp_pusher.py
# @Software: PyCharm
import subprocess as sp
import threading


class RtmpPusher:
    def __init__(self, rtmp,frame_width, frame_height, fps):
        self.rtmp = rtmp
        self.pipe_ffmpeg = self.start_ffmpeg(rtmp,frame_width, frame_height, fps)


    def start_ffmpeg(self, rtmp,frame_width, frame_height, fps):
        """
        启动ffmpeg
        :param rtmp: rtmp地址
        :return:
        """
        # ffmpeg command
        command = ['ffmpeg',
                   '-y',
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   '-s', "{}x{}".format(frame_width, frame_height),
                   '-r', str(fps),
                   '-i', '-',
                   '-c:v', 'libx264',
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'ultrafast',
                   '-f', 'flv',
                  rtmp]

        pipe_ffmpeg = sp.Popen(command, stdin=sp.PIPE)  # stdin=sp.PIPE表示将视频流作为管道输入
        return pipe_ffmpeg

    def push(self, frame):
        """
        推送视频
        :param frame: 视频帧
        :return:
        """
        # TODO
        self.pipe_ffmpeg.stdin.write(frame.tobytes())

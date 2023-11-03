# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/11/3 9:53
# @File    : cv2_run_without_recevier.py
# @Software: PyCharm
import threading

import cv2
import numpy as np
import time

from rtsp_receiver import RtspReceiver
from ultralytics import YOLO


def run_cv2():
    cap = cv2.VideoCapture("rtsp://admin:admin@192.168.3.104:8554/live")

    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("Error: Could not open video device.")
        exit()

    # 设置摄像头的分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        # 读取一帧图像
        ret, frame = cap.read()
        time.sleep(0.5)
        # 检查图像是否读取成功
        if not ret:
            print("Error: Could not read frame.")
            break

        # 显示图像
        cv2.imshow("Frame", frame)

        # 等待键盘输入，如果是 'q'，则退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break







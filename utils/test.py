# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/4 14:19
# @File    : test.py
# @Software: PyCharm
import threading
import cv2
def write_to_flv(filename, data):
    #以cv2的摄像头作为输入的data
    cap = cv2.VideoCapture(0)
    with open(filename, 'ab') as f:
        f.write(data)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        f.write(frame)

def read_from_flv(filename):
    with open(filename, 'rb') as f:
        data = f.read()
        # Process the read data as needed

if __name__ == "__main__":
    flv_filename = "test.flv"

    write_thread = threading.Thread(target=write_to_flv, args=(flv_filename))
    read_thread = threading.Thread(target=read_from_flv, args=(flv_filename))

    write_thread.start()
    read_thread.start()

    write_thread.join()
    read_thread.join()

# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/8/23 10:12
# @File    : multiple-yolov8-tracking.py
# @Software: PyCharm
import threading

import cv2

from ultralytics import YOLO


def run_tracker_in_thread(filename, model):
    video = cv2.VideoCapture(filename)
    frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    for _ in range(frames):
        ret, frame = video.read()
        if ret:
            results = model.track(source=frame, persist=True)
            res_plotted = results[0].plot()
            cv2.imshow('p', res_plotted)
            if cv2.waitKey(1) == ord('q'):
                break


# Load the models
model1 = YOLO('../yolov8n.pt')
model2 = YOLO('../yolov8n.pt')

# Define the video files for the trackers
video_file1 = 'rtsp://admin:admin@192.168.3.111:8554/live'
video_file2 = 'rtsp://admin:admin@192.168.3.111:8554/live'

# Create the tracker threads
tracker_thread1 = threading.Thread(target=run_tracker_in_thread, args=(video_file1, model1), daemon=True)
tracker_thread2 = threading.Thread(target=run_tracker_in_thread, args=(video_file2, model2), daemon=True)

# Start the tracker threads
tracker_thread1.start()
tracker_thread2.start()

# Wait for the tracker threads to finish
tracker_thread1.join()
tracker_thread2.join()

# Clean up and close windows
cv2.destroyAllWindows()

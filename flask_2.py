# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/7 16:07
# @File    : flask_app.py
# @Software: PyCharm
import json
import threading

from flask import Flask, request
import yolo_config
from json_response import JsonResponse
from yolo_manager import YoloManager
from logger_config import logger

from flask import Flask
from multiprocessing import Process, Event
import os
import signal
from flask import Flask, request
import yolo_config
from json_response import JsonResponse
from yolo_manager import YoloManager
from logger_config import logger
app = Flask(__name__)

yolo_process = None
process_lock = Event()
yolo_manager

def start_yolo_manager():
    global yolo_manager
    yolo_manager = YoloManager()
    yolo_manager.start_detect()

@app.route('/yolo/start', methods=['POST'])
def start():
    global yolo_process
    global process_lock

    # Set the event to signal the previous process to exit
    process_lock.set()

    if yolo_process is not None and yolo_process.is_alive():
        # If the previous process is still alive, use os.kill to send a signal to terminate it
        yolo_process.terminate()

    # Start a new process
    yolo_process = Process(target=start_yolo_manager)
    yolo_process.start()
    # Reset the event for the new process
    process_lock.clear()

    return 'Started'

if __name__ == '__main__':
    app.run(debug=True)
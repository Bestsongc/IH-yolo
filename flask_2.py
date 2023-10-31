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


def start_yolo_manager():
    global yolo_manager
    yolo_manager = YoloManager()
    yolo_manager.start_detect()


@app.route('/yolo/start', methods=['POST'])
def yolo_start():
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

    return JsonResponse.success(data=None, msg="yolo_start successful")


@app.route('/yolo/setYoloArgs', methods=['POST'])
def set_yolo_args():
    '''
    设置yolo参数,修改yolo_config.py
    重启后生效
    Returns:
    '''
    logger.debug('---set_yolo_args---')
    data = request.data
    arguments = json.loads(data)
    yolo_config.arguments = arguments
    logger.debug(f'---yolo_config.arguments:{yolo_config.arguments}---')
    return JsonResponse.success(data=None, msg="set_yolo_args successful")

@app.route('/yolo/setCameras', methods=['POST'])
def set_cameras():
    '''
    设置yolo需要监控的摄像头,修改yolo_config.py
    重启后生效
    Returns:
    '''
    logger.debug('---set_cameras---')
    data = request.data
    cameras = json.loads(data)
    yolo_config.cameras = cameras
    logger.debug(f'---yolo_config.cameras:{yolo_config.cameras}---')
    return JsonResponse.success(data=None, msg="set_cameras successful")

@app.route('/yolo/setAbnormalItems', methods=['POST'])
def set_abnormal_items():
    '''
    设置yolo需要监控的异常项,修改yolo_config.py
    重启后生效
    Returns:
    '''
    logger.debug('---set_abnormal_items---')
    data = request.data
    abnormal_items = json.loads(data)
    yolo_config.abnormal_items = abnormal_items
    logger.debug(f'---yolo_config.abnormal_items:{yolo_config.abnormal_items}---')
    return JsonResponse.success(data=None, msg="set_abnormal_items successful")


if __name__ == '__main__':
    yolo_process = None
    process_lock = Event()
    yolo_manager: YoloManager
    threading.current_thread().name = 'flask_app'
    logger.info('---flask_app启动监听---')
    yolo_start()#TODO TEST
    app.run(debug=True)

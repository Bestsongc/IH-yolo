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

app = Flask(__name__)


@app.route('/yolo/start', methods=['POST'])
def start():
    logger.debug('---收到start请求---')
    data = request.data
    json_param = json.loads(data)
    # 从中获取rtsp_urls
    if json_param is None:
        return {
            "msg": "json_param is None",
            "status": 400,
        }
    try:
        # 获取POST参数
        yolo_config.arguments = json_param['yolo_arguments']
        yolo_config.cameras = json_param['cameras']
    except Exception as e:
        return {
            "msg": f"get arguments error:{e}",
            "status": 400,
        }
    # 允许启动yolo
    global is_start
    is_start = True
    return {
        "msg": "success start yolo",
        "status": 200,
    }

@app.route('/yolo/setYoloArgs', methods=['POST'])
def set_yolo_args():
    '''
    设置yolo参数,修改yolo_config.py
    Returns:
    '''
    logger.debug('---set_yolo_args---')
    data = request.data
    arguments = json.loads(data)
    yolo_config.arguments = arguments
    logger.debug(f'---yolo_config.arguments:{yolo_config.arguments}---')
    return JsonResponse.success(data=None,msg= "set_yolo_args successful")

@app.route('/yolo/updateCameras', methods=['POST'])
def update_cameras():
    #TODO 可以用dict来映射修改receiver，再根据线程名把额外识别者一起删了捏
    logger.debug('---update_cameras---')
    return {
        "msg": "error",
        "status": 400,
    }

@app.route('/yolo/cameras/add', methods=['POST'])
def add_camera():
    #TODO 拿到camera
    # camera = josn
    # yolo_manager.add_receivers(camera)
    pass

def delete_camera():
    #TODO 可以用dict来映射修改receiver，再根据线程名把额外识别者一起删了捏
    pass

def update_abnormal_item():
    pass
    #TODO

def add_identifier():
    pass
    #TODO
def delete_identifier():
    pass
    #TODO

def awaiting_start_yolo():
    global is_start
    global yolo_manager
    while not is_start:
        continue
    logger.info('---yolo_manager启动---')
    yolo_manager = YoloManager()
    detect_thread = threading.Thread(target=lambda: yolo_manager.start_detect())
    detect_thread.name = 'detect_thread'
    detect_thread.start()
    

if __name__ == '__main__':
    #修改主线程名字
    threading.current_thread().name = 'flask_app'
    is_start = False
    yolo_manager: YoloManager
    awaiting_start_yolo_thread = threading.Thread(target=lambda: awaiting_start_yolo())
    awaiting_start_yolo_thread.name = 'awaiting_start_yolo_thread'
    awaiting_start_yolo_thread.start()
    logger.info('---flask_app启动监听---')
    # 阻塞状态启动监听
    app.run()

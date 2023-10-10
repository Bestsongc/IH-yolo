# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/7 16:07
# @File    : flask_app.py
# @Software: PyCharm
import threading

from flask import Flask, request

from yolo_manager import YoloManager
from logger_config import logger

app = Flask(__name__)


@app.route('/yolo/start', methods=['POST'])
def start():
    json_param = request.json
    # 从中获取rtsp_urls
    if json_param is None:
        return {
            "msg": "error",
            "data": "no data."
        }
    try:
        global arguments
        global url_list
        # 获取POST参数
        arguments = json_param['data']['arguments']
        url_list = json_param['data']['url_list']
    except Exception as e:
        return {
            "msg": "error",
            "data": f"get arguments error:{e}"
        }
    # 允许启动yolo
    global is_start
    is_start = True
    return {
        "msg": "success",
        "data": "start yolo."
    }


# TODO
@app.route('/yolo/updateUrl', methods=['POST'])
def update_url():
    json_param = request.json
    # 从中获取rtsp_urls
    if json_param is None:
        return {
            "msg": "error",
            "data": "no data."
        }
    try:
        global arguments
        global url_list
        # 获取POST参数
        arguments = json_param['data']['arguments']
        url_list = json_param['data']['url_list']
    except Exception as e:
        return {
            "msg": "error",
            "data": f"get arguments error:{e}"
        }
    # TODO 更新输入源地址
    # global yolo_manager
    # yolo_manager.update_receivers()
    return {
        "msg": "success",
        "data": "start yolo."
    }


def start_yolo_py():
    global is_start
    global yolo_manager
    while not is_start:
        continue
    logger.info('---yolo_manager启动---')
    yolo_manager = YoloManager(arguments, url_list)
    threading.Thread(target=lambda: yolo_manager.start_detect()).start()


if __name__ == '__main__':

    is_start = False
    arguments = None
    url_list = None
    yolo_manager = None
    thread = threading.Thread(target=lambda: start_yolo_py())
    thread.start()
    # 启动监听
    app.run()

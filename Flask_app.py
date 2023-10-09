# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/7 16:07
# @File    : Flask_app.py
# @Software: PyCharm
from flask import Flask, request

from IH_Main import yolo_start

app = Flask(__name__)

@app.route('/yolo', methods=['POST'])
def start():
    json_param = request.json
    # 从中获取rtsp_urls
    if json_param is None:
        return {
            "msg": "error",
            "data": "no data."
        }
    try:
        # 获取POST参数
        arguments = json_param['data']['arguments']
        rtmp_url = json_param['data']['rtmp_url']
        rtsp_url_list = json_param['data']['rtsp_url_list']
    except Exception as e:
        return {
            "msg": "error",
            "data": f"get arguments error:{e}"
        }
    # 异步启动yolo
    yolo_start(arguments, rtmp_url, rtsp_url_list)#怎么改为异步启动
    return {
        "msg": "success",
        "data": "start yolo."
    }


app.run()

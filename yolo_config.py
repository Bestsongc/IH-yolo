# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/10 15:30
# @File    : yolo_config.py
# @Software: PyCharm
arguments={
    "ENV": "dev",
    "MODEL": "IH-821-sim.onnx",
    "CONF_THRES": 0.5,
    "IOU_THRES": 0.7,
    "ABNORMALFRAME_SAVEDIR": "abnormalFrame",
    "FLV_SAVEDIR": "FlvOut",
    "AUTO_CLOSE_TIME": "-1",
    "SHOW_CV2_WINDOW": False,
    "VIDEO_FPS": 10,
    "OUTPUT_FRAME_WIDTH": 1280,
    "OUTPUT_FRAME_HEIGHT": 1080,
    "IDENTIFIER_MAX_DURATION": 10
}
cameras=[
    {
        "camera_id": 1,
        "company": "公司1",
        "department": "部门1",
        "camera_rtsp_url": "rtsp://admin:admin@192.168.3.107:8554/live",
        "srs_rtmp_url": "rtmp://localhost/live/1/livestream",
        "srs_flv_url": "http://localhost:8080/live/1/livestream.flv",
        "isEnable": False,
        "isConnected": False
    },
    {
        "camera_id": 1,
        "company": "公司2",
        "department": "部门2",
        "camera_rtsp_url": "rtsp://admin:admin@192.168.3.107:8554/live",
        "srs_rtmp_url": "rtmp://localhost/live/2/livestream",
        "srs_flv_url": "http://localhost:8080/live/2/livestream.flv",
        "isEnable": False,
        "isConnected": False
    }
        ]
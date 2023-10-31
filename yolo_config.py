# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/10 15:30
# @File    : yolo_config.py
# @Software: PyCharm
arguments = {
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
    "IDENTIFIER_MAX_DURATION": 10,
    "MAX_IDENTIFIER_NUM": 6,
    "MAX_RECEIVER_UPDATE_NUM": 6,
}
cameras = [
    {
        "camera_id": 0,
        "camera_rtsp_url": "rtsp://admin:admin@192.168.3.116:8554/live",
        "srs_rtmp_url": "rtmp://localhost/live/1/livestream",
        "srs_flv_url": "http://localhost:8080/live/1/livestream.flv",

    },
    {
        "camera_id": 1,
        "camera_rtsp_url": "rtsp://admin:admin@192.168.3.116:8554/live",
        "srs_rtmp_url": "rtmp://localhost/live/2/livestream",
        "srs_flv_url": "http://localhost:8080/live/2/livestream.flv",
    }
]
abnormal_items = ["fire", "head", "water", "fog"]

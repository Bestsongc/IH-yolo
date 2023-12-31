# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/21 11:19
# @File    : IH_Main.py
# @Software: PyCharm
import argparse
from logger_config import logger
import threading
import time
import subprocess as sp
import cv2
import torch
import OutStrategy
import rtsp_receiver
from ultralytics import YOLO
import pymysql
import requests
import asyncio

def verify_args(args):
    '''
    验证参数
    Returns:

    '''
    if args.INPUT_SOURCE == '0':
        print("--source输入的'0'，已改为0,->摄像头")

    if not (0 < args.CONF_THRES <= 1):
        print("--CONF_THRES 请输入0~1的数！")
        exit(0)

    if not (0 < args.IOU_THRES <= 1):
        print("--IOU_THRES 请输入0~1的数！")
        exit(0)
def dict_to_args_list(args_dict):
    args_list = []
    for key, value in args_dict.items():
        args_list.append('--' + key)
        args_list.append(str(value))
    return args_list

async def yolo_start(arguments,rtmp,rtsp_list):
    # 获取POST参数


    # 使用argparse解析参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--MODEL', type=str, default='IH-821-sim.onnx',
                        help='Input your YOLOv8 model.支持ONNX，.pt,.engine')
    parser.add_argument('--CONF_THRES', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--IOU_THRES', type=float, default=0.7, help='NMS IoU threshold')
    parser.add_argument('--INPUT_SOURCE', type=str, default=0, help='输入的 source.streams path Or 0 代表摄像头')
    parser.add_argument('--ABNORMALFRAME_SAVEDIR', type=str, default="abnormalFrame", help='异常帧保存路径')
    parser.add_argument('--FLV_SAVEDIR', type=str, default="FlvOut", help='默认关闭(CLOSE), flv视频保存路径')
    parser.add_argument('--AUTO_CLOSE_TIME', type=int, default=-1, help='默认关闭（-1），超过多少秒自动关闭并保存视频')
    parser.add_argument('--SHOW_CV2_WINDOW', type=bool, default=False, help="是否在前台打开窗口展示")
    parser.add_argument('--VIDEO_FPS', type=int, default=10, help="输入输出统一的视频帧率") #TODO 未实现
    arguments = dict_to_args_list(arguments)
    args = parser.parse_args(arguments)
    # 2. 验证参数
    verify_args(args)
    # 将参数打印到日志与控制台
    logger.info(args)
    # 有 GPU 就用 GPU，没有就用 CPU
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    logger.info('device:{}'.format(device))


# if __name__ == '__main__':
#     # 1. 接收参数
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--MODEL', type=str, default='IH-821-sim.onnx',
#                         help='Input your YOLOv8 model.支持ONNX，.pt,.engine')
#     parser.add_argument('--CONF_THRES', type=float, default=0.5, help='Confidence threshold')
#     parser.add_argument('--IOU_THRES', type=float, default=0.7, help='NMS IoU threshold')
#     parser.add_argument('--INPUT_SOURCE', type=str, default=0, help='输入的 source.streams path Or 0 代表摄像头')
#     parser.add_argument('--ABNORMALFRAME_SAVEDIR', type=str, default="abnormalFrame", help='异常帧保存路径')
#     parser.add_argument('--FLV_SAVEDIR', type=str, default="FlvOut", help='默认关闭(CLOSE), flv视频保存路径')
#     parser.add_argument('--AUTO_CLOSE_TIME', type=int, default=-1, help='默认关闭（-1），超过多少秒自动关闭并保存视频')
#     parser.add_argument('--SHOW_CV2_WINDOW', type=bool, default=False, help="是否在前台打开窗口展示")
#     parser.add_argument('--VIDEO_FPS', type=int, default=10, help="输入输出统一的视频帧率") #TODO 未实现
#     args = parser.parse_args()
#     # 2. 验证参数
#     verify_args()
#     # 将参数打印到日志与控制台
#     logger.info(args)
#     # 有 GPU 就用 GPU，没有就用 CPU
#     device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
#     logger.info('device:{}'.format(device))
#     # 2.1 获取rtsp列表
#
#     # TODO 心跳模式，每60s检测之前获得的rtsp是否可用 未实现
#     # 3. 初始化
#     # 3.1 初始化接受者
#
#     # 3.2 初始化YOLO处理者
#     # 3.3 初始化输出者
#

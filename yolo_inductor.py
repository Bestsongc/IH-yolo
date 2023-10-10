# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/9 16:18
# @File    : yolo_inductor.py
# @Software: PyCharm
import argparse
from logger_config import logger
import threading
import time
import subprocess as sp
import cv2
import torch

# 框（rectangle）可视化配置
bbox_color = (150, 0, 0)  # 框的 BGR 颜色
bbox_thickness = 2  # 框的线宽

# 框类别文字
bbox_labelstr = {
    'font_size': 1,  # 字体大小
    'font_thickness': 2,  # 字体粗细
    'offset_x': 0,  # X 方向，文字偏移距离，向右为正
    'offset_y': -10,  # Y 方向，文字偏移距离，向下为正
}
old_detectCount_map = {}  # 上一帧检测到的每个对象的数量
class YoloInductor:
    def process_frame(img_bgr, model, args):
        '''
        利用YOLO处理每一帧图像，并且画出检测框，写上类别文字，返回处理后的一帧
        输入摄像头画面 bgr-array，输出图像 bgr-array
        Args:
            img_bgr ():
            model (): YOLO模型
            ABNORMALFRAME_SAVEDIR (): 异常帧保存路径

        Returns:
            处理后的一帧
        '''

        # 记录该帧开始处理的时间
        global yolo_FPS
        start_time = time.time()
        # 只要置信度大于0.5的框
        results = model.predict(source=img_bgr, task='detect', show=False, stream=True, device=None, verbose=False,
                                vid_stride=1, iou=args.IOU_THRES, conf=args.CONF_THRES)
        # source	跟之前的yolov5一致，可以输入图片路径，图片文件夹路径，视频路径
        # save	保存检测后输出的图像，默认False
        # conf	用于检测的对象置信阈值，默认0.25
        # iou	用于nms的IOU阈值，默认0.7
        # half	FP16推理，默认False
        # device	要运行的设备，即cuda设备=0/1/2/3或设备=cpu
        # show	用于推理视频过程中展示推理结果，默认False
        # save_txt	是否把识别结果保存为txt，默认False
        # save_conf	保存带有置信度分数的结果 ，默认False
        # save_crop	保存带有结果的裁剪图像，默认False
        # hide_label	保存识别的图像时候是否隐藏label ，默认False
        # hide_conf	保存识别的图像时候是否隐藏置信度，默认False
        # vid_stride	视频检测中的跳帧帧数，默认1
        # classes	展示特定类别的，根据类过滤结果，即class=0，或class=[0,2,3]
        # line_thickness	目标框中的线条粗细大小 ，默认3
        # visualize	可视化模型特征 ，默认False
        # augment	是否使用数据增强，默认False
        # agnostic_nms	是否采用class-agnostic NMS，默认False
        # retina_masks	使用高分辨率分割掩码，默认False
        # max_det	单张图最大检测目标，默认300
        # box	在分割人物中展示box信息，默认True

        # results = model(img_bgr, verbose=False)  # verbose设置为False，不单独打印每一帧预测结果

        # 开始画框
        is_abnormal = False  # 是否异常
        for result in results:

            boxes = result.boxes

            # 预测框的个数
            num_bbox = len(boxes.cls)

            # 预测框的 xyxy 坐标
            bboxes_xyxy = boxes.xyxy.cpu().numpy().astype('uint32')  # 坐标
            bboxes_cls = boxes.cls.cpu().numpy().astype('uint32')  # 类别
            # conf原本是(0,1)，转为float
            bboxes_conf = boxes.conf.cpu().numpy().astype('float32')  # confidence score, (N, 1)置信度

            # 检测到的每个对象的数量
            detectCount_map = {}
            for idx in range(num_bbox):  # 遍历每个框
                # 获取框的置信度
                bbox_conf = bboxes_conf[idx]

                # 获取该框坐标
                bbox_xyxy = bboxes_xyxy[idx]

                # 获取框的cls
                bbox_cls = bboxes_cls[idx]

                # 获取框的预测类别
                bbox_clsName = result.names[bbox_cls]

                bbox_label = f"{bbox_clsName}: {bbox_conf * 100:.2f}%"
                # 画框
                img_bgr = cv2.rectangle(img_bgr, (bbox_xyxy[0], bbox_xyxy[1]), (bbox_xyxy[2], bbox_xyxy[3]), bbox_color,
                                        bbox_thickness)

                # 写框类别文字：图片，文字字符串，文字左上角坐标，字体，字体大小，颜色，字体粗细
                img_bgr = cv2.putText(img_bgr, bbox_label,
                                      (bbox_xyxy[0] + bbox_labelstr['offset_x'],
                                       bbox_xyxy[1] + bbox_labelstr['offset_y']),
                                      cv2.FONT_HERSHEY_SIMPLEX, bbox_labelstr['font_size'], bbox_color,
                                      bbox_labelstr['font_thickness'])

                # 为当前检测到的框，将对应的数量+1
                if bbox_clsName in detectCount_map:
                    detectCount_map[bbox_clsName] += 1
                else:
                    detectCount_map[bbox_clsName] = 1

            # 记录该帧处理完毕的时间
            end_time = time.time()
            # 计算每秒处理图像帧数FPS
            yolo_FPS = 1 / (end_time - start_time)

            # 在画面上写字：图片，字符串，左上角坐标，字体，字体大小，颜色，字体粗细
            # 写FPS
            FPS_string = 'FPS  {:.2f}'.format(yolo_FPS)  # 写在画面上的字符串
            img_bgr = cv2.putText(img_bgr, FPS_string, (25, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 0, 255), 2)

            # 写检测到的每个对象的数量
            # 字要小一号，每个对象一行
            for idx, key in enumerate(detectCount_map):
                det_string = key + ' ' + str(detectCount_map[key])
                img_bgr = cv2.putText(img_bgr, det_string, (25, 100 + 15 * idx), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                      (255, 0, 255),
                                      1)
            # 输出线程号+时间戳+检测到的每个对象的数量
            logger.info("线程{}-{}-当前检测到:{},FPS:{:.2f}".format(threading.current_thread().name,
                                                                    time.strftime("%Y-%m-%d_%H-%M-%S",
                                                                                  time.localtime()),
                                                                    str(detectCount_map), yolo_FPS)
                        )


            # 对异常情况画标记
            # 异常条件：检测到的head，water，fire,fork数量中的任意一个相比于上一帧变多
            #TODO 判断异常条件有待修改
            if (detectCount_map.get('head', 0) > old_detectCount_map.get('head', 0) or
                    detectCount_map.get('water', 0) > old_detectCount_map.get('water', 0) or
                    detectCount_map.get('fire', 0) > old_detectCount_map.get('fire', 0) or
                    detectCount_map.get('fork', 0) > old_detectCount_map.get('fork', 0)):
                is_abnormal = True
                logger.critical('有异常现象')
                # 保存异常帧，加入时间戳
                cv2.imwrite(
                    args.ABNORMALFRAME_SAVEDIR + '/' + 'ABNORMAL_' + time.strftime("%Y-%m-%d_%H-%M-%S",
                                                                                   time.localtime()) + '.jpg',
                    img_bgr)
                # 写异常,color为红色
                img_bgr = cv2.putText(img_bgr, 'ABNORMAL', (25, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (1, 1, 250), 2)

            # 更新old_detectCount_map
            old_detectCount_map.clear()
            old_detectCount_map.update(detectCount_map)

        return img_bgr,is_abnormal

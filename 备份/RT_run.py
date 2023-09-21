# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/8/23 9:15
# @File    : RT_run.py
# @Software: PyCharm
from ultralytics import RTDETR

# Load a COCO-pretrained RT-DETR-l model
model = RTDETR('../rtdetr-l.pt')

# Run inference with the RT-DETR-l model on the 'bus.jpg' image
results = model.predict(source='0',show=True,stream=True)
for result in results:
    boxes = result.boxes  # Boxes object for bbox outputs
    # Detection
    # result.boxes.xyxy  # box with xyxy format, (N, 4) 左上角xy 右下角xy
    # bbox_xyxy = result.xyxy.cpu().numpy().astype(uint32) #转为整数的numpy数组

    # result.boxes.xywh  # box with xywh format, (N, 4)
    # result.boxes.xyxyn  # box with xyxy format but normalized, (N, 4)
    # result.boxes.xywhn  # box with xywh format but normalized, (N, 4)
    # result.boxes.conf  # confidence score, (N, 1)
    # result.boxes.cls  # cls, (N, 1)
    # 输出当前帧的出现的框的类别

    print(result.names)  # {0: 'fire', 1: 'fork', 2: 'head', 3: 'helmet', 4: 'water'}
    print(boxes)
    num_bbox = len(result.boxes.cls)
    print('预测出 {} 个框'.format(num_bbox))
    # 将cls转为list
    cls_list = result.boxes.cls.tolist()
    print(cls_list)
    # # 预测类别 ID
    # results[0].boxes.cls

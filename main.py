# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/8/21 11:07
# @File    : main.py
# @Software: PyCharm
import threading

from ultralytics import YOLO


# MODEL = Path(SETTINGS['weights_dir']) / 'path with spaces' / 'yolov8n.pt'  # test spaces in path
# CFG = 'yolov8n.yaml'
# SOURCE = ROOT / 'assets/bus.jpg'
# SOURCE_GREYSCALE = Path(f'{SOURCE.parent / SOURCE.stem}_greyscale.jpg')
# SOURCE_RGBA = Path(f'{SOURCE.parent / SOURCE.stem}_4ch.png')

def run(source):
    model = YOLO("IH821.engine")
    results = model.predict(task='detect',source=source, show=True,stream=True,device = None,save =True)
    # device	None or str	None	运行的设备，即 cuda device=0/1/2/3 或 device=cpu
    # classes	None or list	None	按类别过滤结果，即classes=0，或classes=[0,2,3]
    # save_crop	bool	False	save cropped images with results
    # save_conf	bool	False	save results with confidence scores
    # save bool False saveimages
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

        print(result.names)   #{0: 'fire', 1: 'fork', 2: 'head', 3: 'helmet', 4: 'water'}
        print(boxes)
        num_bbox = len(result.boxes.cls)
        print('预测出 {} 个框'.format(num_bbox))
        #将cls转为list
        cls_list = result.boxes.cls.tolist()
        print(cls_list)
        # # 预测类别 ID
        # results[0].boxes.cls


# main入口
thread1 = threading.Thread(target=run('1.jpg'))
thread1.start()

# thread2 = threading.Thread(target=run("rtsp://admin:123456@192.168.100.37:554/h264/ch1/stream"))
# thread2.start()
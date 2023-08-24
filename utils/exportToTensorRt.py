# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/8/24 11:17
# @File    : exportToTensorRt.py
# @Software: PyCharm
from ultralytics import YOLO

# Load a model
model = YOLO('../IH821.pt')  # load an official model

# Export the model
model.export(format='engine')

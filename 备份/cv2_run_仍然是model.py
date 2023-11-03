# 调用摄像头逐帧实时处理模板
# 不需修改任何代码，只需修改process_frame函数即可
# 同济子豪兄 2021-7-8
import logging
import threading
import time

import cv2
import torch
from tqdm import tqdm

from ultralytics import YOLO

# 导入opencv-python

# 配置日志
logging.basicConfig(filename='../IH-detect.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 获取日志器
logger = logging.getLogger()

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


def process_frame(img_bgr):
    '''
    处理每一帧图像
    输入摄像头画面 bgr-array，输出图像 bgr-array
    Args:
        img_bgr ():
        model (): YOLO模型
        ABNORMAL_FRAME_SAVE_DIR (): 异常帧保存路径

    Returns:
        处理后的一帧
    '''

    # 记录该帧开始处理的时间
    start_time = time.time()
    # 只要置信度大于0.5的框
    # results = model.predict(source=img_bgr,task='detect',show=False,stream=True,device = None,verbose=False)
    results = model(img_bgr, verbose=False)  # verbose设置为False，不单独打印每一帧预测结果

    # 如果是model给的单source，则results[0]就是结果result
    boxes = results[0].boxes
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

        # 只处理置信度大于0.5的框
        if bbox_conf < 0.5:
            continue

        # 获取该框坐标
        bbox_xyxy = bboxes_xyxy[idx]

        # 获取框的cls
        bbox_cls = bboxes_cls[idx]

        # 获取框的预测类别
        bbox_clsName = results[0].names[bbox_cls]

        bbox_label = f"{bbox_clsName}: {bbox_conf * 100:.2f}%"
        # 画框
        img_bgr = cv2.rectangle(img_bgr, (bbox_xyxy[0], bbox_xyxy[1]), (bbox_xyxy[2], bbox_xyxy[3]), bbox_color,
                                bbox_thickness)

        # 写框类别文字：图片，文字字符串，文字左上角坐标，字体，字体大小，颜色，字体粗细
        img_bgr = cv2.putText(img_bgr, bbox_label,
                              (bbox_xyxy[0] + bbox_labelstr['offset_x'], bbox_xyxy[1] + bbox_labelstr['offset_y']),
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
    FPS = 1 / (end_time - start_time)

    # 在画面上写字：图片，字符串，左上角坐标，字体，字体大小，颜色，字体粗细
    # 写FPS
    FPS_string = 'FPS  {:.2f}'.format(FPS)  # 写在画面上的字符串
    img_bgr = cv2.putText(img_bgr, FPS_string, (25, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (255, 0, 255), 2)

    # 写检测到的每个对象的数量
    # 字要小一号，每个对象一行
    for idx, key in enumerate(detectCount_map):
        det_string = key + ' ' + str(detectCount_map[key])
        img_bgr = cv2.putText(img_bgr, det_string, (25, 100 + 15 * idx), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255),
                              1)
    # 输出线程号+时间戳+检测到的每个对象的数量
    logger.info("线程{}-{}-当前检测到:{}".format(threading.current_thread().name,
                                                 time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()),
                                                 str(detectCount_map))
                )
    print("线程{}-{}-当前检测到:{}".format(threading.current_thread().name,
                                           time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()), str(detectCount_map))
          )

    # 检测是否异常
    # 异常条件：检测到的head，water，fire,fork数量中的任意一个相比于上一帧变多
    if (detectCount_map.get('head', 0) > old_detectCount_map.get('head', 0) or
            detectCount_map.get('water', 0) > old_detectCount_map.get('water', 0) or
            detectCount_map.get('fire', 0) > old_detectCount_map.get('fire', 0) or
            detectCount_map.get('fork', 0) > old_detectCount_map.get('fork', 0)):
        # 如果有异常-> 1.画面写异常 2.保存当前帧
        logger.critical('有异常现象')
        print('----!!!!!有异常现象---------')
        # 保存异常帧，加入时间戳
        cv2.imwrite(
            ABNORMAL_FRAME_SAVE_DIR + '/' + 'ABNORMAL_' + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) + '.jpg',
            img_bgr)
        # 写异常,color为红色
        img_bgr = cv2.putText(img_bgr, 'ABNORMAL', (25, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (1, 1, 250), 2)

    # 更新old_detectCount_map
    old_detectCount_map.clear()
    old_detectCount_map.update(detectCount_map)

    return img_bgr


def run_detect(source=0):
    '''
    运行检测
    Returns:
    '''
    # 获取摄像头，传入0表示获取系统默认摄像头
    cap = cv2.VideoCapture(source)

    # 日志显示第几号线程的摄像头是否打开成功
    if cap.isOpened():
        logger.info('线程{}的摄像头打开成功,source={}'.format(threading.current_thread().name, source))
        print('线程{}的摄像头打开成功,source={}'.format(threading.current_thread().name, source))

    # 无限循环，直到break被触发
    while cap.isOpened():

        # 获取画面
        success, frame = cap.read()

        if not success:  # 如果获取画面不成功，则退出
            logger.error('获取画面不成功，退出')
            print('获取画面不成功，退出')
            break

        ## 逐帧处理
        frame = process_frame(frame)

        # 展示处理后的三通道图像
        cv2.imshow('window_' + str(threading.current_thread().name), frame)

        key_pressed = cv2.waitKey(60)  # 每隔多少毫秒毫秒，获取键盘哪个键被按下
        # print('键盘上被按下的键：', key_pressed)

        if key_pressed in [ord('q'), 27]:  # 按键盘上的q或esc退出（在英文输入法下）
            break

    # 关闭摄像头
    cap.release()

    # 关闭图像窗口
    cv2.destroyAllWindows()

# 入口函数
if __name__ == '__main__':
    # 初始化
    # 有 GPU 就用 GPU，没有就用 CPU
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    logger.info('device:{}'.format(device))
    print('device:{}'.format(device))
    model = YOLO("../IH-821-sim.onnx", task='detect')
    ABNORMAL_FRAME_SAVE_DIR = "../abnormalFrame"

    run_detect(0)
    # # 运行两个线程
    # for i in range(1):
    #     t = threading.Thread(target=run_detect, args=('source.streams',))
    #     t.start()


# 视频逐帧处理代码模板
# 不需修改任何代码，只需定义process_frame函数即可
# 同济子豪兄 2021-7-10
def generate_video(input_path='videos/robot.mp4'):
    filehead = input_path.split('/')[-1]
    output_path = "out-" + filehead

    print('视频开始处理', input_path)

    # 获取视频总帧数
    cap = cv2.VideoCapture(input_path)
    frame_count = 0
    while (cap.isOpened()):
        success, frame = cap.read()
        frame_count += 1
        if not success:
            break
    cap.release()
    print('视频总帧数为', frame_count)

    # cv2.namedWindow('Crack Detection and Measurement Video Processing')
    cap = cv2.VideoCapture(input_path)
    frame_size = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(output_path, fourcc, fps, (int(frame_size[0]), int(frame_size[1])))

    # 进度条绑定视频总帧数
    with tqdm(total=frame_count - 1) as pbar:
        try:
            while (cap.isOpened()):
                success, frame = cap.read()
                if not success:
                    break

                # 处理帧
                # frame_path = './temp_frame.png'
                # cv2.imwrite(frame_path, frame)
                try:
                    frame = process_frame(frame)
                except Exception as error:
                    print('报错！', error)
                    pass

                if success == True:
                    # cv2.imshow('Video Processing', frame)
                    out.write(frame)

                    # 进度条更新一帧
                    pbar.update(1)

                # if cv2.waitKey(1) & 0xFF == ord('q'):
                # break
        except:
            print('中途中断')
            pass

    cv2.destroyAllWindows()
    out.release()
    cap.release()
    print('视频已保存', output_path)


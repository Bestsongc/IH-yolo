# 调用摄像头逐帧实时处理模板
import argparse
import logging
import threading
import time
import subprocess as sp
import cv2
import torch

import OutStrategy
from ultralytics import YOLO

# 导入opencv-python

# 配置日志
logging.basicConfig(filename='IH-detect.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
import IH_VideoCapture

yolo_FPS = 10  # 默认为15


def verify_args():
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

    # 检测rtmp地址是否正确
    if args.RTMP_URL[0:4] != 'rtmp':
        print('rtmp地址不正确！')
        exit(0)

def process_frame(img_bgr, model):
    '''
    处理每一帧图像
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
                                                                time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()),
                                                                str(detectCount_map), yolo_FPS)
                    )
        print("线程{}-{}-当前检测到:{},FPS:{:.2f}".format(threading.current_thread().name,
                                                          time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()),
                                                          str(detectCount_map), yolo_FPS)
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
                args.ABNORMALFRAME_SAVEDIR + '/' + 'ABNORMAL_' + time.strftime("%Y-%m-%d_%H-%M-%S",
                                                                               time.localtime()) + '.jpg',
                img_bgr)
            # 写异常,color为红色
            img_bgr = cv2.putText(img_bgr, 'ABNORMAL', (25, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.25, (1, 1, 250), 2)

        # 更新old_detectCount_map
        old_detectCount_map.clear()
        old_detectCount_map.update(detectCount_map)

    return img_bgr


def run_detect(source):
    '''
    运行检测
    Returns:
    '''
    # 获取摄像头，传入0表示获取系统默认摄像头
    # cap = cv2.VideoCapture(source)

    my_cap = IH_VideoCapture.MyVideoCapture(source)

    # 初始化flv视频写入器
    frame_width = int(my_cap.get_frame_width())
    frame_height = int(my_cap.get_frame_height())
    fourcc = cv2.VideoWriter_fourcc('F', 'L', 'V', '1')  # 该参数是Flash视频，文件名后缀为.flv
    global yolo_FPS
    fps = yolo_FPS
    print('fps:' + str(fps))
    print('frame_width:' + str(frame_width))
    print('frame_height:' + str(frame_height))
    # flv保存路径要再加上当前线程的名字(需要去掉空格及特殊符号，来满足文件夹名字要求）与线程开始时间
    flv_savePath = args.FLV_SAVEDIR + '/' + threading.current_thread().name.replace(' ', '').replace(':',
                                                                                                     '-') + '-' + time.strftime(
        "%Y-%m-%d_%H-%M-%S", time.localtime()) + '.flv'
    print('flv_savePath:', flv_savePath)
    # path示例 'flvOut/out.flv'

    out = cv2.VideoWriter(flv_savePath, fourcc, fps, (frame_width, frame_height))

    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    # ffmpeg command
    command = ['ffmpeg',
               '-y',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-pix_fmt', 'bgr24',
               '-s', "{}x{}".format(frame_width, frame_height),
               '-r', str(fps),
               '-i', '-',
               '-c:v', 'libx264',
               '-pix_fmt', 'yuv420p',
               '-preset', 'ultrafast',
               '-f', 'flv',
               args.RTMP_URL]
    print("frame_width"+str(frame_width))
    print("frame_height"+str(frame_height))
    pipe_ffmpeg = sp.Popen(command, stdin=sp.PIPE)  # stdin=sp.PIPE表示将视频流作为管道输入

    model = YOLO(model=args.MODEL, task='detect')  # 加载模型
    # 参数文档 https://docs.ultralytics.com/usage/cfg/

    # 日志显示第几号线程的摄像头是否打开成功
    if my_cap.isOpened():
        logger.info('线程{}的摄像头打开成功,source={}'.format(threading.current_thread().name, source))
        print('线程{}的摄像头打开成功,source={}'.format(threading.current_thread().name, source))

    start_time = time.time()
    # 创建上下文类
    video_out_context = OutStrategy.VideoOutContext()
    if args.FLV_SAVEDIR != 'CLOSE':
        video_out_context.add_strategy(OutStrategy.VideoOutStrategy_write_local_flv(out))
    if args.SHOW_CV2_WINDOW:
        video_out_context.add_strategy(OutStrategy.VideoOutStrategy_showCV2())
    if args.RTMP_URL != 'CLOSE':
        video_out_context.add_strategy(OutStrategy.VideoOutStrategy_push_rtmp(pipe_ffmpeg))
    if args.AUTO_CLOSE_TIME != -1:
        video_out_context.add_strategy(OutStrategy.AutoCloseStrategy(start_time, args.AUTO_CLOSE_TIME))

    # 无限循环，直到break被触发
    try:
        while my_cap.isOpened():
            # 获取画面
            status, frame = my_cap.read()

            if not status:  # 如果获取画面不成功，则退出
                logger.error('status is false,need waiting')
                print('status is false,need waiting')
                time.sleep(1)
                continue

            # 逐帧处理
            try:
                frame = process_frame(frame, model)
            except Exception as error:
                logger.error('process_frame报错！', error)
                print('process_frame报错！', error)

            # 逐帧输出
            try:
                video_out_context.handle_frame(frame)
            except  Exception as error:
                logger.error('video_out_context.handle_frame(frame)报错！', error)
                print('video_out_context.handle_frame(frame)报错！', error)

            # 使用opencv读取rtsp视频流预览的时候，发现运行越久越卡的情况。分析是内存没有释放的缘故，在循环里每帧结束后把该帧用del()删除即可
            del status
            del frame



    except Exception as error:
        print('中途中断 %s', str(error))
        logger.error('中途中断:%s', str(error))

    # 关闭flv视频写入器
    out.release()
    # 关闭摄像头
    my_cap.release()
    # 关闭图像窗口
    cv2.destroyAllWindows()
    # 关闭ffmpeg
    pipe_ffmpeg.terminate()


def run_program():
    # 读取source.streams中的每一行作为一个线程的source作为参数，启动一个线程
    if args.INPUT_SOURCE == 0:
        # 摄像头
        run_detect(0)
        return

    # 否则是文件中的rtsp地址作为流
    with open(args.INPUT_SOURCE, 'r') as f:
        sources = f.readlines()
    # 去掉每行末尾的换行符
    sources = [x.strip() for x in sources]
    # 去掉空行
    sources = [x for x in sources if x != '']
    # 去掉注释行
    sources = [x for x in sources if x[0] != '#']
    # 启动线程
    for source in sources:
        # 创建线程
        thread = threading.Thread(target=run_detect, args=(source,))
        # 启动线程
        thread.start()


# 入口函数
if __name__ == '__main__':
    # 初始化
    parser = argparse.ArgumentParser()
    parser.add_argument('--MODEL', type=str, default='IH-821-sim.onnx',
                        help='Input your YOLOv8 model.支持ONNX，.pt,.engine')
    parser.add_argument('--CONF_THRES', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--IOU_THRES', type=float, default=0.7, help='NMS IoU threshold')
    parser.add_argument('--INPUT_SOURCE', type=str, default=0, help='输入的 source.streams path Or 0 代表摄像头')
    parser.add_argument('--ABNORMALFRAME_SAVEDIR', type=str, default="abnormalFrame", help='异常帧保存路径')
    parser.add_argument('--FLV_SAVEDIR', type=str, default="FlvOut", help='默认关闭(CLOSE), flv视频保存路径')
    parser.add_argument('--AUTO_CLOSE_TIME', type=int, default=-1, help='默认关闭（-1），超过多少秒自动关闭并保存视频')
    parser.add_argument('--RTMP_URL', type=str, default="rtmp://localhost/live/1/livestream",
                        help='推流的流媒体服务器的地址,"CLOSE"代表关闭')
    parser.add_argument('--SHOW_CV2_WINDOW', type=bool, default=False, help="是否在前台打开窗口展示")
    parser.add_argument('--VIDEO_FPS', type=int, default=10, help="输入输出统一的视频帧率") #TODO 未实现
    args = parser.parse_args()
    verify_args()
    # 将参数打印到日志与控制台
    print(args)
    logger.info(args)

    # 有 GPU 就用 GPU，没有就用 CPU
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    logger.info('device:{}'.format(device))
    print('device:{}'.format(device))

    run_program()

import cv2
import time
def main():
    # 打开摄像头
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("无法打开摄像头")
        return

    # 设置保存视频的参数
    fourcc = cv2.VideoWriter_fourcc('F', 'L', 'V', '1')   # 使用FLV编码器
    fps = 1
    out = cv2.VideoWriter('output.flv', fourcc, fps, (640, 480))  # 输出文件名、编码器、帧率、分辨率

    # 每隔1秒增加1帧
    start_time = time.time()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("无法获取视频帧")
            break

        # 写入视频帧
        out.write(frame)
        print("FPS:" + str(fps))
        cv2.imshow("摄像头画面", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time >= 5.0:
            fps  = 30
            out.set(cv2.CAP_PROP_FPS, fps)
            start_time = current_time

    # 释放摄像头和视频写入器
    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

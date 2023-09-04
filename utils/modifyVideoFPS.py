import queue
import threading

import cv2


def write_frames(q, out):
    while True:
        frame = q.get()
        if frame is None:
            break
        out.write(frame)
        q.task_done()

input_path = 'input.flv'
output_path = 'output.flv'
new_fps = 30

cap = cv2.VideoCapture(input_path)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'FLV1')

out = cv2.VideoWriter(output_path, fourcc, new_fps, (width, height))

frame_queue = queue.Queue()
writer_thread = threading.Thread(target=write_frames, args=(frame_queue, out))
writer_thread.start()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame_queue.put(frame)

frame_queue.put(None) # 发送一个信号，通知写入线程结束
writer_thread.join()

cap.release()
out.release()

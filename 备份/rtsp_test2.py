from threading import Thread

import cv2


class VideoScreenshot(object):
    def __init__(self, src=0):
        # Create a VideoCapture object
        self.capture = cv2.VideoCapture(src)

        # Take screenshot every x seconds
        self.screenshot_interval = 0.5

        # Default resolutions of the frame are obtained (system dependent)
        self.frame_width = int(self.capture.get(3))
        self.frame_height = int(self.capture.get(4))

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()

    def show_frame(self):
        # Display frames in main program
        if self.status:
            ## 这一块儿是目标跟踪和显示的代码
            cv2.imshow('frame', self.frame)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)


if __name__ == '__main__':
    rtsp_stream_link = 'rtsp://admin:admin@192.168.3.111:8554/live'
    video_stream_widget = VideoScreenshot(rtsp_stream_link)

    ## 这一块是目标跟踪的代码
    # model = YOLO(model='IH-821-sim.onnx', task='detect')  # 加载模型

    while True:
        try:
            video_stream_widget.show_frame()
        except AttributeError:
            pass
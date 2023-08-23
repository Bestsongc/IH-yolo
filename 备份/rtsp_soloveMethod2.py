from threading import Thread
import cv2
import time
from mmtrack.apis import inference_mot, init_model  # 导入mmtrack进行目标跟踪
from torchvision import transforms


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
            result = inference_mot(model, self.frame, frame_id=self.frame_count)
            new_img = model.show_result(
                self.frame,
                result,
                score_thr=score_thr,
                show=show,
                wait_time=0,
                out_file=None,
                backend=backend)
            cv2.imshow('frame', self.frame)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)

    def save_frame(self):
        # Save obtained frame periodically
        self.frame_count = 0

        def save_frame_thread():
            while True:
                try:
                    cv2.imwrite('pools/frame_{}.png'.format(self.frame_count), self.frame)
                    self.frame_count += 1
                    time.sleep(self.screenshot_interval)
                except AttributeError:
                    pass

        Thread(target=save_frame_thread, args=()).start()


if __name__ == '__main__':
    rtsp_stream_link = 'RTSP链接'
    video_stream_widget = VideoScreenshot(rtsp_stream_link)
    video_stream_widget.save_frame()

    ## 这一块是目标跟踪的代码
    checkpoint = 'work_dirs/epoch_28.pth'
    config = 'work_dirs/train_cfg.py'
    score_thr = 0.0
    show = False
    device = 'cuda:0'
    backend = 'cv2'
    model = init_model(config, checkpoint, device=device)

    while True:
        try:
            video_stream_widget.show_frame()
        except AttributeError:
            pass
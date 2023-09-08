# Ultralytics YOLO 🚀, AGPL-3.0 license
# Builds ultralytics/ultralytics:latest image on DockerHub https://hub.docker.com/r/ultralytics/ultralytics
# Image is CUDA-optimized for YOLOv8 single/multi-GPU training and inference

# Start FROM PyTorch image https://hub.docker.com/r/pytorch/pytorch or nvcr.io/nvidia/pytorch:23.03-py3


# 基础镜像

FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Create working directory
WORKDIR /usr/src/ultralytics

# Copy contents
# COPY . /usr/src/app  (issues as not a .git directory)
# 把本地的文件夹加入到当前容器的 /usr/src/ultralytics
ADD .  /usr/src/ultralytics

# 打印当前目录
RUN pwd
RUN ls -a
# 换源先
#RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list

# pip换源
RUN pip install -U pip
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
RUN pip config set install.trusted-host mirrors.aliyun.com

# docker换源
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN sed -i s@/security.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt-get clean
RUN apt-get update
# 展示当前源
RUN cat /etc/apt/sources.list

RUN pip install  nvidia-tensorrt

# Downloads to user config dir
ADD https://ultralytics.com/assets/Arial.ttf https://ultralytics.com/assets/Arial.Unicode.ttf /root/.config/Ultralytics/

# Install linux packages
# g++ required to build 'tflite_support' and 'lap' packages, libusb-1.0-0 required for 'tflite_support' package
RUN apt update \
    && apt install --no-install-recommends -y gcc git zip curl htop libgl1-mesa-glx libglib2.0-0 libpython3-dev gnupg g++ libusb-1.0-0
# RUN alias python=python3

# Security updates
# https://security.snyk.io/vuln/SNYK-UBUNTU1804-OPENSSL-3314796
RUN apt upgrade --no-install-recommends -y openssl tar







# Install pip packages
RUN python3 -m pip install --upgrade pip wheel
# 它们是各种库或工具，用于不同的任务，例如图像增强、性能测量等
RUN pip install  -e ".[export]" thop albumentations comet pycocotools


# Requires <= Python 3.10, bug with paddlepaddle==2.5.0
RUN pip install  paddlepaddle==2.4.2 x2paddle
# Fix error: `np.bool` was a deprecated alias for the builtin `bool`
RUN pip install  numpy==1.23.5
# Remove exported models
RUN rm -rf tmp

#CD 到对应目录
# pip requirements
#TODO 或许setup.py就可以了
RUN pip install --no-cache -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# Set environment variables
ENV OMP_NUM_THREADS=1
# Avoid DDP error "MKL_THREADING_LAYER=INTEL is incompatible with libgomp.so.1 library" https://github.com/pytorch/pytorch/issues/37377
ENV MKL_THREADING_LAYER=GNU

#ENV中加入main.py的参数
#模型名称
ENV MODEL = "IH-821-sim.onnx"
# 置信度
ENV CONF_THRES = 0.5
# nms阈值
ENV IOU_THRES = 0.7
# 输入源
ENV INPUT_SOURCE = 0
# 保存异常帧的路径
ENV ABNORMALFRAME_SAVEDIR = "abnormalFrame"
# 保存flv的路径
ENV FLV_SAVEDIR = "FlvOut"
# 自动关闭时间
ENV AUTO_CLOSE_TIME = -1
ENV RTMP_URL = "rtmp://localhost/live/livestream"



# Usage Examples -------------------------------------------------------------------------------------------------------

# final configuration


# Build and Push
# t=ultralytics/ultralytics:latest && sudo docker build -f docker/Dockerfile -t $t . && sudo docker push $t
ENTRYPOINT ["python main.py"]
# CMD 会在docker run之后默认执行
# main.py之后接入ENV参数
CMD ["--MODEL", "$MODEL","--CONF_THRES", "$CONF_THRES","--IOU_THRES", "$IOU_THRES","--INPUT_SOURCE", "$INPUT_SOURCE","--ABNORMALFRAME_SAVEDIR", "$ABNORMALFRAME_SAVEDIR","--FLV_SAVEDIR", "$FLV_SAVEDIR","--AUTO_CLOSE_TIME","$AUTO_CLOSE_TIME","--RTMP_URL", "$RTMP_URL"]

# Pull and Run
# t=ultralytics/ultralytics:latest && sudo docker pull $t && sudo docker run -it --ipc=host --gpus all $t   MY-IH-APP python main.py --source 'rtsp://admin:admin@192.168.3.111:8554/live'

# Pull and Run with local directory access
# t=ultralytics/ultralytics:latest && sudo docker pull $t && sudo docker run -it --ipc=host --gpus all -v "$(pwd)"/datasets:/usr/src/datasets $t

# Kill all
# sudo docker kill $(sudo docker ps -q)

# Kill all image-based
# sudo docker kill $(sudo docker ps -qa --filter ancestor=ultralytics/ultralytics:latest)

# DockerHub tag update
# t=ultralytics/ultralytics:latest tnew=ultralytics/ultralytics:v6.2 && sudo docker pull $t && sudo docker tag $t $tnew && sudo docker push $tnew

# Clean up
# sudo docker system prune -a --volumes

# Update Ubuntu drivers
# https://www.maketecheasier.com/install-nvidia-drivers-ubuntu/

# DDP test
# python -m torch.distributed.run --nproc_per_node 2 --master_port 1 train.py --epochs 3

# GCP VM from Image
# docker.io/ultralytics/ultralytics:latest

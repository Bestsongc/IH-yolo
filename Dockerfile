# Ultralytics YOLO 🚀, AGPL-3.0 license
# Builds ultralytics/ultralytics:latest image on DockerHub https://hub.docker.com/r/ultralytics/ultralytics
# Image is CUDA-optimized for YOLOv8 single/multi-GPU training and inference

# Start FROM PyTorch image https://hub.docker.com/r/pytorch/pytorch or nvcr.io/nvidia/pytorch:23.03-py3


# 基础镜像
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime


RUN pip install --no-cache nvidia-tensorrt --index-url https://pypi.ngc.nvidia.com

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

# Create working directory
WORKDIR /usr/src/ultralytics



# Copy contents
# COPY . /usr/src/app  (issues as not a .git directory)
# 把本地的文件夹加入到当前容器的 /usr/src/ultralytics
ADD  ultralytics /usr/src/ultralytics

# Install pip packages
RUN python3 -m pip install --upgrade pip wheel
RUN pip install --no-cache -e ".[export]" thop albumentations comet pycocotools


# Requires <= Python 3.10, bug with paddlepaddle==2.5.0
RUN pip install --no-cache paddlepaddle==2.4.2 x2paddle
# Fix error: `np.bool` was a deprecated alias for the builtin `bool`
RUN pip install --no-cache numpy==1.23.5
# Remove exported models
RUN rm -rf tmp



# Set environment variables
ENV OMP_NUM_THREADS=1
# Avoid DDP error "MKL_THREADING_LAYER=INTEL is incompatible with libgomp.so.1 library" https://github.com/pytorch/pytorch/issues/37377
ENV MKL_THREADING_LAYER=GNU



# Usage Examples -------------------------------------------------------------------------------------------------------

# final configuration


# Build and Push
# t=ultralytics/ultralytics:latest && sudo docker build -f docker/Dockerfile -t $t . && sudo docker push $t
# run
#    ENV FLASK_APP=hello
#    EXPOSE 8000
#    CMD flask run --host 0.0.0.0 --port 8000

# CMD默认执行
 CMD ["python", "main.py"]

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

import multiprocessing
import time

from logger_config import logger
def worker(x):
    while True:
        time.sleep(1)
        logger.info(f'子进程: {x}')

def main():
    pool = multiprocessing.Pool(processes=4)  # 创建包含4个进程的进程池
    pool.apply_async(func=worker, args=(1,))  # 添加任务到进程池
    pool.apply_async(func=worker, args=(2,))  # 添加任务到进程池
    while True:
        time.sleep(1)
        logger.info('主进程1')

if __name__ == '__main__':
    main()

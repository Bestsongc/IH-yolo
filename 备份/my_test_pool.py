# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/12 10:49
# @File    : my_test_pool.py
# @Software: PyCharm
from time import sleep


class receivers_2:
    def __init__(self):
        self.frame = 0
        self.running = True
    def update(self):
        while self.running:
            self.frame+=1

    def stop_update(self):
        self.running = False
    def get_frame(self):
        return self.frame
def for_process_poll():
    from multiprocessing import Pool
    pool = Pool(processes=15)
    # 初始化10个receivers,以dict形式存储
    receivers = {}
    for i in range(10):
        receivers[i] = receivers_2()
        print(f'receiver[{i}]:init')

    # 使用进程池对所有receivers进行update
    for i in range(10):
        pool.apply_async(receivers[i].update)
        print(f'receiver[{i}]:update')

    # 过了一会我就想指定i=1的receiver停止update
    # 等待一段时间后
    import time
    time.sleep(2)  # 例如，等待2秒

    #展示当前进程数
    print(f'当前进程数：{len(pool._cache)}')

    # 停止receiver
    for i in range(10):
        receivers[i].stop_update()
        print(f'receiver[{i}]:stopped')


    #展示当前进程数
    print(f'当前进程数：{len(pool._cache)}')

    # 使用进程池pool.starmap来使用get_frame读取
    while True:
        results = pool.starmap(lambda r: r.get_frame(), [(r,) for r in receivers.values()])
        print(results)

    #     print(f'receiver[{i%10}]:',(pool.apply_async(receivers[i%10].get_frame).get()))

def for_threadpool():
    import concurrent.futures
    receivers = {}
    for i in range(10):
        receivers[i] = receivers_2()
        print(f'receiver[{i}]:init')

    poll = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    while True:
        for i in range(10):
            poll.submit(lambda r : r.update(), receivers[i])
            print(f'receiver[{i}]:update')

    for i in range(10):
        poll.submit(lambda r : r.update(), receivers[i])
        print(f'receiver[{i}]:update')

    # # 创建一个包含20个线程的线程池
    # with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    #     # 提交100个任务给线程池
    #     for i in range(10):
    #         executor.submit(lambda r : r.update, receivers[i])
    #         print(f'receiver[{i%10}]:update')

    sleep(1)
    for i in range(10):
        receivers[i].stop_update()

    # while True:
    #     for i in range(10):
    #         print(f'receiver[{i}]:',receivers[i].get_frame())

    # 要改用使用线程池来不断完成读取任务
    # read_poll = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    # while True:
    #     read_poll.submit(lambda r : r.get_frame(), receivers[0])
    #     TODO

def for_multiprocessingpoll():
    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes=15)
    # 初始化10个receivers,以dict形式存储
    receivers = {}
    for i in range(10):
        receivers[i] = receivers_2()
        print(f'receiver[{i}]:init')

    # 使用线程池对所有receivers进行update
    for i in range(10):
        pool.apply_async(receivers[i].update)
        print(f'receiver[{i}]:update')

    # 过了一会我就想指定i=1的receiver停止update
    # 等待一段时间后
    import time
    time.sleep(2)  # 例如，等待2秒

    # 停止指定的receiver，这里是i=1的receiver
    receivers[1].stop_update()
    print("receiver[1]:stopped")

    # while True:
    #     for i in range(10):
    #         print(f'receiver[{i}]:',receivers[i].get_frame())

    # 使用线程池pool.starmap来使用get_frame读取
    while True:
        results = pool.starmap(lambda r: r.get_frame(), [(r,) for r in receivers.values()])
        print(results)

    # 调用线程池使用update
    # for i in range(100):
    #     pool.apply_async(receivers[i%10].update)
    #     print(f'receiver[{i%10}]:update')
    #     # 从pool.apply_async(receivers[i%10].get_frame) 获取返回值
    #     print(f'receiver[{i%10}]:',(pool.apply_async(receivers[i%10].get_frame).get()))
if __name__ == '__main__':
    # for_threadpool()
    for_process_poll()
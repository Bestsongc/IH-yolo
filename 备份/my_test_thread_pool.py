# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/12 10:49
# @File    : my_test_thread_pool.py
# @Software: PyCharm
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

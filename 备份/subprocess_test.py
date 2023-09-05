# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/9/5 11:02
# @File    : subprocess_test.py
# @Software: PyCharm
import subprocess
p = subprocess.Popen('ls -a', stdout=subprocess.PIPE, shell=True)
print(p.stdout.read())
# -*- coding: utf-8 -*-
# @Author  : Zhuofan Shi
# @Time    : 2023/10/7 15:41
# @File    : nacos_mytest.py
# @Software: PyCharm
import nacos
# 连接地址
SERVER_ADDRESSES = "8.130.137.203"
SERVER_PORT = '8848'

# 命名空间
NAMESPACE = "public"

# 账号信息
USERNAME = 'nacos'
PASSWORD = 'nacos'

# 创建一个连接对象
client = nacos.NacosClient(f'{SERVER_ADDRESSES}:{SERVER_PORT}', namespace=NAMESPACE, username=USERNAME,
                           password=PASSWORD)
# get config
data_id = "config.nacos"
group = "group"
print(client.get_config(data_id, group))
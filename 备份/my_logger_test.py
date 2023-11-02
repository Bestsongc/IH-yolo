import logging

# 创建一个Logger实例
logger = logging.getLogger(__name__)

# 设置日志级别
logger.setLevel(logging.DEBUG)

# 创建一个输出到文件的Handler
file_handler = logging.FileHandler('my_log.log')

# 创建一个自定义的日志格式，包括进程号
log_format = '[%(asctime)s] [%(process)d] [%(levelname)s] - %(message)s'
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# 添加Handler到Logger
logger.addHandler(file_handler)

# 记录日志
logger.debug('This is a debug message.')
logger.info('This is an info message.')
logger.warning('This is a warning message.')
logger.error('This is an error message.')
logger.critical('This is a critical message.')

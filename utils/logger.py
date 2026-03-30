"""
    日志工具类

"""
import logging #python 内置日志模块
import os # 操作系统接口，用于创建目录
import datetime # 日期时间，用于生成日志文件名


def setup_logger(name=__name__, log_level=logging.INFO):
    """
        配置日志
        :param name: 日志名称 当前模块名
        :param log_level: 日志级别
        :return: Logger 对象
        """
    # 创建 logs 目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志文件名
    log_file = f"{log_dir}/test_{datetime.now().strftime('%Y%m%d')}.log"

    # 创建 logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)  # 设置日志级别（INFO 及以上才记录）

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 文件 handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)

    # 控制台 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# 全局 logger
logger = setup_logger()
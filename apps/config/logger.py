# -*- coding=utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler

# 本地调试用的代理
PROXIES = {
    "http": "http://127.0.0.1:1087",
    "https": "http://127.0.0.1:1087",
}


def setup_log():
    """
    日志打印方式s
    :return:
    """
    # 文件输出
    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)
    # logger.handlers.clear()
    # formatter = logging.Formatter(
    #     "[%(asctime)s] [%(threadName)s] [%(levelname)s] [%(module)s.%(funcName)s] [%(filename)s:%(lineno)d] %(message)s")
    # filehandler = logging.handlers.TimedRotatingFileHandler("/Users/rizhiyi/github/MusicDecoder/log/musicdecoder.log",
    #                                                         when='d',
    #                                                         interval=1,
    #                                                         backupCount=7)
    # filehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"
    # filehandler.setFormatter(formatter)
    # logger.addHandler(filehandler)

    # 终端输出
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(threadName)s] [%(levelname)s] [%(module)s.%(funcName)s] [%(filename)s:%(lineno)d] %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    return logger

# Source Generated with Decompyle++
# File: CacheLog.pyc (Python 3.9)

import time
from datetime import datetime
import os
import logging
logger = logging.getLogger('linkplay')
fileHandler = None
streamHandler = None

def startCacheLog(path, cache = (False,)):
    ts = time.time()
    st = datetime.fromtimestamp(ts).strftime('%m%d%H%M%S')
    logFilePath = path / ('%s.log' % st)
    logger = logging.getLogger('linkplay')
    formatter = logging.Formatter('%(asctime)s [%(threadName)s] [%(levelname)-5.5s] [%(filename)s]%(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    if cache:
        fileHandler = logging.FileHandler(str(logFilePath), 'w', **('mode',))
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)


def stopCacheLog():
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.handlers = []


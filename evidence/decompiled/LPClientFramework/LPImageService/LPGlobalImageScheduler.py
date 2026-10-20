# Source Generated with Decompyle++
# File: LPGlobalImageScheduler.pyc (Python 3.9)

'''
全局图片请求调度器。
'''
import itertools
import logging
import queue
import threading
from typing import Any, Callable, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
logger = logging.getLogger('linkplay')

class _LPGlobalImageScheduledJob:
    
    def __init__(self = None, key = None, task = None, priorityRank = (None,), callback = {
        'key': str,
        'task': Callable[([], Any)],
        'priorityRank': int,
        'callback': Optional[Callable[([
            Any], None)]],
        'return': None }):
        '''
        初始化图片调度任务。

        :param key: 任务唯一键。
        :param task: 实际执行函数。
        :param priorityRank: 优先级序号，值越小优先级越高。
        :param callback: 完成后的订阅回调。
        :return: None。
        '''
        if not key:
            pass
        self.key = str('').strip()
        self.task = task
        self.priorityRank = int(priorityRank)
        self.callbacks = [
            callback] if callback else []
        self.generation = 0
        self.started = False



class _LPGlobalImageWorkerPool:
    
    def __init__(self = None, name = None, workerCount = None, deliveryHandler = {
        'name': str,
        'workerCount': int,
        'deliveryHandler': Callable[([
            str,
            str,
            List[Callable[([
                Any], None)]],
            Any], None)],
        'return': None }):
        '''
        初始化固定工作池。

        :param name: 工作池名称。
        :param workerCount: 固定 worker 数量。
        :param deliveryHandler: 完成后投递回主线程的函数。
        :return: None。
        '''
        if not name:
            pass
        self._name = str('').strip()
        self._worker_count = max(1, int(workerCount))
        self._delivery_handler = deliveryHandler
        self._lock = threading.RLock()
        self._queue = queue.PriorityQueue()
        self._jobs = { }
        self._sequence = itertools.count()
        self._threads = []
        self._submitted_count = 0
        self._deduplicated_count = 0
        self._promoted_count = 0
        self._completed_count = 0
        self._failed_count = 0
        for index in range(self._worker_count):
            worker = threading.Thread(self._worker_loop, f'''GlobalImage-{self._name}-{index}''', True, **('target', 'name', 'daemon'))
            worker.start()
            self._threads.append(worker)

    
    def submit(self, jobKey = None, task = None, callback = None, priorityRank = {
        'jobKey': str,
        'task': Callable[([], Any)],
        'callback': Optional[Callable[([
            Any], None)]],
        'priorityRank': int,
        'return': None }):
        '''
        提交任务到工作池，重复 key 只追加回调并按需提升优先级。

        :param jobKey: 任务唯一键。
        :param task: 实际执行函数。
        :param callback: 完成后的订阅回调。
        :param priorityRank: 优先级序号。
        :return: None。
        '''
        if not jobKey:
            pass
        key = str('').strip()
        if not key:
            return None
        with None._lock:
            job = self._jobs.get(key)
            if job is None:
                job = _LPGlobalImageScheduledJob(key, task, priorityRank, callback)
                self._jobs[key] = job
                self._submitted_count += 1
                self._enqueue(job)
            None(None, None, None)
            return None
            self._deduplicated_count += 1
            if callback is not None:
                job.callbacks.append(callback)
            if job.started and int(priorityRank) < int(job.priorityRank):
                job.priorityRank = int(priorityRank)
                job.generation += 1
                self._promoted_count += 1
                self._enqueue(job)
            self(None, None, None)
        with None:
            i
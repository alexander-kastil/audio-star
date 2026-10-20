# Source Generated with Decompyle++
# File: LPWiiMRadioRequestScheduler.pyc (Python 3.9)

'''
WiiMRadio 统一请求调度器。
'''
import itertools
import queue
import threading
from typing import Any, Callable, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from LPClientFramework.LPUtility import logger

class _LPWiiMRadioScheduledJob:
    
    def __init__(self = None, key = None, task = None, priorityRank = (None,), callback = {
        'key': str,
        'task': Callable[([], Any)],
        'priorityRank': int,
        'callback': Optional[Callable[([
            Any], None)]],
        'return': None }):
        '''
        初始化内部调度任务。

        :param key: 任务唯一键。
        :param task: 实际执行函数。
        :param priorityRank: 当前优先级序号，值越小优先级越高。
        :param callback: 结果订阅回调。
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



class _LPWiiMRadioWorkerPool:
    
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
        初始化工作池。

        :param name: 工作池名称。
        :param workerCount: 固定工作线程数量。
        :param deliveryHandler: 任务完成后的投递函数。
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
        for index in range(self._worker_count):
            worker = threading.Thread(self._worker_loop, f'''WiiMRadio-{self._name}-{index}''', True, **('target', 'name', 'daemon'))
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
        提交任务到工作池，若存在相同 key 则仅追加订阅并在必要时提升优先级。

        :param jobKey: 任务唯一键。
        :param task: 实际执行函数。
        :param callback: 结果订阅回调。
        :param priorityRank: 当前优先级序号。
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
                job = _LPWiiMRadioScheduledJob(key, task, priorityRank, callback, **('key', 'task', 'priorityRank', 'callback'))
                self._jobs[key] = job
                self._enqueue(job)
            None(None, None, None)
            return None
            if callback is not None:
                job.callbacks.append(callback)
            if job.started and priorityRank < job.priorityRank:
                job.priorityRank = int(priorityRank)
                job.generation += 1
                self._enqueue(job)
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def _enqueue(self = None, job = None):
        '''
        将任务按当前优先级压入优先队列。

        :param job: 内部任务对象。
        :return: None。
        '''
        self._queue.put(
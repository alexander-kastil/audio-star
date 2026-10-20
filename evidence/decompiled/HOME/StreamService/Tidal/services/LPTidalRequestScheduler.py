# Source Generated with Decompyle++
# File: LPTidalRequestScheduler.pyc (Python 3.9)

'''
TIDAL 异步请求调度器。
'''
import queue
import threading
import logging
import time
from dataclasses import dataclass, field
from itertools import count
from typing import Any, Callable, Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
logger = logging.getLogger('linkplay')
LPTidalRequest = dataclass(<NODE:12>)
_ScheduledJob = dataclass(<NODE:12>)

class LPTidalRequestScheduler(QObject):
    '''优先级异步请求调度器，支持入队、取消和并发控制。'''
    _deliveryReady = pyqtSignal(str, object)
    _STOP_JOB_KEY = '__tidal_scheduler_stop__'
    MAIN_THREAD_WARN_MS = 16
    
    def __init__(self = None, parent = None, maxWorkers = None):
        '''
        初始化调度器。

        :param parent: 父级 QObject。
        :param maxWorkers: 工作线程数量。
        :return: None。
        '''
        super().__init__(parent)
        self._lock = threading.RLock()
        self._queue = queue.PriorityQueue()
        self._jobs = { }
        self._tag_map = { }
        self._sequence = count()
        self._workers = []
        self._max_workers = max(1, int(maxWorkers))
        self._active_jobs = 0
        self._closed = False
        self._deliveryReady.connect(self._dispatchDelivery)
        self._start_workers()

    
    def isShutdown(self = None):
        '''
        返回调度器是否已经关闭。

        :return: 已关闭返回 True。
        '''
        return self._closed

    isShutdown = None(isShutdown)
    
    def _start_workers(self = None):
        '''
        启动工作线程。

        :return: None。
        '''
        if self._closed:
            return None
        for index in None(self._max_workers):
            worker = threading.Thread(self._worker_loop, f'''TidalScheduler-{index}''', True, **('target', 'name', 'daemon'))
            worker.start()
            self._workers.append(worker)

    
    def shutdown(self = None, wait = None, timeout = None):
        '''
        关闭调度器并通知后台线程退出。

        :param wait: 是否等待线程退出。
        :param timeout: 每个线程最多等待秒数。
        :return: None。
        '''
        with self._lock:
            if self._closed:
                pass
            None(None, None, None)
            return None
            self._closed = True
            self._jobs.clear()
            self._tag_map.clear()
            workers = list(self._workers)
            self._workers = []
            None(None, None, None)
        with None:
            if not None:
                pass
        for _ in workers:
            self._queue.put((-1000000000, next(self._sequence), self._STOP_JOB_KEY, -1))
        if not wait:
            return None
        current_thread = None.current_thread()
        join_timeout = max(0, float(timeout))
        for worker in workers:
            if worker is current_thread:
                continue
            worker.join(join_timeout)

    
    def enqueue(self = None, request = None, priority = None):
        '''
        入队一个请求。

        :param request: TIDAL 请求对象。
        :param priority: 优先级，数值越小越先执行。
        :return: None。
        '''
        if not isinstance(request, LPTidalRequest):
            return None
        if not request.key:
            pass
        job_key = None('').strip()
        if not job_key:
            return None
        with None._lock:
            if self._closed:
                pass
            None(None, None, None)
            return None
            job = self._jobs.get(job_key)
            if job is None:
                job = _ScheduledJob(request, int(priority), **('request', 'priority'))
                if request.callback is not None:
                    job.callbacks.append(request.callback)
                self._jobs[job_key] = job
                if request.tag:
                    self._tag_map.setdefault(request.tag, set()).add(job_key)
                self._enqueue_locked(job)
            None(None, None, None)
            return None
            if request.callback is not None:
                job.callbacks = [
                    request.callback]
            if not int(priority) < job.priority and job.started:
                job.priority = int(priority)
                job.generation += 1
                self._enqueue_locked(job)
            None(None, None, None)
        with None:
            if not None:
                pass

    
    def cancelByTag(self = None, tag = None):
        '''
        取消指定 tag 下尚未开始的任务。

        :param tag: 任务标签。
        :return: None。
        '''
        if not tag:
            pass
        normalized = str('').strip()
        if not normalized:
            return None
        with None._lock:
            if self._closed:
                pass
            None(None, None, None)
            return None
            job_keys = self._tag_map.pop(normalized, set())
            for job_key in job_keys:
                job = self._jobs.get(job_key)
                if job is None or job.started:
                    continue
                job.generation += 1
                self._jobs.pop(job_key, None)
            job(None, None, None)
        with None:
            if not None:
                pass

    
    def setConcurrency(self = None, maxWorkers = None):
        '''
        设置并发数。

        :param maxWorkers: 目标并发数。
        :return: None。
        '''
        target = max(1, int(maxWorkers))
        if self._closed:
            return None
        if None <= self._max_workers:
            self._max_workers = target
            return None
        self._max_workers = None
        self._start_workers()

    
    def _enqueue_locked(self = None, job = None):
        '''
        在持锁状态下将任务压入优先队列。

        :param job: 待入队任务。
        :return: None。
        '''
        self._queue.put((job.priority, next(self._sequence), job.request.key, job.generation))

    
    def _worker_loop(self = None):
        '''
        后台工作线程主循环。

        :return: None。
        '''
        (priority, _, job_key, generation) = self._queue.get()
        
        try:
            if job_key == self._STOP_JOB_KEY:
                pass
        finally:
            self._queue.task_done()
        job = None
        with self._lock:
            if self._closed:
                pass
            None(None, None, None)
            self._queue.task_done()
            continue
            current = self._jobs.get(job_key)
            if current is None:
                pass
            None(None, None, None)
            self._queue.task_done()
            continue
            if current.started:
                pass
            None(None, None, None)
            self._queue.task_done()
            continue
            if current.generation != generation:
                pass
            None(None, None, None)
            self._queue.task_done()
            continue
            if current.priority != int(priority):
                pass
            None(None, None, None)
            self._queue.task_done()
            continue
            current.started = True
            self._active_jobs += 1
            active_at_start = self._active_jobs
            pending_at_start = len(self._jobs)
            job = current
            self(None, None, None)
        with None:
            if not None:
                pass

        if job is None:
            pass
        self._queue.task_done()
        continue
        started_at = time.monotonic()
        queue_wait_ms = int((started_at - job.enqueuedAt) * 1000)
        queue_depth_at_start = self._queue.qsize()
    # WARNING: Decompyle incomplete

    
    def _dispatchDelivery(self = None, jobKey = None, payloadBundle = pyqtSlot(str, object)):
        '''
        在主线程派发调度结果。

        :param jobKey: 任务唯一键。
        :param payloadBundle: `(callbacks, payload, metrics)` 元组。
        :return: None。
        '''
        if self._closed:
            return None
        callbacks = None
        payload = None
        metrics = { }
        if isinstance(payloadBundle, tuple) and len(payloadBundle) in frozenset({2, 3}):
            if isinstance(payloadBundle[0], list):
                callbacks = payloadBundle[0]
            payload = payloadBundle[1]
            if len(payloadBundle) == 3 and isinstance(payloadBundle[2], dict):
                metrics = payloadBundle[2]
        dispatch_started_at = time.monotonic()
        if not metrics.get('workerFinishedAt', dispatch_started_at):
            pass
        worker_finished_at = float(dispatch_started_at)
        delivery_wait_ms = int(max(0, dispatch_started_at - worker_finished_at) * 1000)
        callback_elapsed_values = []
    # WARNING: Decompyle incomplete

    _dispatchDelivery = None(_dispatchDelivery)
    __classcell__ = None


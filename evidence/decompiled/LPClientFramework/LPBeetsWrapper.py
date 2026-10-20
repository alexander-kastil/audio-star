# Source Generated with Decompyle++
# File: LPBeetsWrapper.pyc (Python 3.9)

import optparse
import codecs
import sqlite3
import sys
import copy
from pathlib import Path
from beets import ui
from beets import library
from beets import dbcore
from beets import util
from beets import config as beetsconfig
from beets.ui import _setup, SubcommandsOptionParser, _open_library, _configure, decargs, commands
from beets.ui import get_path_formats, get_replacements
from beets import importer
from beets import plugins as beetsplugins
import os
from threading import Thread
import shutil
import yaml
import musicbrainzngs
import json
import time
import queue
import threading
from datetime import datetime
from collections import deque
import pickle
from watchdog.tricks import Trick
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.observers.polling import PollingEmitter
from watchdog.observers.api import BaseObserver
from watchdog.utils.dirsnapshot import DirectorySnapshot
from watchdog.utils.dirsnapshot import DirectorySnapshotDiff

class LPPollingEmitter(PollingEmitter):
    '''允许外部预设 _snapshot 的 PollingEmitter，避免启动时重复扫描目录。

    当 _snapshot 已由外部（initDiff）预设时，on_thread_start 跳过全量扫描。
    '''
    
    def on_thread_start(self = None):
        if self._snapshot is not None:
            return None
        None().on_thread_start()

    __classcell__ = None


class LPPollingObserver(BaseObserver):
    '''使用 LPPollingEmitter 的 PollingObserver，支持启动时注入预扫描快照。'''
    
    def __init__(self = None, timeout = None):
        super().__init__(LPPollingEmitter, timeout, **('emitter_class', 'timeout'))

    __classcell__ = None

from LPClientFramework import LPMusicDatabase, LPUtility, LPWikipedia
from LPClientFramework.LPPlayList import LPLocalMusicPlayList
from LPClientFramework.LPUtility import logger
from LPPermission.LPPermissionUtils import LPPermissionUtils
UPNP_DIRID_ALLMUSICREROOT = '0$4'
UPNP_DIRID_GENREROOT = '0$5'
UPNP_DIRID_ALBUMROOT = '0$7'
UPNP_DIRID_ARTISTROOT = '0$6'
UPNP_DIRID_FOLDERROOT = '0$14'
UPNP_DIRID_PLAYLISTROOT = '0$F'
import requests
DIS_C = '<redacted>'
DIS_S = '<redacted>'
from enum import Enum
glib = None

def _normalizePathString(path):
    '''
    将输入路径统一规范化为字符串。

    参数:
        path (str | Path | None): 原始路径。
    返回:
        str | None: 规范化后的路径字符串；输入为空时返回 None。
    '''
    if path is None:
        return None
    return None(Path(path))


def _isSupportedMusicFilePath(path):
    '''
    判断路径是否为支持的音频文件。

    参数:
        path (str | Path | None): 待检查路径。
    返回:
        bool: 是支持的音频文件路径时返回 True，否则返回 False。
    '''
    normalizedPath = _normalizePathString(path)
    if normalizedPath is None:
        return False
    suffix = None(normalizedPath).suffix[1:].lower()
    if len(suffix) == 0:
        return False
    return None in LPUtility.musicFileType


def _normalizeSupportedMusicFilePath(path, requireExists = (False,)):
    '''
    规范化并校验单文件任务输入路径。

    参数:
        path (str | Path | None): 待处理路径。
        requireExists (bool): 是否要求路径当前存在。
    返回:
        str | None: 合法的音频文件路径；非法或不满足条件时返回 None。
    '''
    normalizedPath = _normalizePathString(path)
    if normalizedPath is None:
        return None
    if None.path.isdir(normalizedPath):
        return None
    if not None(normalizedPath):
        return None
    if not None and os.path.exists(normalizedPath):
        return None


def _iterMusicFilePaths(dirPath):

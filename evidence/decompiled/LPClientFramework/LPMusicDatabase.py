# Source Generated with Decompyle++
# File: LPMusicDatabase.pyc (Python 3.9)

'''本地音乐主库（SQLite）的共享访问契约。

Phase 0 起 Recently 与 beets 共用同一个主库文件 ``{userDataDir}/beets/musiclibrary.db``；
本模块是主库路径、连接参数与 busy_timeout 的唯一来源，避免各业务模块各自拼接路径
或重复设置 PRAGMA。

职责边界：
- 提供 :func:`databasePath` / :func:`connect` 与 ``BUSY_TIMEOUT_MS`` / ``JOURNAL_MODE`` 常量；
- 提供 beets 写门禁状态的**只读**查询，自身不持有冻结状态（冻结唯一入口是
  ``LPBeetsTaskCoordinator``）；
- 不在模块级导入 ``LPBeetsWrapper``，也不导入 ``LPMusicLibrary`` 包（其包级导入会连带
  ``LPRecentlyManager`` / ``LPPlayList``），避免环依赖与包级副作用。
'''
import sqlite3
from pathlib import Path
from LPClientFramework import LPUtility
DATABASE_DIR_NAME = 'beets'
DATABASE_FILE_NAME = 'musiclibrary.db'
BUSY_TIMEOUT_MS = 5000
JOURNAL_MODE = 'wal'

def databasePath():
    '''返回本地音乐主库文件路径。

    参数:
        无。
    返回:
        Path: ``{userDataDir}/beets/musiclibrary.db`` 的绝对路径。
    '''
    return (Path(LPUtility.userDataDir) / DATABASE_DIR_NAME / DATABASE_FILE_NAME).resolve()


def connect(path, readonly = (None, False)):
    '''创建主库 sqlite3 连接并统一设置 PRAGMA。

    参数:
        path (str | Path | None): 目标库路径，未传时使用 :func:`databasePath`。
        readonly (bool): 为 True 时以只读 URI 打开，不创建目录与文件。
    返回:
        sqlite3.Connection: 已设置 ``busy_timeout`` / ``journal_mode`` / ``row_factory`` 的连接。
    '''
    target = Path(path) if path else databasePath()
    if readonly:
        conn = sqlite3.connect('file:%s?mode=ro' % target.as_posix(), True, False, **('uri', 'check_same_thread'))
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA busy_timeout=%d;' % BUSY_TIMEOUT_MS)
        return conn
    None.parent.mkdir(True, True, **('parents', 'exist_ok'))
    conn = sqlite3.connect(str(target), False, **('check_same_thread',))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA busy_timeout=%d;' % BUSY_TIMEOUT_MS)
    currentMode = conn.execute('PRAGMA journal_mode;').fetchone()[0]
    if str(currentMode).lower() != JOURNAL_MODE:
        conn.execute('PRAGMA journal_mode=%s;' % JOURNAL_MODE)
    return conn


def _beetsWrapperModule():
    '''惰性取得 LPBeetsWrapper 模块。

    参数:
        无。
    返回:
        module | None: 已加载或可导入时返回模块，导入失败时返回 None。
    '''
    pass
# WARNING: Decompyle incomplete


def beetsWriteBlockedReason():
    '''只读查询 beets 写是否被阻塞。

    参数:
        无。
    返回:
        str | None: beets 侧存在独占写任务时返回原因描述，未阻塞时返回 None。
    '''
    wrapper = _beetsWrapperModule()
    if wrapper is None:
        return None
    activeSessionQuery = None(wrapper, 'activeStagedMergeSession', None)
    if callable(activeSessionQuery) and activeSessionQuery() is not None:
        return 'staged beets import in progress'
    if None.isDBBusy():
        return 'beets exclusive write in progress'


# Source Generated with Decompyle++
# File: LPFeedbackLogPackager.pyc (Python 3.9)

'''Feedback 日志和图片的 Android 兼容加密 ZIP 打包器。'''
import logging
import shutil
import tempfile
import time
import zipfile
from pathlib import Path
from Crypto.Cipher import AES
from PIL import Image, ImageOps
logger = logging.getLogger('linkplay')

class LPFeedbackWorkDirectoryError(RuntimeError):
    '''打包用工作/暂存目录创建失败，对应埋点错误码 3006。

    单独定义异常类型，使编排器能把它与打包/加密失败（3007）区分开，
    从而各自上报文档规定的错误码。
    '''
    pass


class LPFeedbackLogPackager:
    '''将应用日志和用户图片复制、加密并压缩为单个反馈 ZIP。'''
    MAX_ATTACHMENT_COUNT = 5
    MAX_LOG_AGE_SECONDS = 604800
    MAX_LOG_FILE_COUNT = 20
    MAX_TOTAL_LOG_SIZE = 20971520
    _AES_DIR = 'AES'
    
    def __init__(self, workDirectory, aesKey):
        '''初始化打包器。

        参数:
            workDirectory (str|Path): 临时工作目录根路径。
            aesKey (str): Android 兼容的 16 字节 AES 密钥。
        返回:
            无。
        异常:
            ValueError: AES 密钥长度不是 16 字节时抛出。
        '''
        self._workDirectory = Path(workDirectory)
        self._aesKey = str(aesKey).encode('utf-8')
        if len(self._aesKey) != AES.block_size:
            raise ValueError('Feedback AES key must contain 16 bytes.')

    
    def createArchive(self, submissionId, logDirectory, attachmentPaths, firmwareDirectory = (None,)):
        '''创建一次提交对应的加密 ZIP 包。

        暂存目录结构对齐安卓 LogsBaseDir：日志入 App/、图片入 Picture/、固件入 firmware/。
        服务端按 ZIP entry 路径前缀（App/Crash → AES，其他 .log → RC4，非 .log 原样）路由解密。

        参数:
            submissionId (str): 当前提交唯一标识。
            logDirectory (str|Path): 应用日志目录。
            attachmentPaths (list[str]): 用户已选择的图片路径。
            firmwareDirectory (str|Path|None): 本次提交专属的固件日志源目录；缺省回落到
                ``<logDirectory>/firmware``。无论源目录在哪，ZIP 内仍以 ``firmware/`` 为根。
        返回:
            tuple[Path, Path]: ZIP 路径和本次工作目录路径。
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def cleanup(self, workPath):
        '''删除一次提交产生的临时目录。

        参数:
            workPath (str|Path|None): 待清理的工作目录。
        返回:
            None。
        '''
        if workPath:
            shutil.rmtree(str(workPath), True, **('ignore_errors',))

    
    def _copyLogs(self, logDirectory, stagingRoot, firmwareDirectory = (None,)):
        '''按时间、数量和容量策略复制应用日志到暂存目录的 App/ 分类下。

        firmwareDirectory 下的固件日志原样复制到暂存根的 firmware/ 下
        （保持明文，不加密），与安卓 LogsFirmwareDir 及服务端路由一致。

        参数:
            logDirectory (str|Path): 源日志目录。
            stagingRoot (Path): ZIP 暂存根目录（日志会写入其 App/ 子目录）。
            firmwareDirectory (str|Path|None): 固件日志源目录；缺省用 ``<logDirectory>/firmware``。
        返回:
            None。
        '''
        sourcePath = Path(logDirectory)
        if not sourcePath.is_dir():
            return None
        targetDirectory = None / 'App'
        targetDirectory.mkdir(True, True, **('parents', 'exist_ok'))
        collectedAt = time.time()
        cutoffTime = collectedAt - self.MAX_LOG_AGE_SECONDS
        candidates = self._findLogCandidates(sourcePath, cutoffTime)
        copiedCount = 0
        copiedSize = 0
    # WARNING: Decompyle incomplete

    
    def _findLogCandidates(self, sourceDirectory, cutoffTime):
        '''查找时间窗口内的普通日志文件并按新到旧排序。

        参数:
            sourceDirectory (Path): 日志根目录。
            cutoffTime (float): 允许收集的最早修改时间戳。
        返回:
            list[Path]: 按修改时间降序、相对路径升序排列的候选文件。
        '''
        candidates = []
    # WARNING: Decompyle incomplete

    
    def _copyLogFile(self, sourcePath, sourceDirectory, targetDirectory):
        '''复制单个日志并在失败时清理不完整目标文件。

        参数:
            sourcePath (Path): 待复制日志文件。
            sourceDirectory (Path): 日志根目录。
            targetDirectory (Path): ZIP 暂存日志目录。
        返回:
            bool: 复制成功时返回 True，否则返回 False。
        '''
        targetPath = targetDirectory / sourcePath.relative_to(sourceDirectory)
    # WARNING: Decompyle incomplete

    
    def _copyAttachments(self, attachmentPaths, targetDirectory):
        '''将最多五张图片压缩为 JPEG 并写入 Picture 目录（不加密，保持明文）。

        与安卓一致：图片以明文存入 ZIP，服务端对非 .log 文件原样保存不解密。

        参数:
            attachmentPaths (list[str]): UI 侧已选择的图片路径。
            targetDirectory (Path): ZIP 暂存目录中的 Picture 路径。
        返回:
            None。
        '''
        targetDirectory.mkdir(True, True, **('parents', 'exist_ok'))
        if not attachmentPaths:
            pass
    # WARNING: Decompyle incomplete

    
    def _encryptTree(self, rootDirectory):
        '''递归加密 .log 文件，保留原始文件名，密文写入同级 AES/ 子目录。

        对齐安卓 StatisticsAESHelper：仅加密 .log 文件，密文落到父目录下的 AES/
        子目录并保留原文件名；非 .log 文件（如图片）与 firmware 目录保持明文。

        参数:
            rootDirectory (Path): 待处理目录根路径。
        返回:
            None。
        '''
        for path in sorted(Path(rootDirectory).rglob('*'), True, **('reverse',)):
            if not path.is_file():
                continue
            if any((lambda .0: for parent in .0:
'firmware' in parent.name.lower())(path.parents)):
                continue
            if path.suffix.lower() != '.log':
                continue
            if path.parent.name == self._AES_DIR:
                continue
            aesDirectory = path.parent / self._AES_DIR
            aesDirectory.mkdir(True, True, **('parents', 'exist_ok'))
            encryptedPath = aesDirectory / path.name
            encryptedPath.write_bytes(self._encryptBytes(path.read_bytes()))
            path.unlink()

    
    def _encryptBytes(self, sourceBytes):
        """按 Android Cipher.getInstance('AES') 的 ECB/PKCS7 语义加密字节。

        参数:
            sourceBytes (bytes): 待加密的原始文件内容。
        返回:
            bytes: AES-128-ECB PKCS7 密文。
        """
        paddingLength = AES.block_size - len(sourceBytes) % AES.block_size
        paddedBytes = sourceBytes + bytes([
            paddingLength]) * paddingLength
        return AES.new(self._aesKey, AES.MODE_ECB).encrypt(paddedBytes)

    
    def _createZip(self, sourceDirectory, archivePath):
        '''将加密后的暂存目录写为 ZIP 文件。

        参数:
            sourceDirectory (Path): ZIP 内容根目录。
            archivePath (Path): 输出 ZIP 文件路径。
        返回:
            None。
        '''
        with zipfile.ZipFile(archivePath, 'w', zipfile.ZIP_DEFLATED, **('compression',)) as archiveFile:
            for path in sorted(Path(sourceDirectory).rglob('*')):
                if path.is_file():
                    archiveFile.write(path, path.relative_to(sourceDirectory).as_posix())
                None(None, None, None)
            with None:
                if not None:
                    pass



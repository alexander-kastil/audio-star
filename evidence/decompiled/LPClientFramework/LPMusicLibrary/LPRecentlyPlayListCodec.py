# Source Generated with Decompyle++
# File: LPRecentlyPlayListCodec.pyc (Python 3.9)

'''
Recently Played 的播放列表快照编解码层。

负责把 ``detail["playList"]`` 在「具体音源的播放列表对象」和「可落盘的字典」之间互转。
所有音源恢复播放上下文时都走这里，统一处理对象属性映射、headType 还原、index 归一化和缺失字段补默认值。
'''
from LPClientFramework.LPPlayList.LPPlayList import headerTypeValue, headerTypeEnum, LP_HEADER_TYPE_VALUE_MAP, LPHeaderType
from LPClientFramework.LPUtility import applyDictToObject, logger

class LPRecentlyPlayListCodec(object):
    '''Recently 播放列表快照的编解码器，全部为静态方法，无需实例化。'''
    
    def _toStorableValue(value):
        '''
        把单个属性值归一成可 JSON 序列化的结构。

        - 基础类型（None / bool / int / float / str）原样保留
        - dict / list 递归处理其中元素
        - 其它对象（嵌套播放项、状态机、回调等）一律丢弃，避免落库失败
        '''
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if None(value, dict):
            return (lambda .0: pass# WARNING: Decompyle incomplete
)(value.items())
        if None(value, (list, tuple)):
            return (lambda .0: [ LPRecentlyPlayListCodec._toStorableValue(v) for v in .0 ])(value)

    _toStorableValue = staticmethod(_toStorableValue)
    
    def _objectToDict(obj, excludeKeys = (None,)):
        '''把对象的公开属性浅拷贝成字典，跳过非可序列化字段。'''
        if obj is None:
            return None
        if not excludeKeys:
            pass
        excludeKeySet = None([])
        result = { }
        for key, value in vars(obj).items():
            if key.startswith('_'):
                continue
            if key in excludeKeySet:
                continue
            if callable(value):
                continue
            stored = LPRecentlyPlayListCodec._toStorableValue(value)
            if not stored is None and value is not None and isinstance(value, (dict, list, tuple)):
                continue
            result[key] = stored
        return result

    _objectToDict = staticmethod(_objectToDict)
    
    def playListToDetail(playList, showDict, extra = (None, None)):
        '''
        把播放列表对象序列化成可写入 ``detail`` 的字典。

        Args:
            playList: 具体音源的播放列表对象，需包含 header / list / index / account。
            showDict: UI 行为信息，例如是否允许 openMore、canNavigate。
            extra: 需要额外合并进 detail 的字段。

        Returns:
            ``{"playList": ..., "show": ..., "account": ...}`` 形式的字典。
        '''
        if playList is None:
            return { }
        if not getattr(playList, 'list', None):
            pass
        if not getattr(playList, 'index', 0):
            pass
        playListDict = {
            'header': None._objectToDict(getattr(playList, 'header', None)),
            'list': (lambda .0: [ LPRecentlyPlayListCodec._objectToDict(item) for item in .0 ])([]),
            'index': 0 }
        header = getattr(playList, 'header', None)
        if header is not None:
            playListDict['header']['headType'] = headerTypeValue(getattr(header, 'headType', 0))
        accountDict = LPRecentlyPlayListCodec._objectToDict(getattr(playList, 'account', None))
        detail = {
            'playList': playListDict,
            'show': dict(showDict) if showDict else { },
            'account': accountDict }
        if extra and isinstance(extra, dict):
            detail.update(extra)
        return detail

    playListToDetail = staticmethod(playListToDetail)
    
    def _dictToObject(target, valueDict, excludeKeys = (None,)):
        '''applyDictToObject 的薄封装，统一排除键。'''
        return applyDictToObject(target, valueDict, excludeKeys)

    _dictToObject = staticmethod(_dictToObject)
    
    def _restoreHeader(headerDict, headerClass, source):
        header = headerClass()
        LPRecentlyPlayListCodec._dictToObject(header, headerDict)
        header.headType = headerTypeEnum(getattr(header, 'headType', 0))
        if not getattr(header, 'mediaSource', None):
            header.mediaSource = source
        return header

    _restoreHeader = staticmethod(_restoreHeader)
    
    def _restoreItem(itemDict, itemClass, source):
        item = itemClass()
        LPRecentlyPlayListCodec._dictToObject(item, itemDict)
        if not getattr(item, 'trackSource', None):
            item.trackSource = source
        return item

    _restoreItem = staticmethod(_restoreItem)
    
    def _restoreAccount(accountDict, accountClass, source, normalizeAccount = (None,)):
        account = accountClass()
        LPRecentlyPlayListCodec._dictToObject(account, accountDict)
        if not getattr(account, 'source', None):
            account.source = source
    # WARNING: Decompyle incomplete

    _restoreAccount = staticmethod(_restoreAccount)
    
    def playListFromDetail(detailDict, playListClass, headerClass, itemClass, source, accountClass, accountExcludeKeys, normalizeHeader, normalizeAccount, normalizeItem = (None, None, None, None, None)):
        '''
        从 ``detail["playList"]`` 还原出具体音源的播放列表对象。

        Args:
            detailDict: recently 记录中的 detail 字典。
            playListClass: 目标播放列表类型。
            headerClass: 目标 header 类型。
            itemClass: 目标播放项类型。
            source: 音源标识，用于给缺失的 mediaSource / trackSource / account.source 补默认值。
            accountClass: 目标账号类型，为 None 时跳过账号恢复。
            accountExcludeKeys: 恢复账号时需要跳过的字段。
            normalizeHeader: 对恢复出的 header 做二次修正的回调。
            normalizeAccount: 对恢复出的 account 做二次修正的回调。
            normalizeItem: 对恢复出的每个 item 做二次修正的回调。

        Returns:
            可继续使用的播放列表对象；detailDict 无效时返回 None。
        '''
        if not isinstance(detailDict, dict):
            return None
        playListDict = None.get('playList')
        if not isinstance(playListDict, dict):
            return None
        playList = None()
        headerDict = playListDict.get('header')
    # WARNING: Decompyle incomplete

    playListFromDetail = staticmethod(playListFromDetail)
    
    def currentItemFromPlayList(playList):
        '''
        取播放列表当前播放项，越界时回退到第一项。

        Args:
            playList: 已反序列化的播放列表对象。

        Returns:
            当前播放项对象；列表为空时返回 None。
        '''
        if not playList is None or getattr(playList, 'list', None):
            return None
        if not None(playList, 'index', 0):
            pass
        index = 0
    # WARNING: Decompyle incomplete

    currentItemFromPlayList = staticmethod(currentItemFromPlayList)
    
    def showValue(detailDict, key, default = (None,)):
        '''
        读取 detail["show"] 中的 UI 行为字段。

        Args:
            detailDict: recently detail 字典。
            key: 字段名，例如 openMore / canNavigate。
            default: 字段缺失时的回退值。

        Returns:
            字段值或 default。
        '''
        if not isinstance(detailDict, dict):
            return default
        showDict = None.get('show')
        if not isinstance(showDict, dict):
            return default
        return None.get(key, default)

    showValue = staticmethod(showValue)


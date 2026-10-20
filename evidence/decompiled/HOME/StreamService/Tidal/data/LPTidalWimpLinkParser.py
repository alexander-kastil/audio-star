# Source Generated with Decompyle++
# File: LPTidalWimpLinkParser.pyc (Python 3.9)

'''
TIDAL bio/review 文本 wimpLink 解析器。

将 API 返回的 raw text 中的 [wimpLink ...][/wimpLink] 标签和 <br/> 换行
转换为结构化片段列表，供 QML 端渲染可点击链接和保留换行。
'''
import html
import re
from typing import Any, Dict, List
_WIMP_LINK_RE = re.compile('\\[wimpLink\\s+(\\w+)=\\"([^\\"]*)\\"\\](.*?)\\[/wimpLink\\]', re.DOTALL)
_ATTR_TO_LINK_TYPE: Dict[(str, str)] = {
    'artistId': 'artist',
    'albumId': 'album',
    'trackId': 'track',
    'videoId': 'video',
    'playlistId': 'playlist' }

def _escape_html_text(raw = None):
    '''转义文本中的 HTML 特殊字符，但不影响已有的 <br/> 和 <a> 标签。'''
    return html.escape(raw, False, **('quote',))


def parseBioText(raw = None):
    '''
    解析 TIDAL bio text 中的 wimpLink 标签和 <br/> 换行。

    :param raw: API 返回的原始 bio text。
    :return: 结构化片段列表，每个片段为 dict:
             - {"type": "text", "text": "..."}   — 纯文本
             - {"type": "link", "text": "...", "linkType": "artist|album|...", "linkId": "..."}  — 可点击链接
             - {"type": "break"}                  — 换行
    '''
    if not raw:
        return []
    segments = None
    pos = 0
    for m in _WIMP_LINK_RE.finditer(raw):
        before = raw[pos:m.start()]
        if before:
            _append_text_parts(segments, before)
        attr_name = m.group(1)
        attr_value = m.group(2)
        link_text = m.group(3)
        link_type = _ATTR_TO_LINK_TYPE.get(attr_name, '')
        if link_type and attr_value:
            segments.append({
                'type': 'link',
                'text': link_text,
                'linkType': link_type,
                'linkId': attr_value })
        elif link_text:
            segments.append({
                'type': 'text',
                'text': link_text })
        pos = m.end()
    tail = raw[pos:]
    if tail:
        _append_text_parts(segments, tail)
    return segments


def _append_text_parts(segments = None, text = None):
    '''将一段纯文本按 <br/> 拆分并追加到 segments，自动合并相邻 text 片段。'''
    parts = text.split('<br/>')
    for i, part in enumerate(parts):
        if i > 0:
            segments.append({
                'type': 'break' })
        if not part:
            continue
        if segments and segments[-1]['type'] == 'text':
            segments[-1]['text'] += part
            continue
        segments.append({
            'type': 'text',
            'text': part })


def segmentsToRichText(segments = None, linkColor = None, linkHoverColor = None):

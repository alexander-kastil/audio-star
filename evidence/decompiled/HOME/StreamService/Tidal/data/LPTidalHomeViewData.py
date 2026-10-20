# Source Generated with Decompyle++
# File: LPTidalHomeViewData.pyc (Python 3.9)

'''
TIDAL 首页视图数据整理工具。
'''
from typing import Any, Dict, List, Tuple

def splitHomeSectionsForView(sectionsPayload = None):
    '''
    将首页原始区块拆分为 Featured 分类和需要渲染的内容分区。

    :param sectionsPayload: 首页原始区块列表。
    :return: `(featured_categories, visible_sections)` 二元组。
    '''
    featured_categories = []
    visible_sections = []
    for section in sectionsPayload if isinstance(sectionsPayload, list) else []:
        if not isinstance(section, dict):
            continue
        if not section.get('sectionKey', ''):
            pass
        section_key = str('')
        items = section.get('items', [])
        normalized_items = items if isinstance(items, list) else []
        if section_key == 'featured':
            featured_categories = normalized_items
            continue
        if section_key == 'featured-new-videos':
            continue
        copied_section = dict(section)
        copied_section['items'] = normalized_items
        visible_sections.append(copied_section)
    return (featured_categories, visible_sections)


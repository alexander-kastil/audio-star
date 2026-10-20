# Source Generated with Decompyle++
# File: widget_utils.pyc (Python 3.9)

'''
@Time ： 2026/8/20 14:30
@Auth ： Chris
@File ：widget_utils.py
@Desc:
    通用控件操作辅助函数。
'''
from PyQt6.QtGui import QFont

def replaceWidgetInPlace(old_widget, new_widget_class):
    '''
    将旧控件原位替换为 new_widget_class 的新实例，保留布局位置、字体与样式表。

    参数:
        old_widget (QWidget): 待替换的旧控件，必须是其父控件直接布局的成员。
        new_widget_class (type): 新控件类，构造签名需支持单个 parent 参数。
    返回:
        QWidget | None: 替换成功返回新控件；父控件无布局、旧控件不在布局中或
        无父控件时返回 None，调用方应保留旧控件作为兜底。
    '''
    parent = old_widget.parent()
    if parent is None:
        return None
    layout = None.layout()
    if layout is None:
        return None
    index = None.indexOf(old_widget)
    if index < 0:
        return None
    font = None(old_widget.font())
    style_sheet = old_widget.styleSheet()
    old_widget.setParent(None)
    old_widget.deleteLater()
    new_widget = new_widget_class(parent)
    new_widget.setFont(font)
    new_widget.setStyleSheet(style_sheet)
    layout.insertWidget(index, new_widget)
    return new_widget


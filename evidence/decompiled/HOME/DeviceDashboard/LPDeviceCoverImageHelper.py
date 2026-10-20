# Source Generated with Decompyle++
# File: LPDeviceCoverImageHelper.pyc (Python 3.9)

'''
@Time ： 2026/5/7
@Auth ： OpenCode
@File ：LPDeviceCoverImageHelper.py
@Desc: 设备列表封面图片绘制工具。
'''
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap

def coverCanvasPixmap(pixmap = None, width = None, height = None, radius = (0,)):
    '''
    将封面完整绘制到透明画布中，保持原始宽高比例并居中显示。

    参数:
        pixmap (QPixmap): 原始封面图片。
        width (int): 目标画布宽度。
        height (int): 目标画布高度。
        radius (int): 画布圆角裁剪半径，0 表示不裁剪圆角。
    返回:
        QPixmap: 透明背景的目标尺寸封面画布。
    '''
    width = max(1, int(width))
    height = max(1, int(height))
    canvas = QPixmap(width, height)
    canvas.fill(Qt.GlobalColor.transparent)
    if pixmap is None or pixmap.isNull():
        return canvas
    scaled_pixmap = None.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    draw_x = int((width - scaled_pixmap.width()) / 2)
    draw_y = int((height - scaled_pixmap.height()) / 2)
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    if radius > 0:
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, radius, radius)
        painter.setClipPath(path)
    painter.drawPixmap(draw_x, draw_y, scaled_pixmap)
    painter.end()
    return canvas


# Source Generated with Decompyle++
# File: LPPlayViewUtil.pyc (Python 3.9)

'''
@Time ： 2025/9/23 16:24
@Auth ： Chris
@File ：LPPlayViewUtil.py
@Desc:
'''
from PIL import Image
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPainterPath, QColor
from LPClientFramework.LPPalette import extractThemeColorRgbFromImage
DEFAULT_BACKGROUND_COLOR = QColor(18, 18, 18)
BACKGROUND_OVERLAY_ALPHA = 180

def setCurrentWidget(stackWidget, newWidget):
    currentWidget = stackWidget.currentWidget()
    if currentWidget and hasattr(currentWidget, 'onLeave'):
        currentWidget.onLeave()
    if stackWidget.indexOf(newWidget) == -1:
        stackWidget.addWidget(newWidget)
    stackWidget.setCurrentWidget(newWidget)
    if hasattr(newWidget, 'onEnter'):
        newWidget.onEnter()


def getPaletteBackgroundPixmap(pixmap = None, targetWidth = None, targetHeight = None, fallbackColor = (None,)):
    '''
    生成 PlayView 使用的主题色深色背景图。

    Args:
        pixmap: 原始封面图。
        targetWidth: 目标背景宽度。
        targetHeight: 目标背景高度。
        fallbackColor: 取色失败时使用的兜底颜色。

    Returns:
        根据封面主题色生成的背景 QPixmap。
    '''
    targetWidth = int(targetWidth)
    targetHeight = int(targetHeight)
    if targetWidth <= 0 or targetHeight <= 0:
        return QPixmap()
    if not None:
        pass
    backgroundColor = DEFAULT_BACKGROUND_COLOR
    themeRgb = None
    if not pixmap is not None and pixmap.isNull():
        themeRgb = extractThemeColorRgbFromImage(_pixmapToPILImage(pixmap))
    if themeRgb is not None:
        backgroundColor = QColor(themeRgb[0], themeRgb[1], themeRgb[2])
    return _buildDarkSolidBackgroundPixmap(backgroundColor, targetWidth, targetHeight)


def _pixmapToPILImage(pixmap = None):
    '''
    将 QPixmap 转换为 Pillow Image，供主题色算法分析。

    Args:
        pixmap: 原始封面图。

    Returns:
        RGBA 格式的 Pillow Image。
    '''
    qImage = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
    width = qImage.width()
    height = qImage.height()
    buffer = qImage.constBits().asstring(qImage.sizeInBytes())
    return Image.frombuffer('RGBA', (width, height), buffer, 'raw', 'RGBA', 0, 1)


def _buildDarkSolidBackgroundPixmap(color = None, targetWidth = None, targetHeight = None):
    '''
    根据输入颜色生成加深后的纯色背景图。

    Args:
        color: 背景基础颜色。
        targetWidth: 背景图宽度。
        targetHeight: 背景图高度。

    Returns:
        叠加黑色遮罩后的背景 QPixmap。
    '''
    background = Image.new('RGBA', (targetWidth, targetHeight), (color.red(), color.green(), color.blue(), 255))
    overlay = Image.new('RGBA', (targetWidth, targetHeight), (0, 0, 0, BACKGROUND_OVERLAY_ALPHA))
    background = Image.alpha_composite(background, overlay)
    bgBytes = background.tobytes('raw', 'RGBA')
    qImage = QImage(bgBytes, targetWidth, targetHeight, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qImage)


def centerCoverPixmap(pixmap = None, canvasSide = None, imageSide = None, radius = (None, 8)):
    '''
    将任意比例封面按比例缩放后绘制到正方形透明画布中心。

    :param pixmap: 原始封面图。
    :param canvasSide: 输出正方形画布边长。
    :param imageSide: 封面图缩放目标边长；为空时使用画布边长。
    :param radius: 封面圆角半径。
    :return: 已居中绘制封面的正方形 QPixmap。
    '''
    canvasSide = int(canvasSide)
    imageSide = int(imageSide if imageSide is not None else canvasSide)
    if canvasSide <= 0 and imageSide <= 0 and pixmap is None or pixmap.isNull():
        return QPixmap()
    scaled = None.scaled(imageSide, imageSide, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    rounded = _roundPixmap(scaled, radius)
    canvas = QPixmap(canvasSide, canvasSide)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    x = int((canvasSide - rounded.width()) / 2)
    y = int((canvasSide - rounded.height()) / 2)
    painter.drawPixmap(x, y, rounded)
    painter.end()
    return canvas


def _roundPixmap(pixmap = None, radius = None):
    '''
    对封面图增加圆角，避免 PlayView 工具函数反向依赖 LPUtility 造成导入环。

    :param pixmap: 需要处理的封面图。
    :param radius: 圆角半径。
    :return: 已应用圆角蒙版的 QPixmap。
    '''
    rounded = QPixmap(pixmap.width(), pixmap.height())
    rounded.fill(Qt.GlobalColor.transparent)
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    return rounded


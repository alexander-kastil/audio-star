# Source Generated with Decompyle++
# File: LPFontConfig.pyc (Python 3.9)

'''
@Time ： 2025/5/23 11:38
@Auth ： Chris
@File ：LPFontConfig.py
@Desc:
'''
import platform
WINDOWS_UI_FONT_FAMILY = 'Verdana'

def getScale(benchmarkDPI = (72,)):
    '''
    计算不同平台下的字体缩放比例。

    :param benchmarkDPI: 基准 DPI。
    :return: 字体缩放比例。
    '''
    if platform.system() == 'Darwin':
        logicalDotsPerInch = 72
    else:
        logicalDotsPerInch = 96
    return benchmarkDPI / logicalDotsPerInch

scale = getScale()

def getApplicationFont():
    '''
    获取当前应用默认字体的副本。

    :param: 无。
    :return: 当前 QApplication 默认字体；应用尚未创建时返回 Qt 默认字体。
    '''
    QFont = QFont
    import PyQt6.QtGui
    QApplication = QApplication
    import PyQt6.QtWidgets
    application = QApplication.instance()
    if application is not None:
        return QFont(application.font())
    return None()


def getStartupApplicationFont():
    '''
    获取应用启动字体，Windows 优先使用适合英文 UI 的 Segoe UI。

    :param: 无。
    :return: Windows 安装 Segoe UI 时返回对应字体，否则返回当前应用默认字体。
    '''
    font = getApplicationFont()
    if platform.system() != 'Windows':
        return font
    QFontDatabase = QFontDatabase
    import PyQt6.QtGui
    availableFamilies = QFontDatabase.families()
    resolvedFamily = next((lambda .0: 
# Source Generated with Decompyle++
# File: LPPalette.pyc (Python 3.9)

'''
iOS Palette 算法 Python 移植实现。

该模块按 iOS 端 iOSPalette 的核心流程实现：
1. 图像缩放到 112x112（保持比例）
2. RGB888 -> RGB555 量化并构建直方图
3. Median-cut 颜色分箱（最多 16 色）
4. 过滤黑/白/near-red 颜色
5. 按目标色模型（vibrant/muted/dark 等）计算分值并选色
'''
from __future__ import annotations
import math
from dataclasses import dataclass
from enum import IntFlag
from typing import Dict, List, Optional, Sequence, Tuple, Union
from PIL import Image
MAX_COLOR_NUM = 16
TARGET_IMAGE_SIZE = 112
QUANTIZE_WORD_WIDTH = 5
QUANTIZE_WORD_MASK = (1 << QUANTIZE_WORD_WIDTH) - 1
HIST_ARR_SIZE = 1 << QUANTIZE_WORD_WIDTH * 3

def constrain(amount = None, low = None, high = None):
    '''
    将数值限制在区间 [low, high] 内。

    Args:
        amount: 原始数值。
        low: 下限。
        high: 上限。

    Returns:
        限制后的数值。
    '''
    if amount > high:
        return high
    if None < low:
        return low


def truncatingRemainderDividing(a = None, b = None):
    '''
    使用 iOS 同款“截断整除余数”策略计算浮点余数。

    iOS 代码里为了跨设备稳定性，先放大成整数做 `%`，再缩回浮点。
    这里保持同样行为，且保证余数符号与 C/ObjC 一致（与 Python `%` 不同）。

    Args:
        a: 被除数。
        b: 除数。

    Returns:
        余数（浮点）。
    '''
    if b == 0:
        return 0
    intA = None(a * 1000000)
    intB = int(b * 1000000)
    if intB == 0:
        return 0
    quotient = None.trunc(intA / intB)
    intC = intA - quotient * intB
    return intC / 1e+06


def modifyWordWidthWithValue(value = None, currentWidth = None, targetWidth = None):
    '''
    按 iOS 同款逻辑做颜色位宽变换。

    Args:
        value: 原始数值。
        currentWidth: 原位宽。
        targetWidth: 目标位宽。

    Returns:
        位宽转换后的结果。
    '''
    if targetWidth > currentWidth:
        newValue = value * ((1 << targetWidth) - 1) // ((1 << currentWidth) - 1)
    else:
        newValue = value >> currentWidth - targetWidth
    return newValue & (1 << targetWidth) - 1


def quantizedRed(color = None):
    return color >> QUANTIZE_WORD_WIDTH + QUANTIZE_WORD_WIDTH & QUANTIZE_WORD_MASK


def quantizedGreen(color = None):
    return color >> QUANTIZE_WORD_WIDTH & QUANTIZE_WORD_MASK


def quantizedBlue(color = None):
    return color & QUANTIZE_WORD_MASK


def rgb888ToHsl(red = None, green = None, blue = None):
    '''
    RGB888 转 HSL，按 iOS PaletteColorUtils 实现移植。

    Args:
        red: 红色通道 [0,255]。
        green: 绿色通道 [0,255]。
        blue: 蓝色通道 [0,255]。

    Returns:
        (h, s, l)，其中 h: [0, 360]，s/l: [0, 1]。
    '''
    rf = float(red) / 255
    gf = float(green) / 255
    bf = float(blue) / 255
    maxValue = max(rf, gf, bf)
    minValue = min(rf, gf, bf)
    deltaMaxMin = maxValue - minValue
    lightness = (maxValue + minValue) / 2
    hue = 0
    saturation = 0
    if maxValue != minValue:
        if maxValue == rf:
            hue = truncatingRemainderDividing((gf - bf) / deltaMaxMin, 6)
        elif maxValue == gf:
            hue = (bf - rf) / deltaMaxMin + 2
        else:
            hue = (rf - gf) / deltaMaxMin + 4
        denominator = 1 - abs(2 * lightness - 1)
        saturation = deltaMaxMin / denominator if denominator != 0 else 0
    hue = truncatingRemainderDividing(hue * 60, 360)
    if hue < 0:
        hue += 360
    return (constrain(hue, 0, 360), constrain(saturation, 0, 1), constrain(lightness, 0, 1))


def rgb555ToHsl(rgb555 = None):
    '''
    RGB555 转 HSL。

    Args:
        rgb555: RGB555 packed color。

    Returns:
        (h, s, l)。
    '''
    red = modifyWordWidthWithValue(quantizedRed(rgb555), 5, 8)
    green = modifyWordWidthWithValue(quantizedGreen(rgb555), 5, 8)
    blue = modifyWordWidthWithValue(quantizedBlue(rgb555), 5, 8)
    return rgb888ToHsl(red, green, blue)


def hexColorToRgb(hexColor = None):
    '''
    解析 #RRGGBB 形式颜色字符串。

    Args:
        hexColor: 颜色字符串。

    Returns:
        (r, g, b) 或 None。
    '''
    if not hexColor:
        return None
    colorString = None.strip().lower()
    if colorString.startswith('#'):
        colorString = colorString[1:]
    if len(colorString) != 6:
        return None
    :
        if not hexColor:
            return None
        colorString = None.strip().lower()
        if colorString.startswith('#'):
            colorString = colorString[1:]
        if len(colorString) != 6:
            return None
        
        return (int(colorString[0:2], 16), int(colorString[2:4], 16), int(colorString[4:6], 16))
    return (int(colorString[0:2], 16), int(colorString[2:4], 16), int(colorString[4:6], 16))
# WARNING: Decompyle incomplete


class PaletteTargetMode(IntFlag):
    '''
    目标色模式，保持 iOS 枚举位定义一致。
    '''
    DEFAULT_NON_MODE_PALETTE = 0
    VIBRANT_PALETTE = 1
    LIGHT_VIBRANT_PALETTE = 2
    DARK_VIBRANT_PALETTE = 4
    LIGHT_MUTED_PALETTE = 8
    MUTED_PALETTE = 16
    DARK_MUTED_PALETTE = 32
    ALL_MODE_PALETTE = 64

PaletteColorModel = dataclass(<NODE:12>)

class PaletteSwatch:
    '''
    单个候选颜色样本。
    '''
    
    def __init__(self = None, colorInt = None, population = None):
        self.red = colorInt >> 16 & 255
        self.green = colorInt >> 8 & 255
        self.blue = colorInt & 255
        self.population = population

    
    def getHsl(self = None):
        return rgb888ToHsl(self.red, self.green, self.blue)

    
    def getColorString(self = None):
        return f'''#{self.red:02x}{self.green:02x}{self.blue:02x}'''



class PaletteTarget:
    '''
    目标色规则（亮度/饱和度区间 + 权重）定义。
    '''
    TARGET_DARK_LUMA = 0.26
    MAX_DARK_LUMA = 0.45
    MIN_LIGHT_LUMA = 0.55
    TARGET_LIGHT_LUMA = 0.74
    MIN_NORMAL_LUMA = 0.3
    TARGET_NORMAL_LUMA = 0.5
    MAX_NORMAL_LUMA = 0.7
    TARGET_MUTED_SATURATION = 0.3
    MAX_MUTED_SATURATION = 0.4
    TARGET_VIBRANT_SATURATION = 1
    MIN_VIBRANT_SATURATION = 0.35
    WEIGHT_SATURATION = 0.24
    WEIGHT_LUMA = 0.52
    WEIGHT_POPULATION = 0.24
    
    def __init__(self = None, mode = None):
        self.mode = mode
        self.saturationTargets = [
            0,
            0.5,
            1]
        self.lightnessTargets = [
            0,
            0.5,
            1]
        self.weights = [
            self.WEIGHT_SATURATION,
            self.WEIGHT_LUMA,
            self.WEIGHT_POPULATION]
        self.configureLumaAndSaturationWithMode(mode)

    
    def configureLumaAndSaturationWithMode(self = None, mode = None):
        if mode == PaletteTargetMode.LIGHT_VIBRANT_PALETTE:
            self.setDefaultLightLuma()
            self.setDefaultVibrantSaturation()
        elif mode == PaletteTargetMode.VIBRANT_PALETTE:
            self.setDefaultNormalLuma()
            self.setDefaultVibrantSaturation()
        elif mode == PaletteTargetMode.DARK_VIBRANT_PALETTE:
            self.setDefaultDarkLuma()
            self.setDefaultVibrantSaturation()
        elif mode == PaletteTargetMode.LIGHT_MUTED_PALETTE:
            self.setDefaultLightLuma()
            self.setDefaultMutedSaturation()
        elif mode == PaletteTargetMode.MUTED_PALETTE:
            self.setDefaultNormalLuma()
            self.setDefaultMutedSaturation()
        elif mode == PaletteTargetMode.DARK_MUTED_PALETTE:
            self.setDefaultDarkLuma()
            self.setDefaultMutedSaturation()

    
    def setDefaultLightLuma(self):
        self.lightnessTargets[0] = self.MIN_LIGHT_LUMA
        self.lightnessTargets[1] = self.TARGET_LIGHT_LUMA

    
    def setDefaultNormalLuma(self):
        self.lightnessTargets[0] = self.MIN_NORMAL_LUMA
        self.lightnessTargets[1] = self.TARGET_NORMAL_LUMA
        self.lightnessTargets[2] = self.MAX_NORMAL_LUMA

    
    def setDefaultDarkLuma(self):
        self.lightnessTargets[1] = self.TARGET_DARK_LUMA
        self.lightnessTargets[2] = self.MAX_DARK_LUMA

    
    def setDefaultMutedSaturation(self):
        self.saturationTargets[1] = self.TARGET_MUTED_SATURATION
        self.saturationTargets[2] = self.MAX_MUTED_SATURATION

    
    def setDefaultVibrantSaturation(self):
        self.saturationTargets[0] = self.MIN_VIBRANT_SATURATION
        self.saturationTargets[1] = self.TARGET_VIBRANT_SATURATION

    
    def normalizeWeights(self):
        positiveWeights = (lambda .0: [ w for w in .0 if w > 0 ])(self.weights)
        weightSum = sum(positiveWeights)
        if weightSum == 0:
            return None
        self.weights = (lambda .0 = None: for w in .0:
passcontinuew / weightSum[w])(self.weights)

    
    def getTargetKey(self = None):
        return self.getTargetModeKey(self.mode)

    
    def getTargetModeKey(mode = None):
        mapping = {
            PaletteTargetMode.DARK_MUTED_PALETTE: 'dark_muted',
            PaletteTargetMode.MUTED_PALETTE: 'muted',
            PaletteTargetMode.LIGHT_MUTED_PALETTE: 'light_muted',
            PaletteTargetMode.DARK_VIBRANT_PALETTE: 'dark_vibrant',
            PaletteTargetMode.VIBRANT_PALETTE: 'vibrant',
            PaletteTargetMode.LIGHT_VIBRANT_PALETTE: 'light_vibrant' }
        return mapping.get(mode, '')

    getTargetModeKey = None(getTargetModeKey)
    
    def getMinSaturation(self = None):
        return self.saturationTargets[0]

    
    def getTargetSaturation(self = None):
        return self.saturationTargets[1]

    
    def getMaxSaturation(self = None):
        return self.saturationTargets[2]

    
    def getMinLuma(self = None):
        return self.lightnessTargets[0]

    
    def getTargetLuma(self = None):
        return self.lightnessTargets[1]

    
    def getMaxLuma(self = None):
        return self.lightnessTargets[2]

    
    def getSaturationWeight(self = None):
        return self.weights[0]

    
    def getLumaWeight(self = None):
        return self.weights[1]

    
    def getPopulationWeight(self = None):
        return self.weights[2]



class PFilter:
    '''
    iOS 同款过滤器：过滤黑/白/接近红线颜色。
    '''
    BLACK_MAX_LIGHTNESS = 0.05
    WHITE_MIN_LIGHTNESS = 0.95
    
    def isAllowed(self = None, hsl = None):
        if not self.isBlack(hsl) and not self.isWhite(hsl):
            pass
        return not self.isNearRedILine(hsl)

    
    def isBlack(self = None, hsl = None):
        return hsl[2] <= self.BLACK_MAX_LIGHTNESS

    
    def isWhite(self = None, hsl = None):
        return hsl[2] >= self.WHITE_MIN_LIGHTNESS

    
    def isNearRedILine(self = None, hsl = None):
        if hsl[0] <= hsl[0]:
            pass
        elif hsl[0] <= 37:
            pass
        return hsl[1] <= 0.82



class VBox:
    '''
    Median-cut 算法中的颜色盒子。
    '''
    COMPONENT_RED = 0
    COMPONENT_GREEN = 1
    COMPONENT_BLUE = 2
    
    def __init__(self, lowerIndex = None, upperIndex = None, distinctColors = None, histArr = {
        'lowerIndex': 'int',
        'upperIndex': 'int',
        'distinctColors': 'List[int]',
        'histArr': 'List[int]' }):
        self.lowerIndex = lowerIndex
        self.upperIndex = upperIndex
        self.distinctColors = distinctColors
        self.histArr = histArr
        self.population = 0
        self.minRed = 0
        self.maxRed = 0
        self.minGreen = 0
        self.maxGreen = 0
        self.minBlue = 0
        self.maxBlue = 0
        self.fitBox()

    
    def getVolume(self = None):
        return ((self.maxRed - self.minRed) + 1) * ((self.maxGreen - self.minGreen) + 1) * ((self.maxBlue - self.minBlue) + 1)

    
    def canSplit(self = None):
        return self.upperIndex - self.lowerIndex > 0

    
    def splitBox(self = None):
        if not self.canSplit():
            return None
        splitPoint = None.findSplitPoint()
        newBox = VBox(splitPoint + 1, self.upperIndex, self.distinctColors, self.histArr)
        self.upperIndex = splitPoint
        self.fitBox()
        return newBox

    
    def getAverageColor(self = None):
        redSum = 0
        greenSum = 0
        blueSum = 0
        totalPopulation = 0
        for idx in range(self.lowerIndex, self.upperIndex + 1):
            color = self.distinctColors[idx]
            colorPopulation = self.histArr[color]
            totalPopulation += colorPopulation
            redSum += colorPopulation * quantizedRed(color)
            greenSum += colorPopulation * quantizedGreen(color)
            blueSum += colorPopulation * quantizedBlue(color)
        if totalPopulation <= 0:
            return None
        redMean = None(redSum // totalPopulation, QUANTIZE_WORD_WIDTH, 8)
        greenMean = modifyWordWidthWithValue(greenSum // totalPopulation, QUANTIZE_WORD_WIDTH, 8)
        blueMean = modifyWordWidthWithValue(blueSum // totalPopulation, QUANTIZE_WORD_WIDTH, 8)
        rgb888Color = redMean << 16 | greenMean << 8 | blueMean
        return PaletteSwatch(rgb888Color, totalPopulation)

    
    def fitBox(self):
        minRed = 32768
        minGreen = 32768
        minBlue = 32768
        maxRed = 0
        maxGreen = 0
        maxBlue = 0
        count = 0
        for idx in range(self.lowerIndex, self.upperIndex + 1):
            color = self.distinctColors[idx]
            count += self.histArr[color]
            red = quantizedRed(color)
            green = quantizedGreen(color)
            blue = quantizedBlue(color)
            maxRed = max(maxRed, red)
            minRed = min(minRed, red)
            maxGreen = max(maxGreen, green)
            minGreen = min(minGreen, green)
            maxBlue = max(maxBlue, blue)
            minBlue = min(minBlue, blue)
        self.population = count
        self.minRed = minRed
        self.maxRed = maxRed
        self.minGreen = minGreen
        self.maxGreen = maxGreen
        self.minBlue = minBlue
        self.maxBlue = maxBlue

    
    def findSplitPoint(self = None):
        longestDimension = self.getLongestColorDimension()
        self.modifySignificantOctet(longestDimension, self.lowerIndex, self.upperIndex)
        self.sortColorArray()
        self.modifySignificantOctet(longestDimension, self.lowerIndex, self.upperIndex)
        midPoint = self.population // 2
        count = 0
        for idx in range(self.lowerIndex, self.upperIndex + 1):
            color = self.distinctColors[idx]
            count += self.histArr[color]
            if count >= midPoint:
                return idx
            return self.lowerIndex

    
    def getLongestColorDimension(self = None):
        redLength = self.maxRed - self.minRed
        greenLength = self.maxGreen - self.minGreen
        blueLength = self.maxBlue - self.minBlue
        if redLength >= greenLength and redLength >= blueLength:
            return self.COMPONENT_RED
        if None >= redLength and greenLength >= blueLength:
            return self.COMPONENT_GREEN
        return None.COMPONENT_BLUE

    
    def modifySignificantOctet(self = None, dimension = None, lower = None, upper = {
        'dimension': 'int',
        'lower': 'int',
        'upper': 'int' }):
        if dimension == self.COMPONENT_RED:
            return None
        for idx in None(lower, upper + 1):
            color = self.distinctColors[idx]
            if dimension == self.COMPONENT_GREEN:
                newColor = quantizedGreen(color) << QUANTIZE_WORD_WIDTH + QUANTIZE_WORD_WIDTH | quantizedRed(color) << QUANTIZE_WORD_WIDTH | quantizedBlue(color)
            else:
                newColor = quantizedBlue(color) << QUANTIZE_WORD_WIDTH + QUANTIZE_WORD_WIDTH | quantizedGreen(color) << QUANTIZE_WORD_WIDTH | quantizedRed(color)
            self.distinctColors[idx] = newColor

    
    def sortColorArray(self):
        sortedRange = sorted(self.distinctColors[self.lowerIndex:self.upperIndex + 1])
        self.distinctColors[self.lowerIndex:self.upperIndex + 1] = sortedRange



class PriorityBoxArray:
    '''
    优先队列（按 VBox 体积降序）。
    '''
    
    def __init__(self):
        self.vboxArray = []

    
    def addVBox(self = None, box = None):
        if box is None:
            return None
        if not None.vboxArray:
            self.vboxArray.append(box)
            return None
        for idx, nowBox in None(self.vboxArray):
            if box.getVolume() > nowBox.getVolume():
                self.vboxArray.insert(idx, box)
                if len(self.vboxArray) > MAX_COLOR_NUM:
                    self.vboxArray.pop(MAX_COLOR_NUM)
            return None
        if len(self.vboxArray) < MAX_COLOR_NUM:
            self.vboxArray.append(box)

    
    def poll(self = None):
        if not self.vboxArray:
            return None
        return None.vboxArray.pop(0)

    
    def count(self = None):
        return len(self.vboxArray)

    
    def getVBoxArray(self = None):
        return self.vboxArray



class PaletteAnalyzer:
    '''
    iOS Palette 算法主分析器（同步版本）。
    '''
    
    def __init__(self = None, image = None):
        self.image = image
        self.histArr = [
            0] * HIST_ARR_SIZE
        self.distinctColors = []
        self.swatchArray = []
        self.targetArray = []
        self.maxPopulation = 0
        self.pixelCount = 0
        self.isNeedColorDic = False
        self.filters = [
            PFilter()]

    
    def startToAnalyzeForTargetMode(self = None, mode = None):
        '''
        按指定模式提取主题色。

        Args:
            mode: 目标色模式位标记。

        Returns:
            (recommendColor, allModeColorDic, error)
        '''
        self.initTargetsWithMode(mode)
        if self.image is None:
            return (None, None, ValueError('The image is null.'))
        None.startToAnalyzeImage()
        return self.getSwatchForTarget()

    
    def startToAnalyzeImage(self):
        self.clearHistArray()
        rawPixels = self.rawPixelDataFromImage(self.image)
        if not rawPixels:
            return None
        for red, green, blue, alpha in None:
            if alpha < 255:
                red = red * alpha // 255
                green = green * alpha // 255
                blue = blue * alpha // 255
            red5 = modifyWordWidthWithValue(red, 8, QUANTIZE_WORD_WIDTH)
            green5 = modifyWordWidthWithValue(green, 8, QUANTIZE_WORD_WIDTH)
            blue5 = modifyWordWidthWithValue(blue, 8, QUANTIZE_WORD_WIDTH)
            quantizedColor = red5 << QUANTIZE_WORD_WIDTH + QUANTIZE_WORD_WIDTH | green5 << QUANTIZE_WORD_WIDTH | blue5
            self.histArr[quantizedColor] += 1
        self.distinctColors = []
        for color in range(HIST_ARR_SIZE):
            if self.histArr[color] > 0 and self.shouldIgnoreColor(color):
                self.histArr[color] = 0
            if self.histArr[color] > 0:
                self.distinctColors.append(color)
                continue
                distinctColorCount = len(self.distinctColors)
                if distinctColorCount <= MAX_COLOR_NUM:
                    swatchs = []
                    for color in self.distinctColors:
                        population = self.histArr[color]
                        red = modifyWordWidthWithValue(quantizedRed(color), QUANTIZE_WORD_WIDTH, 8)
                        green = modifyWordWidthWithValue(quantizedGreen(color), QUANTIZE_WORD_WIDTH, 8)
                        blue = modifyWordWidthWithValue(quantizedBlue(color), QUANTIZE_WORD_WIDTH, 8)
                        rgb888Color = red << 16 | green << 8 | blue
                        swatchs.append(PaletteSwatch(rgb888Color, population))
                    self.swatchArray = swatchs
                else:
                    priorityArray = PriorityBoxArray()
                    colorVBox = VBox(0, distinctColorCount - 1, self.distinctColors, self.histArr)
                    priorityArray.addVBox(colorVBox)
                    self.splitBoxes(priorityArray)
                    self.swatchArray = self.generateAverageColors(priorityArray)
        self.findMaxPopulation()

    
    def clearHistArray(self):
        self.histArr = [
            0] * HIST_ARR_SIZE

    
    def rawPixelDataFromImage(self = None, image = None):
        scaledImage = self.scaleDownImage(image)
        rgbaImage = scaledImage.convert('RGBA')
        (width, height) = rgbaImage.size
        self.pixelCount = width * height
        return list(rgbaImage.getdata())

    
    def scaleDownImage(self = None, image = None):
        (width, height) = image.size
        if width <= 0 or height <= 0:
            return image
        scaleX = None / float(width)
        scaleY = TARGET_IMAGE_SIZE / float(height)
        scale = min(scaleX, scaleY)
        newWidth = max(1, int(round(width * scale)))
        newHeight = max(1, int(round(height * scale)))
        if (newWidth, newHeight) == (width, height):
            return image
        resampleMode = Image.Resampling.BILINEAR if None(Image, 'Resampling') else Image.BILINEAR
        return image.resize((newWidth, newHeight), resampleMode)

    
    def splitBoxes(self = None, queue = None):
        if queue.count() < MAX_COLOR_NUM:
            vbox = queue.poll()
            if vbox is not None and vbox.canSplit():
                queue.addVBox(vbox.splitBox())
                queue.addVBox(vbox)
                continue
            return None

    
    def generateAverageColors(self = None, queue = None):

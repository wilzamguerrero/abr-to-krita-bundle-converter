#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse

from procreate.procreate_brush_parser import ProcreateBrushParser, ProcreateBrushSetParser
from kpp.kpp_brush_parser import KPP_Brush_Parser
from kpp.krita_resource_bundle_creator import KritaResourceBundleCreator
from kpp.paintop_preset import BlendingMode, TextureBlendingModePixelEngine, MaskingBlendingMode, BrushTipType, SensorId

from math import degrees, sqrt
import re
import os.path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".brush file path",
                        type=str)
    parser.add_argument("--input", help="input .kpp file path",
                        type=str)
    parser.add_argument("output_path", help="result .kpp file path",
                        type=str)
    parser.add_argument("--bundle", help="result .bundle file path",
                        type=str)
    args = parser.parse_args()

    brushPath = args.file_path
    inputKPPpath = args.input
    outputKPPpath = args.output_path
    bundlePath = args.bundle

    bundleCreator = None
    if bundlePath:
        bundleCreator = KritaResourceBundleCreator(bundlePath)
        bundleCreator.setDesc(f"Generated from {os.path.basename(brushPath)} by procreate_to_kpp.py")
        bundleCreator.createZip()

    if brushPath.endswith('.brush'):
        converter = ProcreateBrushConverter(brushPath, inputKPPpath, outputKPPpath, bundleCreator=bundleCreator)
        converter.convertSettings()
        if converter.subParser.plist is not None:
            converter.convertSettings(isSub=True)
        converter.saveKPP()
    elif brushPath.endswith('.brushset'):
        names = ProcreateBrushSetParser().findBrushPaths(brushPath)
        for name in names:
            print(f"## {name}")
            converter = ProcreateBrushConverter(brushPath, inputKPPpath, os.path.join(outputKPPpath,f"{name}.kpp"), name=name, bundleCreator=bundleCreator)
            converter.convertSettings()
            if converter.subParser.plist is not None:
                converter.convertSettings(isSub=True)
            converter.saveKPP()
            print("######")

    if bundlePath:
        bundleCreator.finishZip()

class ProcreateBrushConverter:
    def __init__(self, brushPath, inputKPPpath, outputKPPpath, name="", bundleCreator=None):
        self.parser = ProcreateBrushParser(brushPath, name)
        self.subParser = ProcreateBrushParser(brushPath, name+"/Sub01")
        with open(outputKPPpath, 'wb') as f:
            f.write(self.parser.loadResource("QuickLook/Thumbnail.png", True))
        self.writer = KPP_Brush_Parser(inputPresetPath=inputKPPpath, outputPresetPath=outputKPPpath, reuseImage=False)

        self.bundleCreator = bundleCreator

    def saveKPP(self):
        self.writer.saveKPP(hasImage=True)

        if self.bundleCreator:
            self.bundleCreator.addResourceFromPath(self.writer.outputPresetPath, "paintoppresets")
    
    def loadSetting(self, key):
        return self.parser.loadSetting(key)

    def loadSubSetting(self, key):
        if self.subParser.plist is not None:
            return self.subParser.loadSetting(key)

    def saveSetting(self, key, value):
        print(f"Converting to {key}")
        self.writer.setPixelEngineSetting(key, value)
    
    def saveSettingIfNonZero(self, key, value):
        if value != 0:
            self.saveSetting(key, value)

    def convertCurve(self, curve, strength=0):
        curveStr = ""
        for point in curve:
            # {0.0, 1.0}
            match = re.match(r"\{(\d+\.?\d*), (\d+.?\d*)\}", point)
            if match:
                x,y = float(match.group(1)), float(match.group(2))
                if strength != 0.0:
                    y *= strength
                curveStr += f"{x},{y};"
            else:
                print(f"Error, couldn't parse curve {curve}")

        return curveStr
    
    # Curves where .5 = neutral
    def convertCurveToCenterZero(self, curve, strength=0):
        curveStr = ""
        for point in curve:
            # {0.0, 1.0}
            match = re.match(r"\{(\d+\.?\d*), (\d+.?\d*)\}", point)
            if match:
                x,y = float(match.group(1)), float(match.group(2))
                if strength != 0.0:
                    y *= strength
                y = y/2 + 0.5
                curveStr += f"{x},{y};"
            else:
                print(f"Error, couldn't parse curve {curve}")

        return curveStr
    
    def valueToCurveWithCenterZero(self, value):
        curve = f"0,{.5-value/2};1,{.5+value/2};"
        return curve

    # xtilt, ytilt, ascension, declination? I cannot test this
    def convertAngleToCurve(self, angle, strength):
        # ???
        # -60 to 0 as 0 to 1
        val = degrees(angle) / 60
        curveStr = f"0,0;{val},{strength};"
        return curveStr
    
    # I cannot test this
    def convertRollToCurve(self, rollParams, strength):
        # ???
        # radians -> percent
        val1 = rollParams['activationFalloff']
        val1 = degrees(val1) / 360
        val2 = rollParams['activationOrigin']
        val2 = degrees(val2) / 360
        curveStr = f"{val1},0;{val2},{strength};"
        return curveStr

    blendModes = {
        1: BlendingMode.Multiply,
        19: BlendingMode.Darken,
        10: BlendingMode.ColorBurn,
        8: BlendingMode.LinearBurn,
        25: BlendingMode.DarkerColor, # extendedBlend only?
        0: BlendingMode.Normal,
        4: BlendingMode.Lighten,
        2: BlendingMode.Screen,
        9: BlendingMode.ColorDodge,
        3: BlendingMode.Add, 
        24: BlendingMode.LighterColor,
        11: BlendingMode.Overlay,
        17: BlendingMode.SoftLightPhotoshop, # which one?
        12: BlendingMode.HardLight,
        21: BlendingMode.VividLight,
        23: BlendingMode.PinLight, # extendedBlend only?
        20: BlendingMode.HardMix, # which one?
        6: BlendingMode.Difference,
        5: BlendingMode.Exclusion,
        7: BlendingMode.Subtract,
        26: BlendingMode.Divide,
        15: BlendingMode.HueHSY, # which one?
        16: BlendingMode.SaturationHSY, # which one?
        14: BlendingMode.ColorHSY, # which one?
        13: BlendingMode.LuminosityHSY, # which one?
        18: BlendingMode.Behind,
        # note: there doesn't appear to be a '22'
    }
    # the Krita values seem to differ between the Pixel engine and
    # other engines (whose numbering skips two texture modes they don't support, lightness map(2)/gradient map(3)
    # these values are for the Pixel engine.
    blendModesTexture = {
        1: TextureBlendingModePixelEngine.Multiply,
        19: TextureBlendingModePixelEngine.Darken,
        10: TextureBlendingModePixelEngine.ColorBurn,
        8: TextureBlendingModePixelEngine.LinearBurn,
        #4: # "lighten" -- no equivalent (oddly), maybe invert and use darken?
        9: TextureBlendingModePixelEngine.ColorDodge,
        11: TextureBlendingModePixelEngine.Overlay,
        20: TextureBlendingModePixelEngine.HardMixPhotoshop, # or hard mix softer PS?
        #6: # "diff" (difference) -- no equivalent
        7: TextureBlendingModePixelEngine.Subtract,
        #26: # "divide" -- no equivalent (oddly), maybe invert and use multiply?
        27: TextureBlendingModePixelEngine.Height, # (grain/texture only) -- or PS version?
        28: TextureBlendingModePixelEngine.LinearHeight, # (grain/texture only) -- or PS version?
    }
    # Krita supports only some blending modes for masked brushes
    blendModesMasking = {
        1: MaskingBlendingMode.Multiply,
        19: MaskingBlendingMode.Darken,
        10: MaskingBlendingMode.ColorBurn,
        8: MaskingBlendingMode.LinearBurn,
        9: MaskingBlendingMode.ColorDodge,
        11: MaskingBlendingMode.Overlay,
        20: MaskingBlendingMode.HardMixPhotoshop, # which one?
    }
    def convertBlendMode(self, value):
        if not value in self.blendModes:
            print(f"Warning: Unknown blend mode {value}")
            return BlendingMode.Normal
        return self.blendModes[value]
    def convertTextureBlendMode(self, value):
        if value == 4:
            print("Warning: Texture blend mode 4 (lighten) not supported")
            return TextureBlendingModePixelEngine.Multiply
        elif value == 6:
            print("Warning: Texture blend mode 6 (difference) not supported")
            return TextureBlendingModePixelEngine.Multiply
        elif value == 26:
            print("Warning: Texture blend mode 26 (divide) not supported")
            return TextureBlendingModePixelEngine.Multiply
        if not value in self.blendModesTexture:
            print(f"Warning: Unknown texture blend mode {value}")
            return TextureBlendingModePixelEngine.Multiply
        return self.blendModesTexture[value]
    def convertMaskingBlendMode(self, value):
        if not value in self.blendModesMasking:
            print(f"Warning: Unknown masking blend mode {value}")
            return MaskingBlendingMode.Multiply
        return self.blendModesMasking[value]

    def enableCurveOption(self, sensorId, enabled):
        self.saveSetting(f"Pressure{sensorId}", enabled)
        if enabled:
            self.saveSetting(f"{sensorId}UseSameCurve", False)

    def enableMaskingCurveOption(self, sensorId, enabled):
        self.saveSetting(f"MaskingBrush/Preset/Pressure{sensorId}", enabled)
        if enabled:
            self.saveSetting(f"MaskingBrush/Preset/{sensorId}UseSameCurve", False)


    def ignoredKey(self,key):
        pass
        #print(f"Ignored: {key} : {self.loadSetting(key)}")
    def unsupportedKey(self, key):
        pass
        #print(f"Unsupported key: {key} : {self.loadSetting(key)}")
    def unsupportedSubKey(self, key):
        pass
        #print(f"Unsupported sub key: {key} : {self.loadSetting(key)}")
    def unknownKey(self, key):
        print(f"Unknown key: {key} : {self.loadSetting(key)}")

    def convertSettings(self, isSub=False):
        isMain = not isSub # readability things...
        plist = self.parser.plist if isMain else self.subParser.plist
        if isSub:
            self.saveSetting('MaskingBrush/Enabled', True)
        for key in plist["$objects"][1].keys():
            value = self.loadSetting(key) if isMain else self.loadSubSetting(key)
            match key:
    
                # Stroke properties
                case 'plotSpacingVersion':
                    self.ignoredKey(key)
                case 'plotSpacing':
                    perc = sqrt(value * 100) / 10 # why ???
                    if isMain:
                        self.writer.setBrushDefinitionSetting('spacing', perc)
                    elif isSub:
                        self.writer.setMaskedBrushDefinitionSetting('spacing', perc)

                case 'plotJitter':
                    #self.unsupportedKey(key)
                    perc = sqrt(value) / 2 # roughly this, no idea actual equation ?????
                    # (100% = 3, 200% = 13.78)
                    if isMain:
                        if value != 0:
                            self.enableCurveOption('Scatter', True)
                        self.saveSetting('ScatterValue', perc)
                    elif isSub:
                        if value != 0:
                            self.enableMaskingCurveOption('Scatter', True)
                        self.saveSetting('MaskingBrush/Preset/ScatterValue', perc)
                case 'plotJitterTilt':
                    self.unsupportedKey(key)
                case 'plotJitterTiltAngle':
                    self.unsupportedKey(key)
                case 'plotJitterRoll':
                    self.unsupportedKey(key)
                case 'plotJitterRollParameters':
                    self.unsupportedKey(key)
                case 'dynamicsFalloff':
                    self.unsupportedKey(key)

                # Stabilization
                # - This isn't per-KPP
                case 'plotSmoothing':
                    self.ignoredKey(key)
                case 'dynamicsPressureSmoothing':
                    self.ignoredKey(key)
                case 'plotMovingAverageStabilization':
                    self.ignoredKey(key)
                case 'plotFFTSmoothingAmount':
                    self.ignoredKey(key)
                case 'plotFFTSmoothingBias':
                    self.ignoredKey(key)

                # Taper
                # - this adds taper to the ends of pencil strokes somehow
                case 'taperVersion':
                    self.ignoredKey(key)
                case 'pencilTaperStartLength':
                    self.unsupportedKey(key)
                case 'pencilTaperEndLength':
                    self.unsupportedKey(key)
                case 'pencilTaperSizeLinked':
                    self.unsupportedKey(key)
                case 'pencilTaperSize':
                    self.unsupportedKey(key)
                case 'pencilTaperOpacity':
                    self.unsupportedKey(key)
                case 'taperPressure':
                    self.unsupportedKey(key)
                case 'pencilTaperShape':
                    self.unsupportedKey(key)
                case 'pencilTipAnimation':
                    self.unsupportedKey(key)
                # touch taper
                # - this adds taper to the ends of touch strokes somehow
                # - closest thing is to do size over distance.. for the beginning of the stroke
                # - how does it do the end?
                case 'taperStartLength':
                    self.unsupportedKey(key)
                case 'taperEndLength':
                    self.unsupportedKey(key)
                case 'taperSizeLinked':
                    self.unsupportedKey(key)
                case 'taperSize':
                    self.unsupportedKey(key)
                case 'taperOpacity':
                    self.unsupportedKey(key)
                case 'taperShape':
                    self.unsupportedKey(key)
                # case [classic taper]
                #    self.unsupportedKey(key)


                # Shape
                case 'bundledShapePath':
                    if isMain:
                        # seems to load embedded Shape.png unless otherwise specified
                        if value == "$null":
                            # give a more useful name, "brushname-Shape.png"
                            value = self.loadSetting('name').replace(" ", "_") + "-Shape.png"
                            resData = self.parser.loadResource("Shape.png")
                            md5sum = self.writer.embedResource(resData, value, "brushes")
                            self.writer.setBrushDefinitionSetting('md5sum', md5sum)

                            # todo: don't embed if using bundle?
                            if self.bundleCreator:
                                self.bundleCreator.addResourceFromData(resData, "brushes", value, md5sum)
                        else:
                            print(f"Warning: Brush requires external brushtip resource {value}")
                        self.writer.setBrushDefinitionSetting('type', BrushTipType.Predefined)
                        self.saveSetting('requiredBrushFile', value)
                        self.writer.setBrushDefinitionSetting('filename', value)
                    elif isSub:
                        # seems to load embedded Shape.png unless otherwise specified
                        if value == "$null":
                            # give a more useful name, "brushname-Shape.png"
                            value = self.loadSetting('name').replace(" ", "_") + "-Shape.png"
                            resData = self.subParser.loadResource("Shape.png")
                            md5sum = self.writer.embedResource(resData, value, "brushes")
                            self.writer.setBrushDefinitionSetting('md5sum', md5sum)

                            # todo: don't embed if using bundle?
                            if self.bundleCreator:
                                self.bundleCreator.addResourceFromData(resData, "brushes", value, md5sum)
                        else:
                            print(f"Warning: Brush requires external brushtip resource {value}")
                        self.writer.setMaskedBrushDefinitionSetting('type', BrushTipType.Predefined)
                        #self.saveSetting('requiredBrushFile', value)
                        self.writer.setMaskedBrushDefinitionSetting('filename', value)
                case 'shapeAzimuth':
                    self.unsupportedKey(key)
                case 'shapeRoll':
                    self.unsupportedKey(key)
                case 'shapeRollMode':
                    self.unsupportedKey(key)
                case 'shapeRotation':
                    self.unsupportedKey(key)
                case 'shapeScatter':
                    self.unsupportedKey(key)
                    #self.saveSetting('ScatterValue')
                case 'shapeScatterRoll':
                    self.unsupportedKey(key)
                case 'shapeScatterRollParameters':
                    self.unsupportedKey(key)
                case 'shapeCount':
                    self.unsupportedKey(key)
                case 'shapeCountTilt':
                    self.unsupportedKey(key)
                case 'shapeCountTiltAngle':
                    self.unsupportedKey(key)
                case 'shapeCountRoll':
                    self.unsupportedKey(key)
                case 'shapeCountRollParameters':
                    self.unsupportedKey(key)
                case 'shapeCountJitter':
                    self.unsupportedKey(key)
                case 'shapeRandomise':
                    self.unsupportedKey(key)
                case 'shapeFlipXJitter':
                    self.unsupportedKey(key)
                case 'shapeFlipYJitter':
                    self.unsupportedKey(key)
                case 'shapeRoundness':
                    self.unsupportedKey(key)
                case 'dynamicsPressureShapeRoundness':
                    self.unsupportedKey(key)
                case 'dynamicsPressureShapeRoundnessCurve':
                    self.unsupportedKey(key)
                case 'dynamicsPressureShapeRoundnessMinimum':
                    self.unsupportedKey(key)
                case 'dynamicsTiltShapeRoundness':
                    self.unsupportedKey(key)
                case 'shapeRoundnessTiltAngle':
                    self.unsupportedKey(key)
                case 'dynamicsTiltShapeRoundnessMinimum':
                    self.unsupportedKey(key)
                case 'shapeFilter':
                    self.unsupportedKey(key)
                case 'shapeFilterMode':
                    self.unsupportedKey(key)

                # Grain
                case 'bundledGrainPath':
                    if isMain:
                        # seems to load embedded Grain.png unless otherwise specified
                        if value == "$null":
                            # give a more useful name, "brushname-Grain.png"
                            value = self.loadSetting('name').replace(" ", "_") + "-Grain.png"
                            resData = self.parser.loadResource("Grain.png")
                            md5sum = self.writer.embedResource(resData, value, "patterns")
                            self.saveSetting('Texture/Pattern/PatternMD5Sum', md5sum)

                            # todo: don't embed if using bundle?
                            if self.bundleCreator:
                                self.bundleCreator.addResourceFromData(resData, "patterns", value, md5sum)
                        else:
                            print(f"Warning: Brush requires external texture resource {value}")
                        self.saveSetting('Texture/Pattern/PatternFileName', value)
                        self.saveSetting('Texture/Pattern/Name', value)
                        self.saveSetting('Texture/Pattern/Enabled', True)
                    elif isSub:
                        self.unsupportedSubKey(key)

                # case [type] ?
                case 'textureMovement':
                    self.unsupportedKey(key)
                case 'textureScale':
                    self.saveSetting('Texture/Pattern/Scale', value)
                case 'textureZoom':
                    self.unsupportedKey(key)
                case 'textureRotation':
                    self.unsupportedKey(key)
                case 'grainDepth':
                    self.unsupportedKey(key)
                case 'grainDepthMinimum':
                    self.unsupportedKey(key)
                case 'grainDepthJitter':
                    self.unsupportedKey(key)
                case 'textureOffsetJitter':
                    self.unsupportedKey(key)
                case 'grainBlendMode':
                    self.saveSetting('Texture/Pattern/TexturingMode', self.convertTextureBlendMode(value))
                case 'textureBrightness':
                    self.saveSetting('Texture/Pattern/Brightness', value)
                case 'textureContrast':
                    if isMain:
                        # convert from -1.0 to 1.0 to 0.0 to 2.0
                        value += 1
                        self.saveSetting('Texture/Pattern/Contrast', value)
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'textureFilter':
                    self.unsupportedKey(key)
                case 'texturizedGrainFollowsCamera':
                    self.ignoredKey(key)
                # 
                case 'grainOrientation':
                    self.unsupportedKey(key)

                # Rendering
                case 'renderingRecursiveMixing':
                    self.unsupportedKey(key)
                case 'renderingMaxTransfer':
                    self.unsupportedKey(key)
                case 'renderingModulatedTransfer':
                    self.unsupportedKey(key)
                case 'dynamicsGlazedFlow':
                    self.unsupportedKey(key)
                case 'wetEdgesAmount':
                    self.unsupportedKey(key)
                case 'burntEdgesAmount':
                    self.unsupportedKey(key)
                case 'burntEdgesBlendMode':
                    self.unsupportedKey(key)
                case 'blendMode':
                    #self.saveSetting('CompositeOp', self.convertBlendMode(value))
                    self.unsupportedKey(key)
                case 'extendedBlend':
                    if isMain:
                        # This appears to supercede 'blendMode'?
                        self.saveSetting('CompositeOp', self.convertBlendMode(value))
                    elif isSub:
                        self.unsupportedSubKey(key)

                case 'blendGammaCorrect':
                    self.unsupportedKey(key)

                # Wet Mix
                # case [dilution]
                case 'dynamicsLoad':
                    self.unsupportedKey(key)
                case 'attackTilt':
                    self.unsupportedKey(key)
                case 'attackTiltAngle':
                    self.unsupportedKey(key)
                case 'attackRoll':
                    self.unsupportedKey(key)
                case 'attackRollParameters':
                    self.unsupportedKey(key)
                # case [pull]
                # case [grade]
                case 'dynamicsBlur':
                    self.unsupportedKey(key)
                case 'dynamicsBlurJitter':
                    self.unsupportedKey(key)
                case 'dynamicsWetnessJitter':
                    self.unsupportedKey(key)
                    
                # Color dynamics
                # Stamp color jitter
                case 'dynamicsJitterHue':
                    if value == 0:
                        continue
                    self.enableCurveOption('h', True)
                    # convert from "20%" to "30%-70%" or "-20:+20"
                    curve = self.valueToCurveWithCenterZero(value)
                    self.writer.setSensor('hSensor', SensorId.FuzzyDab, curve)
                case 'hueJitterTilt':
                    self.unsupportedKey(key)
                case 'hueJitterTiltAngle':
                    self.unsupportedKey(key)
                case 'dynamicsJitterSaturation':
                    if value == 0:
                        continue
                    self.enableCurveOption('s', True)
                    curve = self.valueToCurveWithCenterZero(value)
                    self.writer.setSensor('sSensor', SensorId.FuzzyDab, curve)
                case 'saturationJitterTilt':
                    self.unsupportedKey(key)
                case 'saturationJitterTiltAngle':
                    self.unsupportedKey(key)
                case 'dynamicsJitterLightness':
                    if value == 0:
                        continue
                    self.enableCurveOption('v', True)
                    curve = f"0,{.5-self.loadSetting('dynamicsJitterDarkness')/2};1,{.5+value/2};"
                    self.writer.setSensor('vSensor', SensorId.FuzzyDab, curve)
                case 'lightnessJitterTilt':
                    self.unsupportedKey(key)
                case 'lightnessJitterTiltAngle':
                    self.unsupportedKey(key)
                case 'dynamicsJitterDarkness':
                    if value == 0:
                        continue
                    self.enableCurveOption('v', True)
                    curve = f"0,{.5-value/2};1,{.5+self.loadSetting('dynamicsJitterLightness')/2};"
                    self.writer.setSensor('vSensor', SensorId.FuzzyDab, curve)
                case 'darknessJitterTilt':
                    self.unsupportedKey(key)
                case 'darknessJitterTiltAngle':
                    self.unsupportedKey(key)
                case 'jitterSecondary':
                    self.unsupportedKey(key)
                case 'secondaryColorJitterTilt':
                    self.unsupportedKey(key)
                case 'secondaryColorJitterTiltAngle':
                    self.unsupportedKey(key)
                # Stroke color jitter
                case 'dynamicsJitterStrokeHue':
                    if value == 0:
                        continue
                    self.enableCurveOption('h', True)
                    curve = self.valueToCurveWithCenterZero(value)
                    self.writer.setSensor('hSensor', SensorId.FuzzyStroke, curve)
                case 'dynamicsJitterStrokeSaturation':
                    if value == 0:
                        continue
                    self.enableCurveOption('s', True)
                    curve = self.valueToCurveWithCenterZero(value)
                    self.writer.setSensor('sSensor', SensorId.FuzzyStroke, curve)
                case 'dynamicsJitterStrokeLightness':
                    if value == 0:
                        continue
                    self.enableCurveOption('c', True)
                    curve = f"0,{.5-self.loadSetting('dynamicsJitterStrokeDarkness')/2};1,{.5+value/2};"
                    self.writer.setSensor('vSensor', SensorId.FuzzyStroke, curve)
                case 'dynamicsJitterStrokeDarkness':
                    if value == 0:
                        continue
                    self.enableCurveOption('v', True)
                    curve = f"0,{.5-value/2};1,{.5+self.loadSetting('dynamicsJitterStrokeLightness')/2};"
                    self.writer.setSensor('vSensor', SensorId.FuzzyStroke, curve)
                case 'jitterStrokeSecondary':
                    self.unsupportedKey(key)
                # Color pressure
                case 'dynamicsPressureHue':
                    pass
                case 'dynamicsPressureHueCurve':
                    strength = self.loadSetting('dynamicsPressureHue')
                    if strength == 0:
                        continue
                    if isMain:
                        curve = self.parser.getCurvePoints(key)
                        self.enableCurveOption('h', True)
                        self.writer.setSensor('hSensor', SensorId.Pressure, self.convertCurveToCenterZero(curve, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsPressureSaturation':
                    pass
                case 'dynamicsPressureSaturationCurve':
                    strength = self.loadSetting('dynamicsPressureSaturation')
                    if strength == 0:
                        continue
                    if isMain:
                        curve = self.parser.getCurvePoints(key)
                        self.enableCurveOption('s', True)
                        self.writer.setSensor('sSensor', SensorId.Pressure, self.convertCurveToCenterZero(curve, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsPressureBrightness':
                    pass
                case 'dynamicsPressureBrightnessCurve':
                    strength = self.loadSetting('dynamicsPressureBrightness')
                    if strength == 0:
                        continue
                    if isMain:
                        curve = self.parser.getCurvePoints(key)
                        self.enableCurveOption('v', True)
                        self.writer.setSensor('vSensor', SensorId.Pressure, self.convertCurveToCenterZero(curve, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsPressureSecondaryColor':
                    self.unsupportedKey(key)
                case 'dynamicsPressureSecondaryColorCurve':
                    self.unsupportedKey(key)
                # Color tilt
                case 'dynamicsTiltHue':
                    pass
                case 'hueTiltAngle':
                    strength = self.loadSetting('dynamicsTiltHue')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('h', True)
                        self.writer.setSensor('hSensor', SensorId.TiltElevation, self.convertAngleToCurve(value, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsTiltSaturation':
                    pass
                case 'saturationTiltAngle':
                    strength = self.loadSetting('dynamicsTiltSaturation')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('s', True)
                        self.writer.setSensor('sSensor', SensorId.TiltElevation, self.convertAngleToCurve(value, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsTiltBrightness':
                    pass
                case 'brightnessTiltAngle':
                    strength = self.loadSetting('dynamicsTiltBrightness')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('v', True)
                        self.writer.setSensor('vSensor', SensorId.TiltElevation, self.convertAngleToCurve(value, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsTiltSecondaryColor':
                    self.unsupportedKey(key)
                case 'secondaryColorTiltAngle':
                    self.unsupportedKey(key)
                # Color barrel roll
                case 'dynamicsRollHue':
                    pass
                case 'dynamicsRollHueParameters':
                    strength = self.loadSetting('dynamicsRollHue')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('h', True)
                        self.writer.setSensor('hSensor', SensorId.Rotation, self.convertRollToCurve(value, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsRollSaturation':
                    pass
                case 'dynamicsRollSaturationParameters':
                    strength = self.loadSetting('dynamicsRollSaturation')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('s', True)
                        self.writer.setSensor('sSensor', SensorId.Rotation, self.convertRollToCurve(value, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsRollBrightness':
                    pass
                case 'dynamicsRollBrightnessParameters':
                    strength = self.loadSetting('dynamicsRollBrightness')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('v', True)
                        self.writer.setSensor('vSensor', SensorId.Rotation, self.convertRollToCurve(value, strength))
                    elif isSub:
                        self.unsupportedSubKey(key)
                case 'dynamicsRollSecondaryColor':
                    self.unsupportedKey(key)
                case 'dynamicsRollSecondaryColorParameters':
                    self.unsupportedKey(key)           

                # Dynamics
                case 'dynamicsSpeedSize':
                    if value == 0: # 0 = do nothing
                        continue
                    # -100: slow=thin
                    # +100: fast=thin
                    # speed from -100 to 100 -> 0 to 1 ?
                    curve = ["{0, 0}", "{1, 1}"] if value < 0 else ["{0, 1}", "{1, 0}"]
                    if isMain:
                        self.enableCurveOption('Size', True)
                        self.writer.setSensor('SizeSensor', SensorId.Speed, self.convertCurve(curve, value))
                    elif isSub:
                        self.enableMaskingCurveOption('Size', True)
                        self.writer.setSensor('MaskingBrush/Preset/SizeSensor', SensorId.Speed, self.convertCurve(curve, value))
                case 'dynamicsSpeedOpacity':
                    if value == 0: # 0 = do nothing
                        continue
                    # -100: slow = low opacity
                    # +100: fast = low opacity
                    curve = ["{0, 0}", "{1, 1}"] if value < 0 else ["{0, 1}", "{1, 0}"]
                    if isMain:
                        self.enableCurveOption('Opacity', True)
                        self.writer.setSensor('OpacitySensor', SensorId.Speed, self.convertCurve(curve, value))
                    elif isSub:
                        self.enableMaskingCurveOption('Opacity', True)
                        self.writer.setSensor('MaskingBrush/Preset/OpacitySensor', SensorId.Speed, self.convertCurve(curve, value))
                case 'dynamicsJitterSize':
                    self.unsupportedKey(key)
                case 'dynamicsJitterOpacity':
                    self.unsupportedKey(key)

                # Apple Pencil
                # Pressure
                case 'dynamicsPressureSize':
                    pass
                case 'dynamicsPressureSizeCurve':
                    strength = self.loadSetting('dynamicsPressureSize')
                    if strength == 0:
                        continue
                    curve = self.parser.getCurvePoints(key)
                    if isMain:
                        self.enableCurveOption('Size', True)
                        self.writer.setSensor('SizeSensor', SensorId.Pressure, self.convertCurve(curve, strength))
                    elif isSub:
                        self.enableMaskingCurveOption('Size', True)
                        self.writer.setSensor('MaskingBrush/Preset/SizeSensor', SensorId.Pressure, self.convertCurve(curve, strength))
                case 'dynamicsPressureSizeSpeed':
                    self.unsupportedKey(key)
                case 'dynamicsPressureOpacity':
                    pass
                case 'dynamicsPressureOpacityCurve':
                    strength = self.loadSetting('dynamicsPressureOpacity')
                    if strength == 0:
                        continue
                    curve = self.parser.getCurvePoints(key)
                    if isMain:
                        self.enableCurveOption('Opacity', True)
                        self.writer.setSensor('OpacitySensor', SensorId.Pressure, self.convertCurve(curve, strength))
                    elif isSub:
                        self.enableMaskingCurveOption('Opacity', True)
                        self.writer.setSensor('MaskingBrush/Preset/OpacitySensor', SensorId.Pressure, self.convertCurve(curve, strength))
                case 'dynamicsPressureOpacitySpeed':
                    self.unsupportedKey(key)
                # case [flow]
                case 'dynamicsPressureBleed':
                    self.unsupportedKey(key)
                case 'dynamicsPressureBleedCurve':
                    self.unsupportedKey(key)
                case 'dynamicsPressureBleedSpeed':
                    self.unsupportedKey(key)
                # Tilt
                case 'dynamicsTiltAngle':
                    self.unsupportedKey(key)
                case 'dynamicsTiltOpacity':
                    pass
                case 'opacityTiltAngle':
                    strength = self.loadSetting('dynamicsTiltOpacity')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('Opacity', True)
                        self.writer.setSensor('OpacitySensor', SensorId.TiltElevation, self.convertAngleToCurve(value, strength))
                    elif isSub:
                        self.enableMaskingCurveOption('Opacity', True)
                        self.writer.setSensor('MaskingBrush/Preset/OpacitySensor', SensorId.TiltElevation, self.convertAngleToCurve(value, strength))
                case 'dynamicsTiltGradation':
                    self.unsupportedKey(key)
                case 'gradationTiltAngle':
                    self.unsupportedKey(key)
                case 'dynamicsTiltBleed':
                    self.unsupportedKey(key)
                case 'bleedTiltAngle':
                    self.unsupportedKey(key)
                case 'dynamicsTiltSize':
                    pass
                case 'sizeTiltAngle':
                    strength = self.loadSetting('dynamicsTiltSize')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('Size', True)
                        self.writer.setSensor('SizeSensor', SensorId.TiltElevation, self.convertAngleToCurve(value, strength))
                    elif isSub:
                        self.enableMaskingCurveOption('Size', True)
                        self.writer.setSensor('MaskingBrush/Preset/SizeSensor', SensorId.TiltElevation, self.convertAngleToCurve(value, strength))
                case 'dynamicsTiltCompression':
                    self.unsupportedKey(key)
                # Barrel roll
                case 'dynamicsRollSize':
                    pass
                case 'dynamicsRollSizeParameters':
                    strength = self.loadSetting('dynamicsRollSize')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('Size', True)
                        self.writer.setSensor('SizeSensor', SensorId.Rotation, self.convertRollToCurve(value, strength))
                    elif isSub:
                        self.enableMaskingCurveOption('Size', True)
                        self.writer.setSensor('MaskingBrush/Preset/SizeSensor', SensorId.Rotation, self.convertRollToCurve(value, strength))
                case 'dynamicsRollOpacity':
                    pass
                case 'dynamicsRollOpacityParameters':
                    strength = self.loadSetting('dynamicsRollOpacity')
                    if strength == 0:
                        continue
                    if isMain:
                        self.enableCurveOption('Opacity', True)
                        self.writer.setSensor('OpacitySensor', SensorId.Rotation, self.convertRollToCurve(value, strength))
                    elif isSub:
                        self.enableMaskingCurveOption('Opacity', True)
                        self.writer.setSensor('MaskingBrush/Preset/OpacitySensor', SensorId.Rotation, self.convertRollToCurve(value, strength))
                case 'dynamicsRollBleed':
                    self.unsupportedKey(key)
                case 'dynamicsRollBleedParameters':
                    self.unsupportedKey(key)
                # Hover
                case 'hoverOutline':
                    self.unsupportedKey(key)
                case 'hoverPressure':
                    self.unsupportedKey(key)
                case 'hoverFill':
                    self.unsupportedKey(key)


                # Properties
                case 'stamp':
                    self.unsupportedKey(key)
                case 'oriented':
                    self.unsupportedKey(key)
                case 'previewSize':
                    self.unsupportedKey(key)
                case 'smudgeSize':
                    self.unsupportedKey(key)
                # - these min/max are for the UI
                case 'maxSize':
                    self.ignoredKey(key)
                case 'minSize':
                    self.ignoredKey(key)
                case 'maxOpacity':
                    self.ignoredKey(key)
                case 'minOpacity':
                    self.ignoredKey(key)

                # Materials
                # - This is for 3D model rendering.
                # - Thus we don't care about it.
                case 'metallicAmount':
                    self.ignoredKey(key)
                case 'bundledMetallicPath':
                    self.ignoredKey(key)
                case 'metallicScale':
                    self.ignoredKey(key)
                case 'roughnessAmount':
                    self.ignoredKey(key)
                case 'bundledRoughnessPath':
                    self.ignoredKey(key)
                case 'roughnessScale':
                    self.ignoredKey(key)

                # About this brush
                case 'name':
                    self.writer.setName(value)
                #case [profile picture]
                #   self.unsupportedKey(key)
                case 'authorName':
                    self.unsupportedKey(key)
                case 'creationDate':
                    self.unsupportedKey(key)
                #case [signature]
                #   self.unsupportedKey(key)


                case '$class':
                    self.ignoredKey(key)
                case 'version':
                    self.ignoredKey(key)
                case 'importedFromABR':
                    self.ignoredKey(key)

                case 'color':
                    self.ignoredKey(key)

                case 'paintSize':
                    if isMain:
                        # the scale of the brushtip?
                        self.writer.setBrushDefinitionSetting('scale', value)
                        # put a 32px auto brushtip size in case we don't have the brushtip
                        value = 320 * value
                        self.writer.setBrushDefinitionSetting('diameter', value, BrushTipType.Auto)
                    elif isSub:
                        # the scale of the brushtip?
                        self.writer.setMaskedBrushDefinitionSetting('scale', value)
                        # put a 32px auto brushtip size in case we don't have the brushtip
                        value = 320 * value
                        self.writer.setMaskedBrushDefinitionSetting('diameter', value, BrushTipType.Auto)

                case 'dualBlendMode':
                    if isMain:
                        self.saveSetting('MaskingBrush/MaskingCompositeOp', self.convertMaskingBlendMode(value))
                    elif isSub:
                        # for the sub brush, probably this setting doesn't do anything?
                        self.ignoredKey(key)

                case 'savedPaintOpacities':
                    self.ignoredKey(key)
                case 'savedEraseOpacities':
                    self.ignoredKey(key)
                case 'savedSmudgeOpacities':
                    self.ignoredKey(key)
                case 'savedPaintSizes':
                    self.ignoredKey(key)
                case 'savedEraseSizes':
                    self.ignoredKey(key)
                case 'savedSmudgeSizes':
                    self.ignoredKey(key)

                case 'paintOpacity':
                    if isMain:
                        self.saveSetting('OpacityValue', value)
                    elif isSub:
                        self.saveSetting('MaskingBrush/Preset/OpacityValue', value)
                case 'eraseOpacity':
                    self.unsupportedKey(key)
                case 'smudgeOpacity':
                    self.ignoredKey(key)
                
                case 'eraseSize':
                    self.unsupportedKey(key)

                case 'paintPressure':
                    self.unsupportedKey(key)
                case 'maxPressureSizeClamped':
                    self.unsupportedKey(key)

                case 'shapeOrientation':
                    self.unsupportedKey(key)
                case 'shapeAngle':
                    self.unsupportedKey(key)
                
                case 'textureDepthTilt':
                    self.unsupportedKey(key)
                case 'textureOrientation':
                    self.unsupportedKey(key)
                case 'textureFilterMode':
                    self.unsupportedKey(key)
                case 'textureInverted':
                    self.unsupportedKey(key)
                case 'textureApplication':
                    self.unsupportedKey(key)
                case 'textureDepthTiltAngle':
                    self.unsupportedKey(key)

                case 'bundledHeightPath':
                    self.unsupportedKey(key)
                case 'heightAmount':
                    self.unsupportedKey(key)
                case 'heightScale':
                    self.unsupportedKey(key)

                case 'dynamicsPressureMix':
                    self.unsupportedKey(key)
                case 'dynamicsMix':
                    self.unsupportedKey(key)
                case 'dynamicsMixSoftening':
                    self.unsupportedKey(key)
                case 'dynamicsWetAccumulation':
                    self.unsupportedKey(key)
                case 'dynamicsSmudgeAccumulation':
                    self.unsupportedKey(key)

                case 'dynamicsPressureResponse':
                    self.unsupportedKey(key)
                case 'dynamicsPressureOpacityTransfer':
                    self.unsupportedKey(key)
                case 'dynamicsPressureTransferModulationCurve':
                    self.unsupportedKey(key)

                case 'shapeInverted':
                    self.unsupportedKey(key)
                case 'roughnessGrainInverted':
                    self.unsupportedKey(key)
                case 'metallicGrainInverted':
                    self.unsupportedKey(key)

                # ???
                case 'dynamicsPressurePlotJitterCurve':
                    self.unsupportedKey(key)
                case 'dynamicsPressureGrainDepthCurve':
                    self.unsupportedKey(key)
                case 'dynamicsPressureGrainScaleCurve':
                    self.unsupportedKey(key)
                case 'dynamicsPressureGrainMovementCurve':
                    self.unsupportedKey(key)

                case 'dynamicsPressureStampCountJitterCurve':
                    self.unsupportedKey



                # Fallback, unknown key?
                case _:
                    # Complain about our lack of knowledge
                    self.unknownKey(key)


if __name__ == "__main__":
    main()

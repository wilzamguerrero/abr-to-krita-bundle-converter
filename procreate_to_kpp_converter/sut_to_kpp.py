
#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os.path

import sqlite3

from sut.sut_parser import SUTBrushParser
from kpp.kpp_brush_parser import KPP_Brush_Parser
from kpp.krita_resource_bundle_creator import KritaResourceBundleCreator
from kpp.paintop_preset import TextureBlendingModePixelEngine, BrushTipType, BlendingMode, SensorId


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".sut file path, or directory containing .sut files",
                        type=str)
    parser.add_argument("--input", help="input .kpp file path",
                        type=str)
    parser.add_argument("--output", help="result .kpp file path",
                        type=str)
    parser.add_argument("--bundle", help="result .bundle file path",
                        type=str)
    args = parser.parse_args()

    path = args.file_path
    inputPath = args.input
    outputPath = args.output
    bundlePath = args.bundle

    bundleCreator = None
    if bundlePath:
        bundleCreator = KritaResourceBundleCreator(bundlePath)
        bundleCreator.setDesc(f"Generated from {os.path.basename(path)} by sut_to_kpp.py")
        bundleCreator.createZip()

    paths = []
    if os.path.isdir(path):
        with os.scandir(path) as files:
            for entry in files:
                if entry.path.endswith('.sut'): # "sub tool"
                    paths.append(entry.path)
    elif os.path.isfile(path):
        if path.endswith('.sut'): # "sub tool":
            paths = [path]

    for path in paths:
        name = os.path.basename(path)[:-4]
        print(f"Converting {name}")
        parser = SUTBrushParser(path)

        converter = SUTBrushConverter(parser, inputPath, outputPath, name=name, bundleCreator=bundleCreator)
        converter.convertSettings()
        converter.saveKPP()

    if bundlePath:
        bundleCreator.finishZip()

class SUTBrushConverter:
    def __init__(self, parser, inputPath, outputPath, name="", bundleCreator=None):
        self.parser = parser
        self.writer = KPP_Brush_Parser(inputPresetPath=inputPath, outputPresetPath=outputPath)

        self.name = name
        self.bundleCreator = bundleCreator

    def saveKPP(self):
        kppData = self.writer.saveKPP()

        if self.bundleCreator:
            if self.writer.outputPresetPath:
                self.bundleCreator.addResourceFromPath(self.writer.outputPresetPath, "paintoppresets")
            elif kppData:
                self.bundleCreator.addResourceFromData(kppData, "paintoppresets", f"{self.name}.kpp")


    def convertBlendMode(self, value):
        print("TODO: convertBlendMode")
        return BlendingMode.Normal
    
    def convertTextureBlendMode(self, value):
        print("TODO: convertTextureBlendMode")
        return TextureBlendingModePixelEngine.Multiply

    
    def loadSetting(self, key):
        #return self.parser.loadSetting(key)
        return "[value]"


    def saveSetting(self, key, value):
        print(f"Converting to {key}")
        self.writer.setPixelEngineSetting(key, value)
    
    def saveSettingIfNonZero(self, key, value):
        if value != 0:
            self.saveSetting(key, value)


    def enableCurveOption(self, sensorId, enabled):
        self.saveSetting(f"Pressure{sensorId}", enabled)
        if enabled:
            self.saveSetting(f"{sensorId}UseSameCurve", False)


    def ignoredKey(self,key):
        pass
        #print(f"Ignored: {key} : {self.loadSetting(key)}")
    def unsupportedKey(self, key):
        pass
        #print(f"Unsupported key: {key} : {self.loadSetting(key)}")
    def unsupportedSubKey(self, key):
        pass
        #print(f"Unsupported sub key: {key} : {self.loadSetting(key)}")
    def unknownKey(self, key, value="???"):
        print(f"Unknown key: {key} : {value}")


    def convertSettings(self):
            connection = sqlite3.connect(self.parser.path)

            connection.row_factory = sqlite3.Row

            cursor = connection.cursor()



            pressureCurve = ""

            for row in cursor.execute("SELECT * FROM Manager"):
                for key in row.keys():
                    value = row[key]

                    match key:
                        case '_PW_ID': # ignore
                            pass

                        case 'ToolType':
                            self.unsupportedKey(key)

                        case 'Version':
                            self.unsupportedKey(key)

                        case 'RootUuid':
                            self.unsupportedKey(key)
                        case 'CurrentNodeUuid':
                            self.unsupportedKey(key)

                        case 'MaxVariantID':
                            self.unsupportedKey(key)
                        case 'CommonVariantID':
                            self.unsupportedKey(key)

                        case 'ObjectNodeUuid':
                            self.unsupportedKey(key)

                        case 'PressureGraph':
                            points = self.parser.readPressureGraph(value)
                            for (x,y) in points:
                                pressureCurve += f"{x},{y};"

                        case 'SavedCount':
                            self.ignoredKey(key)

                        # Fallback, unknown key?
                        case _:
                            # Complain about our lack of knowledge
                            self.unknownKey(key, value)


            for row in cursor.execute("SELECT * FROM Node"):
                for key in row.keys():
                    value = row[key]

                    match key:
                        case '_PW_ID': # ignore..
                            pass

                        case 'NodeUuid':
                            self.unsupportedKey(key)
                        case 'NodeName':
                            self.writer.setName(value)

                        case 'NodeShortCutKey':
                            self.ignoredKey(key)

                        case 'NodeLock':
                            self.unsupportedKey(key)

                        case 'NodeInputOp':
                            self.unsupportedKey(key)
                        case 'NodeOutputOp':
                            self.unsupportedKey(key)
                        case 'NodeRangeOp':
                            self.unsupportedKey(key)

                        case 'NodeIcon':
                            self.unsupportedKey(key)
                        case 'NodeIconColor':
                            self.unsupportedKey(key)

                        case 'NodeHidden':
                            self.unsupportedKey(key)

                        case 'NodeInstalledState':
                            self.unsupportedKey(key)
                        case 'NodeInstalledVersion':
                            self.unsupportedKey(key)

                        case 'NodeHideByGrade':
                            self.unsupportedKey(key)

                        case 'NodeDefaultIdentifier':
                            self.unsupportedKey(key)

                        case 'NodeNextUuid':
                            self.unsupportedKey(key)
                        case 'NodeFirstChildUuid':
                            self.unsupportedKey(key)
                        case 'NodeSelectedUuid':
                            self.unsupportedKey(key)

                        case 'NodeVariantID':
                            self.unsupportedKey(key)
                        case 'NodeInitVariantID':
                            self.unsupportedKey(key)

                        case 'NodeCustomIcon':
                            self.unsupportedKey(key)


                        # Fallback, unknown key?
                        case _:
                            # Complain about our lack of knowledge
                            self.unknownKey(key, value)

            
            brushUuid = ""
            diameter = 0

            self.writer.setBrushDefinitionSetting('BrushVersion', 2)

            for row in cursor.execute("SELECT * FROM Variant"):
                for key in row.keys():
                    value = row[key]
                    
                    match key:
                        case '_PW_ID': # ignore..
                            pass

                        case 'VariantID':
                            self.unsupportedKey(key)
                        case 'VariantShowSeparator':
                            self.unsupportedKey(key)
                        case 'VariantShowParam':
                            self.unsupportedKey(key)

                        case 'Opacity':
                            self.saveSetting('OpacityValue', value/100)

                        case 'AntiAlias':
                            self.unsupportedKey(key)

                        case 'CompositeMode':
                            self.saveSetting('CompositeOp', self.convertBlendMode(value))

                        case 'FlickerReduction':
                            self.unsupportedKey(key)
                        case 'FlickerReductionBySpeed':
                            self.unsupportedKey(key)

                        case 'Stickness':
                            self.unsupportedKey(key)

                        # Texture
                        case 'TextureImage':
                            if value is not None:
                                (path1, name, path2) = self.parser.unpackResourcePaths(value)
                                uuid = path2[-36:]
                                resData = self.parser.loadResource(uuid, cursor)
                                md5sum = self.writer.embedResource(resData, f"{name}.png", "patterns")
                                self.saveSetting('Texture/Pattern/PatternMD5Sum', md5sum)
                                self.saveSetting('Texture/Pattern/Enabled', True)
                                self.saveSetting('Texture/Pattern/PatternFileName', f"{name}.png")
                        case 'TextureCompositeMode':
                            self.saveSetting('Texture/Pattern/TexturingMode', self.convertTextureBlendMode(value))
                        case 'TextureReverseDensity':
                            self.unsupportedKey(key)
                        case 'TextureStressDensity':
                            self.unsupportedKey(key)
                        case 'TextureScale2':
                            self.unsupportedKey(key)
                        case 'TextureRotate':
                            self.unsupportedKey(key)

                        # Brush Size
                        case 'BrushSize':
                            diameter = value
                            if brushUuid != "":
                                (width, height) = self.parser.resourceDimensions[brushUuid]
                                print(f"Dmtr: {diameter} / {max(width,height)}")
                                self.writer.setBrushDefinitionSetting('scale', diameter / max(width,height))
                            self.writer.setBrushDefinitionSetting('diameter', value)
                        case 'BrushSizeUnit':
                            self.unsupportedKey(key)
                        case 'BrushSizeEffector':
                            self.unsupportedKey(key)
                        case 'BrushSizeSyncViewScale':
                            self.unsupportedKey(key)

                        case 'BrushAtLeast1Pixel':
                            self.unsupportedKey(key)

                        case 'BrushOpacityEffector':
                            self.unsupportedKey(key)

                        # Flow
                        case 'BrushFlow':
                            self.saveSetting('FlowValue', value/100)
                        case 'BrushFlowEffector':
                            self.unsupportedKey(key)
                        case 'BrushAdjustFlowByInterval':
                            self.unsupportedKey(key)

                        # Hardness
                        case 'BrushHardness':
                            # ???
                            value = 100 - value
                            self.saveSetting('hFade', value)
                            self.saveSetting('vFade', value)
                            self.saveSetting('softnessCurve', f"0,0;1,{value}") # or something

                        # Interval
                        case 'BrushInterval':
                            self.writer.setBrushDefinitionSetting('spacing', value/100) # ???
                        case 'BrushIntervalEffector':
                            self.unsupportedKey(key)
                        case 'BrushAutoIntervalType':
                            self.unsupportedKey(key)

                        case 'BrushContinuousPlot':
                            self.unsupportedKey(key)

                        # Thickness
                        case 'BrushThickness':
                            self.unsupportedKey(key)
                        case 'BrushThicknessEffector':
                            self.unsupportedKey(key)
                        case 'BrushVerticalThicknes':
                            self.unsupportedKey(key)

                        # Rotation
                        case 'BrushRotation':
                            self.unsupportedKey(key)
                        case 'BrushRotationEffector':
                            self.unsupportedKey(key)
                        case 'BrushRotationRandomScale':
                            self.unsupportedKey(key)
                        case 'BrushRotationInSpray':
                            self.unsupportedKey(key)
                        case 'BrushRotationEffectorInSpray':
                            self.unsupportedKey(key)
                        case 'BrushRotationRandomInSpray':
                            self.unsupportedKey(key)

                        # Pattern
                        case 'BrushUsePatternImage':
                            self.unsupportedKey(key)
                        case 'BrushPatternImageArray':
                            if value is not None:
                                (path1, name, path2) = self.parser.unpackResourcePaths(value)
                                brushUuid = path2[-36:]
                                resData = self.parser.loadResource(brushUuid, cursor)
                                md5sum = self.writer.embedResource(resData, f"{name}.png", "brushes")
                                self.writer.setBrushDefinitionSetting('md5sum', md5sum)
                                self.writer.setBrushDefinitionSetting('type', BrushTipType.Predefined)
                                self.writer.setBrushDefinitionSetting('filename', f"{name}.png")

                                if diameter != 0:
                                    (width, height) = self.parser.resourceDimensions[brushUuid]
                                    print(f"Dmtr: {diameter} / {max(width,height)}")
                                    self.writer.setBrushDefinitionSetting('scale', diameter / max(width,height))
                        case 'BrushPatternOrderType':
                            self.unsupportedKey(key)
                        case 'BrushPatternOrderType2':
                            self.unsupportedKey(key)
                        case 'BrushPatternReverse':
                            self.unsupportedKey(key)

                        # Texture
                        case 'TextureForPlot':
                            self.unsupportedKey(key)
                        case 'TextureDensity':
                            self.unsupportedKey(key)
                        case 'TextureDensityEffector':
                            self.unsupportedKey(key)

                        # Water Color
                        case 'BrushUseWaterColor':
                            self.unsupportedKey(key)
                        case 'BrushWaterColor':
                            self.unsupportedKey(key)

                        # Mix Color
                        case 'BrushMixColor':
                            self.unsupportedKey(key)
                        case 'BrushMixColorEffector':
                            self.unsupportedKey(key)
                        case 'BrushMixAlpha':
                            self.unsupportedKey(key)
                        case 'BrushMixAlphaEffector':
                            self.unsupportedKey(key)
                        case 'BrushMixColorExtension':
                            self.unsupportedKey(key)

                        # Blur
                        case 'BrushBlurLinkSize':
                            self.unsupportedKey(key)
                        case 'BrushBlur':
                            self.unsupportedKey(key)
                        case 'BrushBlurUnit':
                            self.unsupportedKey(key)
                        case 'BrushBlurEffector':
                            self.unsupportedKey(key)

                        # Sub Color
                        case 'BrushSubColor':
                            self.unsupportedKey(key)
                        case 'BrushSubColorEffector':
                            self.unsupportedKey(key)

                        case 'BrushRibbon':
                            self.unsupportedKey(key)

                        case 'BrushBlendPatternByDarken':
                            self.unsupportedKey(key)

                        # Spray
                        case 'BrushUseSpray':
                            self.unsupportedKey(key)
                        case 'BrushSpraySize':
                            self.unsupportedKey(key)
                        case 'BrushSpraySizeUnit':
                            self.unsupportedKey(key)
                        case 'BrushSpraySizeEffector':
                            self.unsupportedKey(key)
                        case 'BrushSprayDensity':
                            self.unsupportedKey(key)
                        case 'BrushSprayDensityEffector':
                            self.unsupportedKey(key)
                        case 'BrushSprayBias':
                            self.unsupportedKey(key)
                        case 'BrushSprayUseFixedPoint':
                            self.unsupportedKey(key)
                        case 'BrushSprayFixedPointArray':
                            self.unsupportedKey(key)

                        # Revision
                        case 'BrushUseRevision':
                            self.unsupportedKey(key)
                        case 'BrushRevision':
                            self.unsupportedKey(key)
                        case 'BrushRevisionBySpeed':
                            self.unsupportedKey(key)
                        case 'BrushRevisionByViewScale':
                            self.unsupportedKey(key)
                        case 'BrushRevisionBezier':
                            self.unsupportedKey(key)

                        # InOut
                        case 'BrushInOutTarget':
                            self.unsupportedKey(key)
                        case 'BrushInOutType':
                            self.unsupportedKey(key)
                        case 'BrushInOutBySpeed':
                            self.unsupportedKey(key)

                        # In
                        case 'BrushUseIn':
                            self.unsupportedKey(key)
                        case 'BrushInLength':
                            self.unsupportedKey(key)
                        case 'BrushInLengthUnit':
                            self.unsupportedKey(key)
                        case 'BrushInRatio':
                            self.unsupportedKey(key)

                        # Out
                        case 'BrushUseOut':
                            self.unsupportedKey(key)
                        case 'BrushOutLength':
                            self.unsupportedKey(key)
                        case 'BrushOutLengthUnit':
                            self.unsupportedKey(key)
                        case 'BrushOutRatio':
                            self.unsupportedKey(key)

                        case 'BrushSharpenCorner':
                            self.unsupportedKey(key)

                        # Water Edge
                        case 'BrushUseWaterEdge':
                            self.unsupportedKey(key)
                        case 'BrushWaterEdgeRadius':
                            self.unsupportedKey(key)
                        case 'BrushWaterEdgeRadiusUnit':
                            self.unsupportedKey(key)
                        case 'BrushWaterEdgeAlphaPower':
                            self.unsupportedKey(key)
                        case 'BrushWaterEdgeValuePower':
                            self.unsupportedKey(key)
                        case 'BrushWaterEdgeAfterDrag':
                            self.unsupportedKey(key)
                        case 'BrushWaterEdgeBlur':
                            self.unsupportedKey(key)
                        case 'BrushWaterEdgeBlurUnit':
                            self.unsupportedKey(key)

                        # Vector Eraser
                        case 'BrushUseVectorEraser':
                            self.unsupportedKey(key)
                        case 'BrushVectorEraserType':
                            self.unsupportedKey(key)
                        case 'BrushVectorEraserReferAllLayer':
                            self.unsupportedKey(key)

                        case 'BrushEraseAllLayer':
                            self.unsupportedKey(key)

                        case 'BrushEnableSnap':
                            self.unsupportedKey(key)

                        # Vector Magnet
                        case 'BrushUseVectorMagnet':
                            self.unsupportedKey(key)
                        case 'BrushVectorMagnetPower':
                            self.unsupportedKey(key)

                        case 'BrushUseReferLayer':
                            self.unsupportedKey(key)

                        # Fill
                        case 'FillReferVectorCenter':
                            self.unsupportedKey(key)
                        case 'FillUseExpand':
                            self.unsupportedKey(key)
                        case 'FillExpandLength':
                            self.unsupportedKey(key)
                        case 'FillExpandLengthUnit':
                            self.unsupportedKey(key)
                        case 'FillExpandType':
                            self.unsupportedKey(key)
                        case 'FillColorMargin':
                            self.unsupportedKey(key)
                        

                        # Fallback, unknown key?
                        case _:
                            # Complain about our lack of knowledge
                            self.unknownKey(key, value)


                break # only the first Variant ...?


            # no MaterialFile for now



if __name__ == "__main__":
    main()


#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import os.path

from abr.abr_parser import ABRBrushParser
from kpp.kpp_brush_parser import KPP_Brush_Parser
from kpp.krita_resource_bundle_creator import KritaResourceBundleCreator
from kpp.paintop_preset import TextureBlendingModePixelEngine, BrushTipType, BlendingMode, SensorId

from math import radians

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".abr file path",
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
        bundleCreator.setDesc(f"Generated from {os.path.basename(path)} by abr_to_kpp.py")
        bundleCreator.createZip()


    parser = ABRBrushParser(path)
    #parser.loadABR(path)

    parser.openFile()

    # read desc first to get brushtip names
    parser.readDesc(parser.fileHandle, parser.gotoBlock("desc"))

    sampUuidMd5 = {}
    pattUuidMd5 = {}

    if bundleCreator:
        sampEnd = parser.gotoBlock("samp")
        sampNames = []
        while parser.fileHandle.seek(0, 1) < sampEnd:
            # Invert the brushtip, so black=opaque
            (brushtipPNG, brushtipName, brushtipUuid) = parser.readBrushtip(parser.fileHandle, returnImage=True, invert=True)
            if brushtipName in sampNames:
                brushtipName = f"{brushtipName} {brushtipUuid[0:7]}"
            sampNames.append(brushtipName)
            md5sum = bundleCreator.addResourceFromData(brushtipPNG, 'brushes', f"{brushtipName}.png")
            sampUuidMd5[brushtipUuid] = md5sum
        parser.verifyBytesRead(parser.fileHandle, sampEnd, 'samp')

        pattEnd = parser.gotoBlock("patt")
        pattNames = []
        while parser.fileHandle.seek(0, 1) < pattEnd:
            images = parser.readPattern(parser.fileHandle, returnImage=True)
            for (patternPNG, patternName, patternUuid) in images:
                if patternName in pattNames:
                    patternName = f"{patternName} {patternUuid[0:7]}"
                pattNames.append(patternName)
                md5sum = bundleCreator.addResourceFromData(patternPNG, 'patterns', f"{patternName}.png")
                pattUuidMd5[patternUuid] = md5sum
        parser.verifyBytesRead(parser.fileHandle, pattEnd, 'patt')

    #parser.readDesc(parser.fileHandle, parser.gotoBlock("desc"))

    parser.closeFile()

    names = []
    for i in range(len(parser.desc['Brsh'])):
        name = parser.desc['Brsh'][i]['Objc']['brushPreset'][0]['Nm  ']['TEXT']
        print(f"### Brush number {i}: {name}")
        name = name.replace("/", "_")
        if name in names:
            name = f"{name} Duplicate" # ...
        names.append(name)
        output = os.path.join(outputPath,f"{name}.kpp") if outputPath else ""
        converter = ABRBrushConverter(parser, inputPath, output, name=name, bundleCreator=bundleCreator, sampUuidMd5=sampUuidMd5, pattUuidMd5=pattUuidMd5)
        converter.convertSettings(i)
        converter.saveKPP()

    if bundlePath:
        bundleCreator.finishZip()

class ABRBrushConverter:
    def __init__(self, parser, inputPath, outputPath, name="", bundleCreator=None, sampUuidMd5=None, pattUuidMd5=None, sampUuidPNG=None):
        self.parser = parser
        self.writer = KPP_Brush_Parser(inputPresetPath=inputPath, outputPresetPath=outputPath)

        self.name = name
        self.bundleCreator = bundleCreator

        self.sampUuidMd5 = sampUuidMd5
        self.pattUuidMd5 = pattUuidMd5
        self.sampUuidPNG = sampUuidPNG if sampUuidPNG else {}

        self.thumbnailPNG = None


    def saveKPP(self):
        kppData = self.writer.saveKPP(thumbnailPNG=self.thumbnailPNG)

        if self.bundleCreator:
            if self.writer.outputPresetPath:
                self.bundleCreator.addResourceFromPath(self.writer.outputPresetPath, "paintoppresets")
            elif kppData:
                self.bundleCreator.addResourceFromData(kppData, "paintoppresets", f"{self.name}.kpp")

    
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


    # the Krita values seem to differ between the Pixel engine and
    # other engines (whose numbering skips two texture modes they don't support, lightness map(2)/gradient map(3)
    # these values are for the Pixel engine.
    blendModesTexture = {
        'Mltp': TextureBlendingModePixelEngine.Multiply,
        #'': TextureBlendingModePixelEngine.Subtract,
        'Drkn': TextureBlendingModePixelEngine.Darken,
        'Ovrl': TextureBlendingModePixelEngine.Overlay,
        'CDdg': TextureBlendingModePixelEngine.ColorDodge,
        'CBrn': TextureBlendingModePixelEngine.ColorBurn,
        'Hght': TextureBlendingModePixelEngine.HeightPhotoshop,
        'hardMix': TextureBlendingModePixelEngine.HardMixPhotoshop,
    }

    # in no particular order
    blendModes = {
        'Mltp': BlendingMode.Multiply,
        'Ovrl': BlendingMode.Overlay,
        'linearBurn': BlendingMode.LinearBurn,
        'hardMix': BlendingMode.HardMixPhotoshop,
        'CBrn': BlendingMode.ColorBurn,
        'CDdg': BlendingMode.ColorDodge,
        'Drkn': BlendingMode.Darken,
        #'linearHeight':
        #'Hght':
        'Nrml': BlendingMode.Normal, # maybe only in toolOptions?
    }

    def convertTextureBlendMode(self, value):
        if not value in self.blendModesTexture:
            print(f"Warning: Unknown texture blend mode {value}")
            return TextureBlendingModePixelEngine.Multiply
        return self.blendModesTexture[value]
    
    sensors = {
        # 0: disabled
        1: SensorId.Fade,
        2: SensorId.Pressure,
        3: SensorId.TiltDirection,
        4: SensorId.TangentialPressure, 
        5: SensorId.Rotation
    }

    def convertSensor(self, value):
        if not value in self.sensors:
            print(f"Warning: Unknown sensor {value}")
            return SensorId.Pressure
        return self.sensors[value]


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


    def getOnlyKey(self, dict):
        keys = list(dict.keys())
        lenKeys = len(keys)
        if lenKeys != 1:
            print(f"tried to getOnlyKey of {lenKeys}")
        return keys[0]
    def getValueFromKey(self, key):
        value = self.getOnlyKey(key)
        type = self.getOnlyKey(key[value])

        match type:
            case 'TEXT':
                return key[value]['TEXT']

            case 'Objc':
                return key[value]['Objc']
            
            case 'UntF':
                (unit, float) = key[value]['UntF']
                match unit:
                    case '#Pxl': # Pixels
                        return float
                    case '#Prc': # Percentage (0.0 to 100.0 %)
                        # Krita typically stores percentage as 0.0 to 1.0
                        return float/100
                    case '#Ang': # Angle (-180.0 to 180.0 degrees)
                        # Krita typically stores angle as radians (0 to π)
                        if float < 0:
                            float += 360
                        return radians(float)
                    case _:
                        print(f"Unknown unit {unit} for {value}! Value: {float}")
                        return float

            case 'bool':
                return key[value]['bool']

            case 'long':
                return key[value]['long']

            case 'enum':
                # todo, process the enum
                # if key[value]['enum'] == "BlnM"

                return key[value]['enum'][1]

            case 'doub':
                return key[value]['doub']

            case _ :
                print(f"unknown type in value: {type}")
                return key[value][type]


    def convertSettings(self, i):
        preset = self.parser.desc['Brsh'][i]['Objc']['brushPreset']

        for child in preset:
            key = self.getOnlyKey(child)
            value = self.getValueFromKey(child)

            match key:
                case 'Nm  ':
                    self.writer.setName(value)

                # Brush
                case 'Brsh':
                    type = self.getOnlyKey(value)
                    if type == 'computedBrush':
                        self.writer.setBrushDefinitionSetting('type', BrushTipType.Auto)
                    elif type == 'sampledBrush':
                        self.writer.setBrushDefinitionSetting('type', BrushTipType.Predefined)
                    else:
                        print(f"Unknown brush type {type}")

                    self.writer.setBrushDefinitionSetting('BrushVersion', 2)

                    brushUuid = ""
                    diameter = 0
                    (width, height) = self.parser.brushtipSizes[""] # default

                    for child in value[type]:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            # 'computedBrush' and 'sampledBrush'
                            case 'Dmtr': # Diameter
                                if type == 'sampledBrush':
                                    diameter = value2
                                    if brushUuid == "":
                                        print(f"Dmtr: {diameter} / default {max(width,height)}")
                                    else:
                                        print(f"Dmtr: {diameter} / {max(width,height)}")
                                    self.writer.setBrushDefinitionSetting('scale', diameter / max(width,height))
                                elif type == 'computedBrush':
                                    self.writer.setBrushDefinitionSetting('diameter', value2)
                            case 'Hrdn': # Hardness
                                if type == 'computedBrush':
                                    value = 100 - value2
                                    self.saveSetting('hFade', value)
                                    self.saveSetting('vFade', value)
                                    self.saveSetting('softnessCurve', f"0,0;1,{value}") # or something
                            case 'Angl': # Angle
                                self.writer.setBrushDefinitionSetting('angle', value2)
                            case 'Rndn': # Roundness
                                if type == 'computedBrush':
                                    self.writer.setBrushDefinitionSetting('ratio', value2)
                            case 'Spcn': # Spacing
                                # from percent to 0-10
                                # todo, this value seems off?
                                self.writer.setBrushDefinitionSetting('spacing', value2)
                            case 'Intr': 
                                self.unsupportedKey(key)
                            case 'flipX':
                                self.enableCurveOption('Mirror', value2)
                                self.saveSetting('HorizontalMirrorEnabled', value2)
                            case 'flipY':
                                self.enableCurveOption('Mirror', value2)
                                self.saveSetting('VerticalMirrorEnabled', value2)

                            # 'sampledBrush'
                            case 'sampledData':
                                brushUuid = value2
                                #self.writer.setBrushDefinitionSetting('filename', f"{brushUuid}.png")
                                md5 = self.sampUuidMd5.get(brushUuid)
                                if md5 is not None:
                                    self.writer.setBrushDefinitionSetting('md5sum', md5)

                                # Store thumbnail for this brush
                                thumbnail = self.sampUuidPNG.get(brushUuid)
                                if thumbnail is not None:
                                    self.thumbnailPNG = thumbnail

                                # get the brushtip size needed for scale
                                try:
                                    (width, height) = self.parser.brushtipSizes[brushUuid]
                                except(KeyError):
                                    print(f"Warning: brushUuid {brushUuid} not found in brushtips, scale will be wrong")
                                # if diameter was read before the brushUuid, set scale properly here
                                if diameter != 0:
                                    print(f"diameter: {diameter} / {max(width,height)}")
                                    self.writer.setBrushDefinitionSetting('scale', diameter / max(width,height))
                            case 'Nm  ':
                                value = value2.replace("/", "_")
                                self.writer.setBrushDefinitionSetting('filename', f"{value}.png")
                                self.unsupportedKey(key)

                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'useTipDynamics':
                    self.unsupportedKey(key)
                case 'flipX':
                    self.enableCurveOption('Mirror', value)
                    self.saveSetting('HorizontalMirrorEnabled', value)
                case 'flipY':
                    self.enableCurveOption('Mirror', value)
                    self.saveSetting('VerticalMirrorEnabled', value)
                case 'brushProjection':
                    self.unsupportedKey(key)
                case 'minimumDiameter':
                    self.unsupportedKey(key)
                case 'minimumRoundness':
                    self.unsupportedKey(key)
                case 'tiltScale':
                    self.unsupportedKey(key)

                case 'szVr': # Size Control
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy': # Control # (type)
                                self.enableCurveOption('Size', value2 != 0)
                                if value2 != 0:
                                    curve = "0,0;1,1"
                                    self.writer.setSensor('SizeSensor', self.convertSensor(value2), curve)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)
                
                case 'angleDynamics':
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.unsupportedKey(key)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'roundnessDynamics':
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.unsupportedKey(key)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'useScatter':
                    self.enableCurveOption('Scatter', value)
                case 'Spcn': # spacing?
                    self.unsupportedKey(key)
                case 'Cnt ': # Tip Count
                    self.unsupportedKey(key)
                case 'bothAxes':
                    self.unsupportedKey(key)


                case 'countDynamics': # Tip Count Dynamics
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.unsupportedKey(key)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'scatterDynamics':
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.enableCurveOption('Scatter', value2 != 0)
                                if value2 != 0:
                                    curve = "0,0;1,1"
                                    self.writer.setSensor('ScatterSensor', self.convertSensor(value2), curve)
                                self.unsupportedKey(key)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.enableCurveOption('Scatter', value2 != 0)
                                self.saveSetting('ScatterValue', value2)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)
                
                case 'dualBrush':
                    for key2 in value.keys():
                        match key2:
                            case 'dualBrush':
                                self.unsupportedKey(key)
                            case 'useDualBrush':
                                self.unsupportedKey(key)
                            case 'Flip':
                                self.unsupportedKey(key)
                            case 'Brsh':
                                self.unsupportedKey(key)
                                # etc...
                            case 'BlnM': # Blending Mode
                                self.unsupportedKey
                            case 'useScatter':
                                self.unsupportedKey(key)
                            case 'Spcn':
                                self.unsupportedKey(key)
                            case 'Cnt ':
                                self.unsupportedKey(key)
                            case 'bothAxes':
                                self.unsupportedKey(key)
                            case 'countDynamics':
                                self.unsupportedKey(key)
                            case 'scatterDynamics':
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                # Brush Group
                case 'brushGroup':
                    self.unsupportedKey(key)

                # Texture --
                case 'useTexture':
                    self.saveSetting('Texture/Pattern/Enabled', value != 0)
                case 'TxtC': # Texture each tip
                    self.unsupportedKey(key)
                case 'interpretation':
                    self.unsupportedKey(key)
                case 'textureBlendMode':
                    self.saveSetting('Texture/Pattern/TexturingMode', self.convertTextureBlendMode(value))
                    self.saveSetting('Texture/Pattern/UseSoftTexturing', True) # this mimics PS texturing
                case 'textureDepth':
                    self.enableCurveOption('Texture/Strength/', value != 0)
                    self.saveSetting('Texture/Strength/Value', value)
                case 'minimumDepth':
                    self.unsupportedKey(key)

                case 'textureDepthDynamics':
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.enableCurveOption('Texture/Strength/', value2 != 0)
                                if value2 != 0:
                                    curve = "0,0;1,1"
                                    self.writer.setSensor('Texture/Strength/Sensor', self.convertSensor(value2), curve)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)
                

                case 'Txtr': # Texture Pattern
                    for child in value['Ptrn']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'Nm  ': # Name
                                value = f"{value2}.png".replace("/", "_")
                                self.saveSetting('Texture/Pattern/PatternFileName', value)
                                self.saveSetting('Texture/Pattern/Name', value2)
                            case 'Idnt': # Identity # UUID
                                #value = f"{value2}.png"
                                #self.saveSetting('Texture/Pattern/PatternFileName', value)
                                #self.saveSetting('Texture/Pattern/Name', value)

                                md5 = self.pattUuidMd5.get(value2)
                                if md5 is not None:
                                    self.saveSetting('Texture/Pattern/PatternMD5Sum', md5)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)
                
                case 'textureScale':
                    self.saveSetting('Texture/Pattern/Scale', value)
                case 'InvT': # Invert Texture
                    self.saveSetting('Texture/Pattern/Invert', value)
                case 'protectTexture':
                    self.unsupportedKey(key)
                case 'textureBrightness':
                    # from ??? to -1;1
                    value /= 100
                    self.saveSetting('Texture/Pattern/Brightness', value)
                case 'textureContrast':
                    # from ??? to 0;2
                    value /= 50
                    self.saveSetting('Texture/Pattern/Contrast', value)

                # --

                case 'usePaintDynamics':
                    self.unsupportedKey(key)
                
                case 'prVr': # Flow Jitter
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.enableCurveOption('Flow', value2 != 0)
                                if value2 != 0:
                                    curve = "0,0;1,1"
                                    self.writer.setSensor('FlowSensor', self.convertSensor(value2), curve)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'opVr': # Opacity Jitter
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.enableCurveOption('Opacity', value2 != 0)
                                if value2 != 0:
                                    curve = "0,0;1,1"
                                    self.writer.setSensor('OpacitySensor', self.convertSensor(value2), curve)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'wtVr': # ???
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.unsupportedKey(key)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'mxVr': # ???
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.unsupportedKey(key)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)

                case 'useColorDynamics':
                    self.unsupportedKey(key)

                case 'clVr': # Color Dynamics
                    for child in value['brVr']:
                        key2 = self.getOnlyKey(child)
                        value2 = self.getValueFromKey(child)
                        match key2:
                            case 'bVTy':
                                self.unsupportedKey(key)
                            case 'fStp': # Fade Step
                                self.unsupportedKey(key)
                            case 'jitter':
                                self.unsupportedKey(key)
                            case 'Mnm ': # minimum?
                                self.unsupportedKey(key)
                            case _:
                                self.unknownKey(f"{key} {key2}", value2)
                
                case 'H   ': # Hue Jitter
                    self.enableCurveOption('h', value != 0)
                case 'Strt': # Saturation Jitter
                    self.enableCurveOption('s', value != 0)
                case 'Brgh': # Brightness Jitter
                    self.enableCurveOption('v', value != 0)
                case 'purity':
                    self.unsupportedKey(key)
                case 'colorDynamicsPerTip':
                    self.unsupportedKey(key)
                case 'Wtdg': # Wet Edges
                    self.unsupportedKey(key)
                case 'Nose': # Noise
                    self.unsupportedKey(key)
                case 'Rpt ': # Airbrush # (repeat?)
                    self.saveSetting('PaintOpSettings/isAirbrushing', value)

                case 'useBrushSize':
                    self.unsupportedKey(key)
                case 'useBrushPose':
                    self.unsupportedKey(key)

                case 'toolOptions':
                    self.unsupportedKey(key)

                # Fallback, unknown key?
                case _:
                    # Complain about our lack of knowledge
                    self.unknownKey(key, value)


if __name__ == "__main__":
    main()

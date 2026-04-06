#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023, 2024 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import zlib
import xml.dom.minidom as miniDOM
import base64
import hashlib
import re
from enum import IntEnum
import struct

try:
    # for running from the other scripts
    from kpp.paintop_preset import (presetForEngine,
                                    Sensor,
                                    BrushTipType)
except ImportError:
    # for running standalone
    from paintop_preset import (presetForEngine,
                                Sensor,
                                BrushTipType)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".kpp file path",
                        type=str)
    parser.add_argument("--dump_xml", help="xml dump output file path",
                        type=str)
    parser.add_argument("--output", help="result .kpp file path",
                        type=str)
    args = parser.parse_args()

    path = args.file_path
    xmloutpath = args.dump_xml
    newpath = args.output

    parser = KPP_Brush_Parser(path, newpath)
    parser.getPresetXML()

    if xmloutpath:
        parser.dumpPresetXML(xmloutpath)


class KPP_Brush_Parser:
    def __init__(self, inputPresetPath=None, outputPresetPath=None, reuseImage=True, engine=None):
        self.inputPresetPath = inputPresetPath
        self.outputPresetPath = outputPresetPath

        self.modifyExisting = inputPresetPath and reuseImage

        if inputPresetPath and reuseImage:
            if self.outputPresetPath: # modifying copy
                self.makeDuplicate()
                self.inputPresetPath == self.outputPresetPath
            else: # overwrite existing...
                #self.outputPresetPath == self.inputPresetPath
                print("overwriting input kpp is disabled")

        #if outputPresetPath and not inputPresetPath: # generating new
        if not inputPresetPath: # generating new
            self.xml = self.generatePresetXML()
        else: # modifying existing
            self.xml = self.getPresetXML(reuseImage)

        if not engine:
            engine = self.readSetting('paintop')
        self.engine = presetForEngine(engine)

    def saveKPP(self, hasImage=False, thumbnailPNG=None):
        #if not self.outputPresetPath:
        #    print("Cannot save KPP: No output path!")
        #    return

        if self.modifyExisting:
            self.writePresetXML()
        else:
            if hasImage:
                self.addPresetXML()
            else:
                return self.generateKPP(thumbnailPNG=thumbnailPNG) # ...

    def generatePresetXML(self):
        presetXML = miniDOM.getDOMImplementation().createDocument(None, 'Preset', None)
        presetXML.documentElement.setAttribute("name", "Unnamed Preset")
        presetXML.documentElement.setAttribute("paintopid", "paintbrush")
        presetXML.documentElement.setAttribute("embedded_resources", "0")

        brushDef = presetXML.createElement("brush_definition")
        brush = presetXML.createElement("Brush")
        brush.setAttribute("BrushVersion", "2") # Otherwise scale will be doubled
        brushDef.appendChild(presetXML.createTextNode(brush.toxml()))
        presetXML.documentElement.appendChild(brushDef)

        return presetXML

    def generateKPP(self, thumbnailPNG=None):
        if thumbnailPNG:
            # Use the provided brushtip PNG as the thumbnail;
            # we need to inject the preset zTXt and tEXt chunks into it.
            data = self._injectPresetIntoPNG(thumbnailPNG)
        else:
            data = self._generateKPPWithBlankImage()

        if self.outputPresetPath:
            with open(self.outputPresetPath, 'wb') as f:
                f.write(data)

        return data

    def _generatePresetChunks(self):
        """Generate the zTXt (preset) and tEXt (version) PNG chunks."""
        chunks = bytearray()

        # Compressed Text (preset data)
        ztxt = b'zTXt'
        ztxtData = b"preset\0" + b"\0"
        ztxtData += zlib.compress(self.xml.toxml(encoding="us-ascii"))
        chksum = zlib.crc32(ztxt + ztxtData)
        chunks += struct.pack(">i", len(ztxtData))
        chunks += ztxt
        chunks += ztxtData
        chunks += struct.pack(">I", chksum)

        # Text (preset version)
        textID = b"tEXt"
        textVer = b"version\0" + b"5.0"
        chunks += struct.pack(">i", len(textVer))
        chunks += textID
        chunks += textVer
        chunks += b"\xF9\x0F\x32\xE9"

        return chunks

    def _injectPresetIntoPNG(self, pngData):
        """Insert preset zTXt/tEXt chunks into an existing PNG, before IDAT."""
        data = bytearray(pngData)
        presetChunks = self._generatePresetChunks()

        # Find the first IDAT chunk to insert before it
        pos = 8  # skip PNG magic
        while pos < len(data):
            chunkLen = struct.unpack(">I", data[pos:pos+4])[0]
            chunkType = data[pos+4:pos+8]
            if chunkType == b'IDAT':
                # Insert preset chunks right before IDAT
                result = bytearray(data[:pos]) + presetChunks + bytearray(data[pos:])
                return bytes(result)
            pos += 12 + chunkLen  # 4 len + 4 type + data + 4 crc

        # Fallback: insert before IEND
        iendPos = data.rfind(b'IEND') - 4  # 4 bytes for length
        if iendPos > 0:
            result = bytearray(data[:iendPos]) + presetChunks + bytearray(data[iendPos:])
            return bytes(result)

        return bytes(data)

    def _generateKPPWithBlankImage(self):
        (width, height) = (8,8)
        imgData = [bytes(b'\xff' * width)] * height # white

        data = bytearray()

        PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
        data += (PNG_MAGIC)

        # Image Header
        ihdr = b'IHDR'
        ihdrData = struct.pack(">i", width)
        ihdrData += struct.pack(">i", height)
        ihdrData += struct.pack(">B", 8) # depth. fixme if other depths are supported
        ihdrData += struct.pack(">B", 0) # color type; grayscale
        ihdrData += struct.pack(">B", 0) # compression
        ihdrData += struct.pack(">B", 0) # filter
        ihdrData += struct.pack(">B", 0) # interlacing
        chksum = zlib.crc32(ihdr + ihdrData)

        data += (struct.pack(">i", 13)) # IHDR chunk len
        data += (ihdr)
        data += (ihdrData)
        data += (struct.pack(">I", chksum))

        # Preset chunks (zTXt + tEXt)
        data += self._generatePresetChunks()

        # Image Data
        idat = b'IDAT'
        imgDataWithFilterBytes = bytearray()
        for row in imgData:
            # Prepend the filter type (0: none) to each scanline.
            imgDataWithFilterBytes += b"\0"+row
        idatData = zlib.compress(imgDataWithFilterBytes)
        chksum = zlib.crc32(idat + idatData)

        data += (struct.pack(">i", len(idatData)))
        data += (idat)
        data += (idatData)
        data += (struct.pack(">I", chksum))

        # Image End
        data += (b"\0\0\0\0" + b"IEND" + b"\xae\x42\x60\x82")

        return data


    def makeDuplicate(self):
        # todo: how to do this efficiently?
        buf = b""
        with open(self.inputPresetPath, 'rb') as f:
            buf = f.read() #all
        with open(self.outputPresetPath, 'wb') as f:
            f.write(buf)


    def getPresetXML(self, reuseImage=True):
        with open(self.inputPresetPath, 'r+b') as f:
            PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
            if f.read(8) != PNG_MAGIC:
                print(f"Error: Not a .png file!: {self.inputPresetPath}")
                return False

            found_preset_data = False
            while buf := f.read(4):
                chunk_data_len = int.from_bytes(buf, 'big')
                chunk_id = f.read(4)

                if chunk_id == b'zTXt' or chunk_id == b'iTXt':
                    found_preset_data = True
                    # Remember this chunk info for later
                    if reuseImage:
                        self.chunk_type = chunk_id
                        self.chunk_pos = f.seek(0, 1) - 8
                        self.data_length = chunk_data_len

                    # Validate that this is a KPP
                    self.head_expected = b''
                    if chunk_id == b'zTXt':
                        self.head_expected = b'preset\0\0'
                    elif chunk_id == b'iTXt':
                        self.head_expected = b'preset\0\1\0UTF-8\0preset\0'

                    head = f.read(len(self.head_expected))
                    if head != self.head_expected:
                        print(f"Error: Metadata does not appear to contain a preset: {self.inputPresetPath}")
                        return False

                    # Read and decompress the text
                    compressed_text = f.read(chunk_data_len - len(self.head_expected))
                    text = zlib.decompress(compressed_text)

                    # Work around a bug in Krita 5's preset saving...
                    # (remove an invalid value)
                    text = text.decode()
                    patternMd5 = re.search(r'<param (?:type="string" )?name="Texture/Pattern/PatternMD5"(?: type="string")?><!\[CDATA\[(.+?)\]\]></param>', text)
                    if patternMd5 and re.search("[^a-zA-Z0-9+/=]", patternMd5.group(1)):
                        text = re.sub(re.escape(patternMd5.group(0)), "", text)
                        # Note that this may print unprintable characters...
                        print(f"Info: removing bad pattern md5 \"{patternMd5.group(1)}\" to parse {self.inputPresetPath}")

                    # Convert it to XML
                    # and make sure it's valid, still
                    XMLdoc = miniDOM.parseString(text)
                    XMLroot = XMLdoc.documentElement
                    if XMLroot.tagName != "Preset":
                        print("No Preset tag")
                        return False
                    old_name = XMLroot.getAttribute("name")
                    if old_name == None:
                        print("Preset has no name")
                        return False
                    
                    # Everything was fine, so read the rest of file so we can append it back later
                    if reuseImage:
                        f.seek(self.chunk_pos + 8 + chunk_data_len + 4, 0)
                        self.rest_of_file = f.read()

                    #print(XMLroot)

                    return XMLdoc

                # Seek to next chunk at current position + data + CRC
                f.seek(chunk_data_len + 4, 1)

            if not found_preset_data:
                print(f"Error: Found no preset metadata chunk.: {self.inputPresetPath}")
                return False

    # Overwrite existing KPP XML
    def writePresetXML(self):
        new_text = self.xml.toxml(encoding="us-ascii")

        new_compressed_text = zlib.compress(new_text)

        new_data_length = len(self.head_expected) + len(new_compressed_text)

        with open(self.outputPresetPath, 'r+b') as f:
            PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
            if f.read(8) != PNG_MAGIC:
                print("Not a .png file!")
                return False

            f.seek((self.chunk_pos + 8 + len(self.head_expected)), 0)
            # Cut off the rest of the file and write the new text.
            f.truncate()
            f.write(new_compressed_text)

            chksum = zlib.crc32(self.chunk_type + self.head_expected + new_compressed_text)
            # Write the CRC after the data we just wrote.
            f.write(chksum.to_bytes(4, 'big'))
            
            f.write(self.rest_of_file)

            f.seek(self.chunk_pos, 0)
            f.write(new_data_length.to_bytes(4, 'big'))

    # Add XML to existing PNG file
    def addPresetXML(self):
        with open(self.outputPresetPath, 'r+b') as f:
            PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
            if f.read(8) != PNG_MAGIC:
                print("Not a .png file!")
                return False
            
            restOfFile = b""

            # apparently the text must be written before the IDAT and IEND, so..
            while buf := f.read(4):
                chunk_data_len = int.from_bytes(buf, 'big')
                chunk_id = f.read(4)

                if chunk_id == b"IDAT":
                    startIDAT = f.seek(-8, 1)
                    restOfFile = f.read()
                    f.seek(startIDAT, 0)
                    break

                # Seek to next chunk at current position + data + CRC
                f.seek(chunk_data_len + 4, 1)

            presetChunkID= b"zTXt"
            presetData = b"preset\0\0" + zlib.compress(self.xml.toxml(encoding="us-ascii"))
            presetChunkLength = len(presetData)
            f.write(presetChunkLength.to_bytes(4, 'big'))
            f.write(presetChunkID)
            f.write(presetData)
            chksum = zlib.crc32(presetChunkID + presetData)
            f.write(chksum.to_bytes(4, 'big'))

            # preset version, this is required
            textID = b"tEXt"
            textVer = b"version\x005.0"
            f.write(len(textVer).to_bytes(4, 'big'))
            f.write(textID)
            f.write(textVer)
            f.write(b"\xF9\x0F\x32\xE9") # CRC

            f.write(restOfFile)


    def dumpPresetXML(self, outpath):
        with open(outpath, 'w') as f:
            print(self.xml.toprettyxml(), file = f)
    

    def embedResource(self, data, filename, type):
        base64Image = base64.b64encode(data)

        md5sum = hashlib.md5(base64Image, usedforsecurity=False).hexdigest()
        resource = self.xml.createElement('resource')
        resource.setAttribute('md5sum', md5sum)
        resource.setAttribute('type', type)
        resource.setAttribute('name', filename)
        resource.setAttribute('filename', filename)
        resource.appendChild(self.xml.createTextNode(base64Image.decode()))

        resources = self.xml.getElementsByTagName('resources')
        if len(resources) == 0:
            # if it doesn't exist we need to make it
            print(f"Creating Resources element")
            resources = self.xml.createElement('resources')
            self.xml.documentElement.appendChild(resources)
        else:
            resources = resources[0]

        resources.appendChild(resource)

        preset = self.xml.documentElement
        currentResources = preset.getAttribute("embedded_resources")
        if currentResources is None:
            currentResources = 0
        else:
            currentResources = int(currentResources)
        preset.setAttribute("embedded_resources", str(currentResources + 1))

        return md5sum


    def setSetting(self, key, value):
        if key == 'name':
            #print("use setName")
            self.setName(value)

        if key in self.engine.keys:
            param = self.engine.keys[key]
            type = param['type']
            if type == Sensor:
                print("use setSensor")
                #self.setSensor(key, value)
            else:
                self.setParam(key, value, type)
        else:
            print(f"Unknown {self.engine.keys['paintop']} param {key}")

    def setPixelEngineSetting(self, key, value):
        self.setSetting(key, value)


    def setPresetKey(self, key, value):
        if key in self.engine.presetKeys:
            if key == 'paintopid':
                print("Changing the brush engine (this is probably a bad idea)")
            elif key == 'embedded_resources':
                print("Manually changing the embedded resources count...")

            self.xml.documentElement.setAttribute(key, value)
            print(f"{key}: {value}")
        else:
            print(f"Unknown {self.engine.keys['paintop']} Preset setting {key}")

    def setName(self, value):
        self.xml.documentElement.setAttribute("name", value)
        print(f"Name: {value}")
    
    def setParam(self, key, value, type=False):
        if type and value.__class__ is not type:
            print(f"Warning: {value} is not {type} expected by {key} (expected type may be wrong)")
        if issubclass(type, IntEnum):
            value = int(value) # don't make it a string
        foundParam = False
        for param in self.xml.documentElement.getElementsByTagName('param'):
            name = param.getAttribute('name')
            if (name == key):
                print(f"set {name} to {value}")
                param.replaceChild(self.xml.createTextNode(str(value)), param.firstChild)
                foundParam = True
        if not foundParam:
            # if it doesn't exist we need to make it
            #print("Warning: didn't set", key)
            print(f"Creating {key} with {value}")
            newParam = self.xml.createElement("param")
            newParam.setAttribute('type', 'string')
            newParam.setAttribute('name', key)
            newParam.appendChild(self.xml.createTextNode(str(value)))
            self.xml.documentElement.appendChild(newParam)

    def readSetting(self, key):
        for param in self.xml.getElementsByTagName('param'):
            if param.getAttribute('name') == key:
                return param.firstChild.data

    def readBrushDefinitionSetting(self, key):
        brushDef = None
        for param in self.xml.documentElement.getElementsByTagName('param'):
            if param.getAttribute('name') == 'brush_definition':
                brushDef = param
        if brushDef is None:
            return
        brush = miniDOM.parseString(brushDef.firstChild.data).documentElement
        return brush.getAttribute(key)

    def setBrushDefinitionSetting(self, key, value, type=None, isMasked=False):
        if key != 'type':
            if type is None:
                type = self.readBrushDefinitionSetting('type')
            if type is None or type == '': # ?
                print("please set a brush definition with a type first")
                type = BrushTipType.Predefined
        if key in self.engine.brushDefinition['Brush']:
            if key == 'type':
                print("Switching brushtip type...")
            self.setBrushDefinitionImpl(key, value, self.engine.brushDefinition['Brush'][key]['type'], False, isMasked)
            #print(f"set brush_definition {key} to {value}")
        elif key in self.engine.brushDefinition[type]:
            self.setBrushDefinitionImpl(key, value, self.engine.brushDefinition[type][key]['type'], False, isMasked)
            #print(f"set brush_definition {key} to {value}")
        elif type == BrushTipType.Auto and key in self.engine.brushDefinition['MaskGenerator']:
            self.setBrushDefinitionImpl(key, value, self.engine.brushDefinition['MaskGenerator'][key]['type'], True, isMasked)
            #print(f"set brush_definition maskgen {key} to {value}")
        else:
            print(f"Unknown {type} Brush setting {key}")

    def setMaskedBrushDefinitionSetting(self, key, value, type=None):
        self.setBrushDefinitionSetting(key, value, type, isMasked=True)

    def setBrushDefinitionImpl(self, key, value, type=False, inMaskGen=False, isMasked=False):
        value = self.validateType(key, value, type)

        brushDef = None
        if isMasked:
            for param in self.xml.documentElement.getElementsByTagName('param'):
                if param.getAttribute('name') == 'MaskingBrush/Preset/brush_definition':
                    brushDef = param
            if brushDef is None:
                brushDef = self.xml.createElement('param')
                brushDef.setAttribute('name', 'MaskingBrush/Preset/brush_definition')
                self.xml.documentElement.appendChild(brushDef)
        else:
            for param in self.xml.documentElement.getElementsByTagName('param'):
                if param.getAttribute('name') == 'brush_definition':
                    brushDef = param
            if brushDef is None:
                brushDef = self.xml.createElement('param')
                brushDef.setAttribute('name', 'brush_definition')
                self.xml.documentElement.appendChild(brushDef)

        brush = None
        if brushDef.hasChildNodes():
            brush = miniDOM.parseString(brushDef.firstChild.data).documentElement
        else:
            brush = self.xml.createElement('Brush')

        if inMaskGen:
            if brush.hasChildNodes():
                maskGen = brush.firstChild
                if maskGen.__class__  != miniDOM.Element: # " "
                    maskGen = brush.childNodes[1]
            else:
                maskGen = self.xml.createElement('MaskGenerator')
            print(f"set brush_definition MaskGenerator {key} to {value}")
            maskGen.setAttribute(key, value)
            if brush.hasChildNodes():
                brush.replaceChild(maskGen, brush.firstChild)
            else:
                brush.appendChild(maskGen)
        else:
            print(f"set brush_definition {key} to {value}")
            brush.setAttribute(key, value)

        if brushDef.hasChildNodes():
            brushDef.replaceChild(self.xml.createTextNode(brush.toxml()), brushDef.firstChild)
        else:
            brushDef.appendChild(self.xml.createTextNode(brush.toxml()))

    def validateType(self, key, value, type):
        if type and value.__class__ is not type:
            print(f"Warning: {value} is not {type} expected by {key} (expected type may be wrong)")
        if issubclass(type, IntEnum):
            value = int(value) # don't make it a string
        # Write everything as a string
        value = str(value)
        return value

    def makeChildSensor(self, inputKey, curve):
        newSensor = self.xml.createElement('ChildSensor')
        newSensor.setAttribute('id', inputKey)
        newSensor.appendChild(self.makeCurveElem(curve))
        return newSensor
    def makeCurveElem(self, curve):
        curveElem = self.xml.createElement('curve')
        curveElem.appendChild(self.xml.createTextNode(curve))
        return curveElem
    
    def validateCurve(self, curve):
        print("Validating curve", curve)
        # 0.0,0.0;1.0,1.0;
        points = curve.split(";")
        nonZeroY = 0
        for pt in points:
            if pt == "": # after the last semicolon
                continue
            xy = pt.split(",")
            if float(xy[1]) > 0:
                nonZeroY += 1
        if nonZeroY == 0:
            print("  Curve is 0! Don't enable it")
            return False
        
        return True

    def setSensor(self, sensorKey, inputKey, curve):
        if not self.validateCurve(curve):
            return

        sensorParam = None
        for param in self.xml.getElementsByTagName('param'):
            if param.getAttribute('name') == sensorKey:
                sensorParam = param
                break

        if sensorParam is None:
            sensorParam = self.xml.createElement('param')
            sensorParam.setAttribute('name', sensorKey)

        sensorParams = None
        if sensorParam.hasChildNodes():
            sensorParams = sensorParam.firstChild
            if sensorParams.__class__ != miniDOM.Element:
                sensorParams = miniDOM.parseString(param.firstChild.data).documentElement
        else:
            sensorParams = self.xml.createElement('params')
            sensorParams.setAttribute('id', inputKey)

        if sensorParams.getAttribute('id') == 'sensorslist':
            foundInputSensor = False
            for inputParam in sensorParams.getElementsByTagName('ChildSensor'):
                if inputParam.getAttribute('id') == inputKey:
                    foundInputSensor = True
                    curveParam = self.makeCurveElem(curve)
                    if inputParam.hasChildNodes():
                        inputParam.replaceChild(curveParam, inputParam.firstChild)
                        print(f"sensorslist {sensorKey}: set {inputKey} to {curve}")
                    else:
                        inputParam.appendChild(curveParam)
                        print(f"sensorslist {sensorKey}: add {inputKey} to {curve}")
                    break
                if not foundInputSensor:
                    sensorParams.appendChild(self.makeChildSensor(inputKey, curve))
        else: # not sensorsList
            if sensorParams.getAttribute('id') == inputKey:
                # set the curve
                curveParam = self.makeCurveElem(curve)
                if sensorParams.hasChildNodes():
                    sensorParams.replaceChild(curveParam, sensorParams.firstChild)
                    print(f"sensor {sensorKey}: set {inputKey} to {curve}")
                else:
                    sensorParams.appendChild(curveParam)
                    print(f"sensor {sensorKey}: add {inputKey} to {curve}")
            else:
                # make a sensorsList
                sensorsListParams = self.xml.createElement('params')
                sensorsListParams.setAttribute('id', 'sensorslist')

                oldSensorParams = self.xml.createElement('ChildSensor')
                for key in sensorParams.attributes.keys():
                    oldSensorParams.setAttribute(key, sensorParams.getAttribute(key))
                if sensorParams.hasChildNodes():
                    oldSensorParams.appendChild(sensorParams.firstChild)
                sensorsListParams.appendChild(oldSensorParams)

                childParam = self.makeChildSensor(inputKey, curve)
                sensorsListParams.appendChild(childParam)
                print(f"sensorslist added, {sensorKey}: set {inputKey} to {curve}")

                sensorParams = sensorsListParams

        sensorParams = self.xml.createCDATASection("<!DOCTYPE params>"+sensorParams.toxml())
        if sensorParam.hasChildNodes():
            sensorParam.replaceChild(sensorParams, sensorParam.firstChild)
        else:
            sensorParam.appendChild(sensorParams)

        #print("sensorParams", sensorParams.toxml())
        #print("sensorParam", sensorParam.toxml())


    def setSensorDrawingAngle(self, sensorKey, inputKey, curve, fanCornersEnabled, fanCornersStep, angleOffset, lockedAngleMode):
        print("setSensorDrawingAngle is not yet implemented!")

    def setSensorFade(self, sensorKey, inputKey, curve, periodic, length):
        if not self.validateCurve(curve):
            return

        sensorParam = None
        for param in self.xml.getElementsByTagName('param'):
            if param.getAttribute('name') == sensorKey:
                sensorParam = param
                break

        if sensorParam is None:
            sensorParam = self.xml.createElement('param')
            sensorParam.setAttribute('name', sensorKey)

        sensorParams = self.xml.createElement('params')
        sensorParams.setAttribute('id', inputKey)
        sensorParams.setAttribute('length', str(int(length)))
        sensorParams.setAttribute('periodic', '1' if periodic else '0')
        sensorParams.appendChild(self.makeCurveElem(curve))

        sensorParams = self.xml.createCDATASection("<!DOCTYPE params>" + sensorParams.toxml())
        if sensorParam.hasChildNodes():
            sensorParam.replaceChild(sensorParams, sensorParam.firstChild)
        else:
            sensorParam.appendChild(sensorParams)

        self.xml.documentElement.appendChild(sensorParam)

    def setSensorDistance(self, sensorKey, inputKey, curve, periodic, length):
        print("setSensorDistance is not yet implemented!")

    def setSensorTime(self, sensorKey, inputKey, curve, periodic, duration):
        print("setSensorTime is not yet implemented!")

    def setCurve(self, key, value):
        print("setCurve is not yet implemented!")


if __name__ == "__main__":
    main()

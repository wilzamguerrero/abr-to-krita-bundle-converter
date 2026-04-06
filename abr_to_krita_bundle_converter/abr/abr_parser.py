#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import struct
import pprint
import uuid
import zlib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".abr file path",
                        type=str)
    parser.add_argument("--dump_path", help="dump output file path",
                    type=str)
    parser.add_argument("--dump_images_path", help="dump images output file path",
                    type=str)
    args = parser.parse_args()

    path = args.file_path
    dumpPath = args.dump_path
    dumpImagesPath = args.dump_images_path

    if path.endswith('.abr'):
        parser = ABRBrushParser(path, dumpImagesPath=dumpImagesPath)
        parser.loadABR(path)

        if dumpPath:
            parser.dumpDesc(dumpPath)


class ABRBrushParser:
    def __init__(self, path, name="", dumpImagesPath=""):
        self.path = path
        self.name = name
        self.dumpImagesPath = dumpImagesPath

        self.fileHandle = None
        self.version = None
        self.subversion = None
        self.blockInfos = {}

        self.desc = {}

        self.brushtipSizes = {"": [32,32]}
        self.brushtipNames = {}

    # Read over the entire file at once
    def loadABR(self, path):
        with open(path, 'rb') as f:
            self.version =  struct.unpack(">h", f.read(2))[0]
            self.subversion =  struct.unpack(">h", f.read(2))[0]
            print(f"version {self.version} subversion {self.subversion}")

            found_preset_data = False
            while buf := f.read(4):
                if buf != b'8BIM':
                    print(f"Error: Couldn't find 8BIM!: {path}")
                    return False
                chunk_id = f.read(4).decode()
                chunk_data_len = struct.unpack(">i", f.read(4))[0]
                if chunk_data_len % 2 == 1:
                    chunk_data_len += 1
                if chunk_id == 'samp':
                    self.readSamp(f, f.seek(0, 1)+chunk_data_len)
                elif chunk_id == 'patt':
                    self.readPatt(f, f.seek(0, 1)+chunk_data_len)
                elif chunk_id == 'desc':
                    found_preset_data = True
                    self.readDesc(f, f.seek(0, 1)+chunk_data_len)
                elif chunk_id == 'phry':
                    # Ignore the mystery 'phry' chunk
                    f.seek(chunk_data_len, 1)
                else:
                    print(f"Found unknown block {chunk_id}! Skipping.")
                    f.seek(chunk_data_len, 1)

            if not found_preset_data:
                print(f"Error: Found no preset metadata chunk.: {self.path}")
                return False

    # Open the file and get the block info
    # Please close the file afterward...
    def openFile(self):
        self.fileHandle = open(self.path, 'rb')

        f = self.fileHandle

        buf = f.read(2)
        if len(buf) < 2:
            raise RuntimeError(f"File too small to be a valid ABR: {self.path}")
        self.version = struct.unpack(">h", buf)[0]

        buf = f.read(2)
        if len(buf) < 2:
            raise RuntimeError(f"File too small to be a valid ABR: {self.path}")
        self.subversion = struct.unpack(">h", buf)[0]

        if self.version < 6:
            self.closeFile()
            raise RuntimeError(
                f"ABR version {self.version} is not supported. "
                f"Only ABR version 6+ (Photoshop CS and later) are supported.")

        while True:
            buf = f.read(4)
            if len(buf) < 4:
                break  # end of file
            if buf != b'8BIM':
                self.closeFile()
                raise RuntimeError(
                    f"Invalid ABR file: expected '8BIM' marker but found {buf!r} at offset {f.seek(0, 1) - 4}")

            buf = f.read(4)
            if len(buf) < 4:
                break
            chunk_id = buf.decode('ascii', errors='replace')

            buf = f.read(4)
            if len(buf) < 4:
                break
            chunk_data_len = struct.unpack(">i", buf)[0]
            if chunk_data_len % 2 == 1:
                chunk_data_len += 1

            self.blockInfos[chunk_id] = {'pos': f.seek(0, 1), 'len': chunk_data_len}

            f.seek(chunk_data_len, 1)

    def closeFile(self):
        self.fileHandle.close()

    def gotoBlock(self, block):
        f = self.fileHandle

        blockInfo = self.blockInfos.get(block)
        if not blockInfo:
            print(f"Error: Found no {block} chunk.: {self.path}")
            return 0

        f.seek(blockInfo['pos'])

        # Return the end position
        return blockInfo['pos'] + blockInfo['len']


    def readDesc(self, f, endPos):
        # Todo: ???
        buf = f.read(4) # 16
        #print(int.from_bytes(buf, 'big'))
        buf = f.read(4) # 1
        #print(int.from_bytes(buf, 'big'))
        buf = f.read(4) # 0
        #print(int.from_bytes(buf, 'big'))
        buf = f.read(2) # 0
        #print(int.from_bytes(buf, 'big'))
        buf = f.read(4) # null
        #print(buf)
        buf = f.read(4) # 1
        #print(int.from_bytes(buf, 'big'))
        buf = f.read(4) # 0


        buf = f.read(4) # Brsh
        if buf != b'Brsh':
            print("Expected 'Brsh'!")
            return False
        buf = f.read(4) # VlLs
        if buf != b'VlLs':
            print("Expected 'VlLs'!")
            return False
        self.desc['Brsh'] = self.readVlLs(f)

        self.verifyBytesRead(f, endPos, 'desc')

        self.getBrushtipNames()

    def verifyBytesRead(self, f, endPos, chunk_id):
        bytesLeft = endPos - f.seek(0, 1)
        if bytesLeft:
            if bytesLeft == 1:
                f.seek(1, 1) # Read the pad byte
            else:
                print(f"Error: Did not read remaining {bytesLeft} bytes in {chunk_id} block (at {f.seek(0,1)})")

    def getBrushtipNames(self):
        # get the brushtip names to associate with their uuids
        for i in range(len(self.desc['Brsh'])):
            try:
                brushtip = self.desc['Brsh'][i]['Objc']['brushPreset'][1]['Brsh']
                brushtip = brushtip['Objc']
                if 'sampledBrush' in brushtip.keys():
                    sampledBrush = brushtip['sampledBrush']
                    # Find sampledData and Nm entries by key name instead of hardcoded index
                    brushUuid = None
                    brushName = None
                    for entry in sampledBrush:
                        if 'sampledData' in entry:
                            brushUuid = entry['sampledData']['TEXT']
                        elif 'Nm  ' in entry:
                            brushName = entry['Nm  ']['TEXT']
                    if brushUuid and brushName:
                        self.brushtipNames[brushUuid] = brushName
            except (KeyError, IndexError, TypeError) as e:
                print(f"Warning: Could not get brushtip name for brush {i}: {e}")
                continue

    def dumpDesc(self, dumpPath):
        with open(dumpPath, 'w', encoding='utf_8') as f:
            #print(self.desc, file = f)
            #pprint.pp(self.desc, stream = f, width=180)

            # Pretty print the dictionary, but
            # manually print out the Brsh and Objc/brushPreset parts,
            # so that they don't cause huge leading indentation
            print("{'Brsh': ", file=f)
            for child in self.desc['Brsh']:
                print("[{'Objc': {'brushPreset': ", file=f)
                pprint.pp(child['Objc']['brushPreset'], stream=f)
                print("} } ]", file=f)
            print("}", file=f)



    def readVlLs(self, f):
        vlls = []

        numChildren = struct.unpack(">i", f.read(4))[0]
        for _ in range(numChildren):
            type = f.read(4).decode()

            match type:
                case 'Objc':
                    value = self.readObjc(f)

                case 'TEXT':
                    value = self.readTEXT(f)

                case 'UntF':
                    value = self.readUntF(f)

                case 'bool':
                    value = self.readBool(f)

                case 'long':
                    value = self.readLong(f)

                case 'enum':
                    value = self.readEnum(f)

                case 'doub':
                    value = self.readDoub(f)

                case 'tdta':
                    value = self.readTdta(f)

                case 'VlLs':
                    value = self.readVlLs(f)

                case _ :
                    print(f"unknown type in VlLs: {type}")
                    break

            vlls.append({type: value})

        return vlls

    def readObjc(self, f):
        objc = {}

        name = self.readPaddedVariableLenString(f)
        className = self.readVariableLenString(f)
        objc[className] = []
        numChildren = struct.unpack(">i", f.read(4))[0]
        for _ in range(numChildren):
            name = self.readVariableLenString(f)

            type = f.read(4).decode()
            match type:
                case 'TEXT':
                    value = self.readTEXT(f)

                case 'Objc':
                    value = self.readObjc(f)
                
                case 'UntF':
                    value = self.readUntF(f)
                
                case 'bool':
                    value = self.readBool(f)

                case 'long':
                    value = self.readLong(f)

                case 'enum':
                    value = self.readEnum(f)

                case 'doub':
                    value = self.readDoub(f)

                case 'tdta':
                    value = self.readTdta(f)

                case 'VlLs':
                    value = self.readVlLs(f)

                case _ :
                    print(f"unknown type in Objc: {type}")
                    return False

            objc[className].append({name: {type: value}})

        return objc

    def readTEXT(self, f):
        textCharLen = struct.unpack(">i", f.read(4))[0]
        textLen = textCharLen * 2
        text = f.read(textLen).decode(encoding='utf_16_be', errors='replace').rstrip('\0')
        return text

    def readTdta(self, f):
        dataLen = struct.unpack(">i", f.read(4))[0]
        data = f.read(dataLen)
        return data
    
    def readUntF(self, f):
        unit = f.read(4).decode()
        value = struct.unpack(">d", f.read(8))[0]
        return [unit, value]

    def readBool(self, f):
        value = struct.unpack("?", f.read(1))[0]
        return value

    def readVariableLenString(self, f):
        textLen = struct.unpack(">i", f.read(4))[0]
        if textLen == 0:
            textLen = 4 # fourCC
        text = f.read(textLen).decode()
        return text

    def readPaddedVariableLenString(self, f):
        textLen = struct.unpack(">i", f.read(4))[0]
        if textLen % 2 == 1:
            textLen += 1
        if textLen == 0:
            textLen = 4 # fourCC
        text = f.read(textLen).decode()
        return text
    
    def readLong(self, f):
        value = struct.unpack(">l", f.read(4))[0]
        return value
    
    def readEnum(self, f):
        enum = self.readVariableLenString(f)
        value = self.readVariableLenString(f)
        return [enum, value]

    def readDoub(self, f):
        value = struct.unpack(">d", f.read(8))[0]
        return value

    def readSamp(self, f, endPos):
        while f.seek(0, 1) < endPos:
            self.readBrushtip(f)

        self.verifyBytesRead(f, endPos, 'samp')

    def readBrushtip(self, f, returnImage=False, invert=False):
        lenBrushtip = struct.unpack(">i", f.read(4))[0]
        #print("lenBrushtip:", lenBrushtip)
        startPos = f.seek(0,1)
        #print("startPos:", startPos)
        # check if the uuid is valid, otherwise something's wrong
        brushUuid = uuid.UUID(self.readPOSIXString(f))
        #print("uuid", brushUuid)

        if self.subversion != 1:
            buf = struct.unpack(">h", f.read(2))[0] # 1
            buf = struct.unpack(">i", f.read(4))[0] # 0
            buf = struct.unpack(">h", f.read(2))[0] # 3

            lenBrushtipMinus49 = struct.unpack(">i", f.read(4))[0]

            # top left bottom right
            buf = struct.unpack(">i", f.read(4))[0]
            buf = struct.unpack(">i", f.read(4))[0]
            buf = struct.unpack(">i", f.read(4))[0]
            buf = struct.unpack(">i", f.read(4))[0]

            lenEmpty = struct.unpack(">i", f.read(4))[0]
            for _ in range(lenEmpty-1):
                buf = struct.unpack(">i", f.read(4))[0] # 0
            buf = struct.unpack(">i", f.read(4))[0] # 1

            lenBrushtipMinus49Minus256 = struct.unpack(">i", f.read(4))[0]

            buf = struct.unpack(">i", f.read(4))[0] # 8
        else: # if subversion 1
            # top left bottom right
            buf = struct.unpack(">h", f.read(2))[0]
            buf = struct.unpack(">h", f.read(2))[0]
            buf = struct.unpack(">h", f.read(2))[0]
            buf = struct.unpack(">h", f.read(2))[0]
            # Unknown
            buf = struct.unpack(">h", f.read(2))[0]

        top = struct.unpack(">i", f.read(4))[0]
        left = struct.unpack(">i", f.read(4))[0]
        bottom = struct.unpack(">i", f.read(4))[0]
        right = struct.unpack(">i", f.read(4))[0]

        width = right-left
        height = bottom-top

        self.brushtipSizes[str(brushUuid)] = [width, height]

        #print("width, height", width, height)

        depth = struct.unpack(">h", f.read(2))[0]
        #print("depth:", depth)
        compression = struct.unpack(">b", f.read(1))[0]
        #print("compression:", compression)

        imgData = self.readImageData(f, compression, depth, width, height, invert)

        f.read(8) # 0 ???

        currentPos = f.seek(0,1)
        bytesRead = currentPos - startPos
        if bytesRead != lenBrushtip:
            print(f"Error: Expected {lenBrushtip - bytesRead} more bytes in brushtip (at {currentPos})")

        # Padded to 4 bytes??
        if currentPos % 4 != 0:
            padding = 4 - currentPos % 4
            f.read(padding)

        name = self.brushtipNames.get(str(brushUuid))
        if name is not None:
            name.replace("/", "_")
        else:
            name = brushUuid
        #print("brushtip name:", name, "uuid:", brushUuid)

        if self.dumpImagesPath:
            #self.dumpImageTga(imgData, brushUuid, width, height)
            self.dumpImage(imgData, name, width, height)

        if returnImage:
            return [self.imageToPNGData(imgData, width, height), name, str(brushUuid)]

    def readImageData(self, f, compression, depth, width, height, invert):
        imgData = []

        if depth != 8:
            print("Found bitdepth other than 8, please implement it")

        if compression == 1: # RLE
            rowLens = []
            for _ in range(height):
                lenRow = struct.unpack(">h", f.read(2))[0]
                rowLens.append(lenRow)

            for rowLen in rowLens:
                rowData = bytearray()
                while rowLen > 0:
                    buf = f.read(1)
                    amount = struct.unpack(">b", buf)[0]
                    rowLen -= 1
                    if amount == -128: # just continue
                        continue
                    if amount < 0: # uncompress run ('backward')
                        byte = f.read(1)
                        if invert:
                            byte = (byte[0] ^ 0xff).to_bytes(1, 'big')
                        rowData += byte * (-amount+1)
                        rowLen -= 1
                    else: # read ('forward')
                        for _ in range(amount+1):
                            byte = f.read(1)
                            if invert:
                                byte = (byte[0] ^ 0xff).to_bytes(1, 'big')
                            rowData += byte
                            rowLen -= 1
                imgData.append(rowData)
        else: # uncompressed
            #imgData = f.read(width*height)
            for _ in range(height):
                bytes = f.read(width)
                if invert:
                    bytes = bytearray(bytes)
                    for i in range(len(bytes)):
                        bytes[i] = bytes[i] ^ 0xff
                imgData.append(bytes)

        #print(f"found {len(imgData)} bytes of data out of {width*height}")

        return imgData


    def dumpImageTga(self, imgData, brushUuid, width, height):
        with open(self.dumpImagesPath+str(brushUuid)+".tga", 'wb') as f:
            f.write(struct.pack("<b", 0)) # ID length
            f.write(struct.pack("<b", 0)) # color map type
            f.write(struct.pack("<b", 3)) # image type (grayscale)
            # color map spec
            f.write(struct.pack("<h", 0)) # first index
            f.write(struct.pack("<h", 0)) # num indices
            f.write(struct.pack("<b", 0)) # size index
            # image map spec
            f.write(struct.pack("<h", 0)) # x-origin (lower left)
            f.write(struct.pack("<h", 0)) # y-origin
            f.write(struct.pack("<h", width))
            f.write(struct.pack("<h", height))
            f.write(struct.pack("<b", 8)) # depth (1byte) fixme if other depths are supported
            f.write(struct.pack("<b", 0 | 0b00100000)) # image descriptor; 5th bit, top-to-bottom

            #f.write(imgData)
            for row in imgData:
                f.write(row)

    def dumpImage(self, imgData, name, width, height):
        with open(self.dumpImagesPath+str(name)+".png", 'wb') as f:
            #self.dumpImgAsPNG(imgData, f, width, height)
            f.write(self.imageToPNGData(imgData, width, height))

    #def dumpImgAsPNG(self, imgData, f, width, height):
    def imageToPNGData(self, imgData, width, height):
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
        data += (chksum.to_bytes(4, 'big'))

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
        data += (chksum.to_bytes(4, 'big'))

        # Image End
        data += (b"\0\0\0\0" + b"IEND" + b"\xae\x42\x60\x82")

        return data

    def readPOSIXString(self, f):
        textLen = struct.unpack(">b", f.read(1))[0]
        text = f.read(textLen).decode()
        return text

    def readPatt(self, f, endPos, invert=False):
        while f.seek(0, 1) < endPos:
            self.readPattern(f, invert)

        self.verifyBytesRead(f, endPos, 'patt')

    def readPattern(self, f, invert=False, returnImage=False):
        images = []

        lenPattern = struct.unpack(">i", f.read(4))[0]

        startPos = f.seek(0,1)
        buf = struct.unpack(">i", f.read(4))[0] # 1
        numPatterns = struct.unpack(">i", f.read(4))[0] # 3 or 1. num subpatterns
        buf = struct.unpack(">h", f.read(2))[0] # w?
        buf = struct.unpack(">h", f.read(2))[0] # h?

        name = self.readTEXT(f)
        #print(name)

        pattUuid = uuid.UUID(self.readPOSIXString(f))
        #print(pattUuid)

        buf = struct.unpack(">i", f.read(4))[0] # 3
        lenPatternMinusPrevious = struct.unpack(">i", f.read(4))[0]
        buf = struct.unpack(">i", f.read(4))[0] # 0
        buf = struct.unpack(">i", f.read(4))[0] # 0
        buf = struct.unpack(">i", f.read(4))[0] # w?
        buf = struct.unpack(">i", f.read(4))[0] # h?
        buf = struct.unpack(">i", f.read(4))[0] # 24

        for i in range(numPatterns):
            #images.append(self.readSubPattern(f, i, pattUuid, invert, returnImage))
            images.append(self.readSubPattern(f, i, name, str(pattUuid), invert, returnImage))

        f.read(92) # ???

        currentPos = f.seek(0,1)
        bytesRead = currentPos - startPos
        bytesLeft = lenPattern - bytesRead

        if (bytesLeft) == 8:
            # on version 10?
            f.read(8)
            currentPos = f.seek(0,1)
            bytesRead = currentPos - startPos
            bytesLeft = lenPattern - bytesRead

        if bytesRead != lenPattern:
            print(f"Error: Expected {bytesLeft} more bytes in pattern (at {currentPos})")

            print("(reading the missing bytes)")
            f.read(bytesLeft) # ???

        # Padded to 4 bytes??
        if currentPos % 4 != 0:
            padding = 4 - currentPos % 4
            f.read(padding)


        if returnImage:
            return images


    def readSubPattern(self, f, i, filename, patternUuid, invert=False, returnImage=False):
        buf = struct.unpack(">i", f.read(4))[0] # 1

        sizePlusHeader = struct.unpack(">i", f.read(4))[0] # w*h + 23 (the following)
        #print(sizePlusHeader)
        buf = struct.unpack(">i", f.read(4))[0] # 8
        top = struct.unpack(">i", f.read(4))[0] # 0
        left = struct.unpack(">i", f.read(4))[0] # 0
        bottom = struct.unpack(">i", f.read(4))[0] # w?
        right = struct.unpack(">i", f.read(4))[0] # h?

        width = right-left
        height = bottom-top

        #print("width, height", width, height)

        depth = struct.unpack(">h", f.read(2))[0] # 8
        compression = struct.unpack(">b", f.read(1))[0] # 0

        imgData = self.readImageData(f, compression, depth, width, height, invert)

        filename = filename.replace("/", "_")
        if i > 0:
            filename = f"{filename} {i}"
        if self.dumpImagesPath:
            self.dumpImage(imgData, filename, width, height)

        if returnImage:
            return [self.imageToPNGData(imgData, width, height), filename, patternUuid]

            
        
if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from zipfile import ZipFile
import plistlib
import re
import os.path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".brush file path",
                        type=str)
    parser.add_argument("--dump_plist", help="plist dump output file path",
                    type=str)
    parser.add_argument("--setting", help="setting key to print the value of",
                    type=str)
    parser.add_argument("--setting_curve", help="setting key to print the curve value of",
                    type=str)
    args = parser.parse_args()

    path = args.file_path
    dumpPlistPath = args.dump_plist
    setting = args.setting
    setting_curve = args.setting_curve

    if path.endswith('.brush'):
        parser = ProcreateBrushParser(path)
        if dumpPlistPath:
            parser.dumpPlist(dumpPlistPath)
        if setting:
            print(parser.loadSetting(setting))
        if setting_curve:
            print(parser.getCurvePoints(setting_curve))

        subParser = ProcreateBrushParser(path, "/Sub01")
        if subParser.plist is not None:
            if dumpPlistPath:
                parser.dumpPlist(dumpPlistPath+".Sub01") # not great

    elif path.endswith('.brushset'):
        names = ProcreateBrushSetParser().findBrushPaths(path)
        for name in names:
            parser = ProcreateBrushParser(path, name)
            if dumpPlistPath:
                parser.dumpPlist(os.path.join(dumpPlistPath,f"{name}.txt"))
            if setting or setting_curve:
                print(parser.loadSetting('name'))
            if setting:
                print(parser.loadSetting(setting))
            if setting_curve:
                print(parser.getCurvePoints(setting_curve))

            subParser = ProcreateBrushParser(path, name+"/Sub01")
            if subParser.plist is not None:
                if dumpPlistPath:
                    subParser.dumpPlist(os.path.join(dumpPlistPath,f"{name}-Sub01.txt"))


class ProcreateBrushSetParser:
    def __init__(self):
        pass
    def findBrushPaths(self, path):
        with ZipFile(path) as brushSetFile:
            with brushSetFile.open('brushset.plist') as brushArchive:
                plist = plistlib.load(brushArchive)
                return plist['brushes']


class ProcreateBrushParser:
    def __init__(self, path, name=""):
        self.prefix = name + "/" if name else "" # inside the Zip it's "/", hopefully?
        self.plist = self.loadPlist(path, name)
        self.path = path
        self.name = name

    def loadPlist(self, path, name):
        with ZipFile(path) as brushFile:
            try:
                brushFileInfo = brushFile.getinfo(self.prefix+"Brush.archive")
            except:
                return None
            with brushFile.open(brushFileInfo) as brushArchive:
                return plistlib.load(brushArchive)

    def dumpPlist(self, outpath):
        with open(outpath, 'w') as f:
            formattedText = re.sub(", ", ", \n", str(self.plist))
            print(formattedText, file = f)

    def loadSetting(self, key):
        try:
            value = self.plist["$objects"][1][key]
        except KeyError:
            print(f"warning: loadSetting: '{key}' not found")
            return 0
        if value.__class__ == plistlib.UID:
            value = self.getUID(value.data)
        return value

    def getUID(self, id):
        return self.plist["$objects"][id]
    
    def getCurvePoints(self, key):
        list = []
        value = self.plist["$objects"][1][key]
        if value.__class__ == plistlib.UID:
            value = self.getUID(value.data)
            points = value['points']
            if points.__class__ == plistlib.UID:
                arrayObj = self.getUID(points.data)
                array = arrayObj['NS.objects']
                for val in array:
                    if val.__class__ == plistlib.UID:
                        val = self.getUID(val.data)
                        list.append(val)
        return list
    
    def loadResource(self, filename, strip=False):
        print(self.path)
        filename = self.prefix+filename
        buf = b""
        with ZipFile(self.path) as brushFile:
            if not filename in brushFile.namelist():
                print(f"Warning: Couldn't open resource file {filename}")
                return buf
            brushFileInfo = brushFile.getinfo(filename)
            with brushFile.open(brushFileInfo, 'r') as f:
                buf = f.read() #all
                if strip:
                    buf = self.stripPNG(buf)
        
        return buf
    
    # this isn't really necessary but whatever
    def stripPNG(self, data):
        # we could just get the IHDR/IDAT/IEND,
        # but mostly we just want to strip the iTXt
        before, sep, after = data.partition(b'iTXt')
        if sep:
            iTXtLen = int.from_bytes(before[-4:], byteorder='big')
            # get rid of the len(4), the data(len), and the crc(4)
            return before[:-4] + after[iTXtLen+4:]

        return data
        
if __name__ == "__main__":
    main()

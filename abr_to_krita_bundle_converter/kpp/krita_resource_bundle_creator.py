#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later


import argparse
from zipfile import ZipFile
import os.path
from datetime import date
import hashlib
import platform

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("resources_path", help="path to folder containing resources",
                        type=str)
    parser.add_argument("bundle_path", help="path to write the output bundle file to",
                        type=str)
    parser.add_argument("--desc", help="bundle description text",
                    type=str)
    args = parser.parse_args()

    resourcesPath = args.resources_path
    bundlePath = args.bundle_path
    desc = args.desc

    bundleCreator = KritaResourceBundleCreator(bundlePath)
    bundleCreator.createZip()
    bundleCreator.setDesc(desc)
    bundleCreator.addResourcesFromFolder(resourcesPath)
    bundleCreator.finishZip()


class KritaResourceBundleCreator:
    def __init__(self, bundlePath):
        self.bundlePath = bundlePath

        # List of (resType, fileName, md5sum) in order added
        self.resourceEntries = []

        self.desc = ""

        # (type, fileName) -> [tag_name, ...]
        self.resourceTags = {}

    def setDesc(self, desc):
        self.desc = desc

    def createZip(self):
        with ZipFile(self.bundlePath, 'w') as bundleZip:
            bundleName = os.path.basename(self.bundlePath)

            bundleZip.writestr("mimetype", "application/x-krita-resourcebundle")

            # date.today() is not formatted the expected way, but oh well, this is lazy
            metaXML =f"""<?xml version="1.0" encoding="UTF-8"?>
<meta:meta xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:dc="http://purl.org/dc/elements/1.1">
 <meta:generator>krita_resource_bundle_creator.py</meta:generator>
 <meta:bundle-version>1</meta:bundle-version>
 <dc:author></dc:author>
 <dc:title>{bundleName}</dc:title>
 <dc:description>{self.desc}</dc:description>
 <meta:initial-creator></meta:initial-creator>
 <dc:creator></dc:creator>
 <meta:creation-date>{date.today()}</meta:creation-date>
 <meta:dc-date>{date.today()}</meta:dc-date>
 <meta:email></meta:email>
 <meta:license></meta:license>
 <meta:website></meta:website>
 <meta:meta-userdefined meta:name="email" meta:value=""/>
 <meta:meta-userdefined meta:name="license" meta:value=""/>
 <meta:meta-userdefined meta:name="website" meta:value=""/>
</meta:meta>
"""
            bundleZip.writestr("meta.xml", metaXML)

            # Dummy preview image so Krita doesn't complain about it missing;
            # 2x2 red
            bundleImg = b"\x89PNG\r\n\x1a\n" + \
                        b"\0\0\0\x0d" + b"IHDR" + b"\0\0\0\2" + b"\0\0\0\2" + b"\x08" + b"\x02" + b"\0" + b"\0" + b"\0" + b"\xfd\xd4\x9a\x73" \
                        b"\0\0\0\x10" + b"IDAT" + b"\x08" + b"\xd7" + b"\x63\xFC\xCF\x00\x02\x4C\x60\x92\x01\x00"+ b"\x0D\x1D\x01\x03" + b"\x49\xA0\x1F\x65" \
                        b"\0\0\0\0" + b"IEND" + b"\xae\x42\x60\x82"
            bundleZip.writestr("preview.png", bundleImg)

    # finishZip() must be called to write the manifest.xml after adding everything,
    # because we are too lazy to do it properly
    def finishZip(self):
        with ZipFile(self.bundlePath, 'a') as bundleZip:
            manifestXML = """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">"""
            for resType, fileName, md5sum in self.resourceEntries:
                key = (resType, fileName)
                tags = self.resourceTags.get(key, [])
                if tags:
                    manifestXML += f'\n <manifest:file-entry manifest:media-type="{resType}" manifest:full-path="{resType}/{fileName}" manifest:md5sum="{md5sum}">'
                    manifestXML += '\n  <manifest:tags>'
                    for t in tags:
                        manifestXML += f'\n   <manifest:tag>{t}</manifest:tag>'
                    manifestXML += '\n  </manifest:tags>'
                    manifestXML += '\n </manifest:file-entry>'
                else:
                    manifestXML += f'\n <manifest:file-entry manifest:media-type="{resType}" manifest:full-path="{resType}/{fileName}" manifest:md5sum="{md5sum}"/>'
            manifestXML += "\n</manifest:manifest>\n"
            bundleZip.writestr("META-INF/manifest.xml", manifestXML)

    def addTag(self, tagName, resourceType, fileName):
        key = (resourceType, fileName)
        if key not in self.resourceTags:
            self.resourceTags[key] = []
        if tagName not in self.resourceTags[key]:
            self.resourceTags[key].append(tagName)

    def addResourcesFromFolder(self, resourcesPath):
        for rootPath, dirs, files in os.walk(resourcesPath):
                for fileName in files:
                    type = ""
                    if fileName.endswith(('.kpp')):
                        type = "paintoppresets"
                    # todo: whatever other types that can be determined from filetype...
                    # and for other types, use a folder structure to determine type

                    if type != "":
                        filePath = os.path.join(rootPath, fileName)
                        self.addResourceFromPath(filePath, type)

    def addResourceFromPath(self, filePath, type):
        print("addResourceFromPath", filePath, type)
        with ZipFile(self.bundlePath, 'a') as bundleZip:
            md5sum = ""
            with open(filePath, "rb") as f:
                major, minor, point = platform.python_version_tuple()
                if (int(major) > 3 or int(major) == 3 and int(minor) >= 11):
                    digest = hashlib.file_digest(f, "md5") # added in python3.11...
                    md5sum = digest.hexdigest()
                else:
                    md5sum = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
            fileName = os.path.basename(filePath)
            bundleZip.write(filePath, f"{type}/{fileName}")
            self.resourceEntries.append((type, fileName, md5sum))

    def addResourceFromData(self, data, type, fileName, md5sum=None):
        if md5sum == None:
            md5sum = hashlib.md5(data, usedforsecurity=False).hexdigest()
        print("addResourceFromData", type, fileName)
        with ZipFile(self.bundlePath, 'a') as bundleZip:
            bundleZip.writestr(f"{type}/{fileName}", data)
            self.resourceEntries.append((type, fileName, md5sum))

        return md5sum


if __name__ == "__main__":
    main()

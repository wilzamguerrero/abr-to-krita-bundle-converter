#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import sqlite3
import tarfile
from io import BytesIO
import os.path
from os import mkdir, listdir
import struct
from uuid import UUID

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help=".sut file path, or directory containing .sut files",
                        type=str)
    parser.add_argument("--dump_path", help="dump output file path",
                    type=str)
    parser.add_argument("--dump_images_path", help="dump images output file path",
                    type=str)
    args = parser.parse_args()

    path = args.file_path
    dumpPath = args.dump_path
    dumpImagesPath = args.dump_images_path

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
        print(f"Parsing {name}")
        parser = SUTBrushParser(path, name=name, dumpPath=dumpPath, dumpImagesPath=dumpImagesPath)

        if dumpPath:
            parser.dumpSUT(path)


class SUTBrushParser:
    def __init__(self, path, name="", dumpPath="", dumpImagesPath=""):
        self.path = path
        self.name = name
        self.dumpPath = dumpPath
        self.dumpImagesPath = dumpImagesPath

        self.resourceDimensions = {"": [32,32]}

    def dumpSUT(self, path):
        dumpTextPath = os.path.join(self.dumpPath, self.name+".txt")

        with open(dumpTextPath, 'w', encoding='utf_16_be') as f:

            connection = sqlite3.connect(path)

            connection.row_factory = sqlite3.Row

            cursor = connection.cursor()

            #for row in cursor.execute("SELECT * FROM sqlite_schema"):
            #    for key in row.keys():
            #        value = row[key]
            #        print(f"{key}: {value}")

            hasMaterialFile = cursor.execute("SELECT name FROM sqlite_schema WHERE type == 'table' AND name = 'MaterialFile'").fetchone() is not None


            print("Manager table:", file=f)
            for row in cursor.execute("SELECT * FROM Manager"):
                for key in row.keys():
                    value = row[key]
                    if value is not None and key == "PressureGraph":
                        points = self.readPressureGraph(value)
                        print(f"{key}: {points}", file=f)
                    elif value != b'\x00' and (key == "RootUuid" or key == "CurentNodeUuid" or key == "ObjectNodeUuid"):
                        uuidStr = str(UUID(bytes=value))
                        print(f"{key}: {uuidStr}", file=f)
                    else:
                        print(f"{key}: {value}", file=f)

            print("\nNode table:", file=f)
            for row in cursor.execute("SELECT * FROM Node"):
                for key in row.keys():
                    value = row[key]
                    if value != b'\x00' and (key == "NodeUuid" or key == "NodeNextUuid" or key == "NodeFirstChildUuid" or key == "NodeSelectedUuid"):
                        uuidStr = str(UUID(bytes=value))
                        print(f"{key}: {uuidStr}", file=f)
                    else:
                        print(f"{key}: {value}", file=f)

            print("\nVariant table:", file=f)
            for row in cursor.execute("SELECT * FROM Variant"):
                for key in row.keys():
                    value = row[key]
                    if value is not None:
                        if key == "TextureImage" or key == "BrushPatternImageArray":
                            (path1, name, path2) = self.unpackResourcePaths(value)
                            print(f"{key}: {name}\n    {path1}\n    {path2}", file=f)
                        elif key.endswith("Effector") and key != "BrushRotationEffector":
                            values = self.readEffector(value, key)
                            print(f"{key}: {values}", file=f)
                        elif key == "BrushInOutTarget":
                            values = self.readInOutTarget(value)
                            print(f"{key}: {values}", file=f)
                        elif key == "VariantShowParam":
                            values = self.readVariantShowParam(value)
                            print(f"{key}: {values}", file=f)
                        else:
                            print(f"{key}: {value}", file=f)
                    else:
                        print(f"{key}: {value}", file=f)

            if hasMaterialFile:
                print("\nMaterialFile table:", file=f)
                for row in cursor.execute("SELECT * FROM MaterialFile"):
                    for key in row.keys():
                        value = row[key]
                        if key != 'FileData':
                            print(f"{key}: {value}", file=f)

                    #FileData = a tar file...
                    materialFileData = BytesIO(row['FileData'])
                    materialTar = tarfile.TarFile(fileobj=materialFileData)
                    print("FileData: tar names", materialTar.getnames(), file=f)
                    #for info in materialTar.getmembers():
                    #    print("tar info", info.isfile(), info.size, file=f)

                    if self.dumpImagesPath:
                        dumpFolder = os.path.join(self.dumpImagesPath, self.name)
                        if not os.path.isdir(dumpFolder):
                            os.mkdir(dumpFolder)

                        uuid = row['CatalogPath'][-36:]
                        dumpDataPath = os.path.join(dumpFolder, uuid)

                        if not os.path.isdir(dumpDataPath):
                            os.mkdir(dumpDataPath)
                        # ???
                        if not os.path.isdir(os.path.join(dumpDataPath, "data")):
                            os.mkdir(os.path.join(dumpDataPath, "data"))
                        if not os.path.isdir(os.path.join(dumpDataPath, "thumbnail")):
                            os.mkdir(os.path.join(dumpDataPath, "thumbnail"))
                        if not os.path.isdir(os.path.join(dumpDataPath, "icedata")):
                            os.mkdir(os.path.join(dumpDataPath, "icedata"))

                        for name in materialTar.getnames():
                            reader = materialTar.extractfile(name)
                            filename = os.path.join(dumpDataPath, name) 
                            with open(filename, 'wb') as imageOutFile:
                                imageOutFile.write(reader.read())

                        #
                        material = os.path.join(dumpDataPath, "data", "material_0.layer")
                        if os.path.isfile(material):
                            self.loadC2F(material, zero=True)
                        else:
                            material = os.path.join(dumpDataPath, "data", "material.layer")
                            if os.path.isfile(material):
                                self.loadC2F(material)


            connection.close()

    
    def unpackResourcePaths(self, bytes):
        if bytes is None:
            return []
    
        reader = BytesIO(bytes)

        lenHeader = struct.unpack(">i", reader.read(4))[0] # 8
        value1 = struct.unpack(">i", reader.read(4))[0] # 1 ???
        lenData = struct.unpack(">i", reader.read(4))[0] # len(bytes) - 8
        #print(value1)

        path1 = self.readVarText(reader)
        #print(path1)

        value2 = struct.unpack(">i", reader.read(4))[0] # 2 for material_0, 3 for material ???
        #print(value2)
        name = self.readVarText(reader)
        #print(name)

        value3 = struct.unpack(">i", reader.read(4))[0] # 1 ???
        #print(value3)
        path2 = self.readVarText(reader)
        #print(path2)

        return (path1, name, path2)
    
    def readVarText(self, byteReader):
        len = struct.unpack(">i", byteReader.read(4))[0]
        return byteReader.read(len).decode(encoding="utf_16_le")

    def readEffector(self, bytes, key=None):
        if bytes is None:
            return []

        #if key is not None:
        #    print(key)
        #print("byteslen",len(bytes))
        reader = BytesIO(bytes)

        lenHeader = struct.unpack(">i", reader.read(4))[0] # 40

        # todo: ???

        values0 = struct.unpack(">"+"B"*8, reader.read(8))
        #print(values0)

        num = 5
        values = struct.unpack(">"+"i"*num, reader.read(num*4))
        lenData = struct.unpack(">i", reader.read(4))[0]
        value4 = struct.unpack(">i", reader.read(4))[0]
        #print(values, lenData, value4)

        points = []
        if len(bytes) > 40:
            lenHeader = struct.unpack(">i", reader.read(4))[0] # 12
            numDatas = struct.unpack(">i", reader.read(4))[0] # 
            lenData = struct.unpack(">i", reader.read(4))[0] # 16

            for _ in range(numDatas):
                x = struct.unpack(">d", reader.read(8))[0]
                y = struct.unpack(">d", reader.read(8))[0]
                #print(x,y)

                points.append([x, y])

        return [values0, (values, lenData, value4), points]
    
    def readPressureGraph(self, bytes):
        if bytes is None:
            return []

        reader = BytesIO(bytes)

        lenHeader = struct.unpack(">i", reader.read(4))[0] # 12
        numDatas = struct.unpack(">i", reader.read(4))[0] # 
        lenData = struct.unpack(">i", reader.read(4))[0] # 16

        points = []
        for _ in range(numDatas):
            x = struct.unpack(">d", reader.read(8))[0]
            y = struct.unpack(">d", reader.read(8))[0]
            #print(x,y)
            points.append([x,y])
        
        return points
    
    def readInOutTarget(self, bytes):
        if bytes is None:
            return []

        reader = BytesIO(bytes)

        lenHeader = struct.unpack(">i", reader.read(4))[0] # 12
        numDatas = struct.unpack(">i", reader.read(4))[0] # 11
        lenData = struct.unpack(">i", reader.read(4))[0] # 12

        # todo: ???
        datas = []
        for _ in range(numDatas):
            values0 = struct.unpack(">"+"i"*(lenData//4), reader.read(lenData))
            #print(values0)
            datas.append(values0)

        return datas
    
    def readVariantShowParam(self, bytes):
        if bytes is None:
            return []

        reader = BytesIO(bytes)

        lenHeader = struct.unpack(">i", reader.read(4))[0] # 12
        numDatas = struct.unpack(">i", reader.read(4))[0] # 
        lenData = struct.unpack(">i", reader.read(4))[0] # 4

        # todo: ???
        datas = []
        for _ in range(numDatas):
            value = struct.unpack(">i", reader.read(lenData))[0]
            #print(value)
            datas.append(value)

        return datas


    def loadC2F(self, path, zero=False):
        with open(path, 'rb') as f:
            C2F_MAGIC = b'\x89C2F\r\n\x1a\n'
            if f.read(8) != C2F_MAGIC:
                print(f"Error: Not a C2F file!: {path}")
                return False
            
            dataNum = 0

            while buf := f.read(4):
                chunk_data_len = struct.unpack("<i", buf)[0]
                chunk_id = f.read(4).decode()

                #print(f"Found chunk {chunk_id}")      

                if chunk_id == "dATA":
                    something = f.read(2) # 1 or 0 ??
                    data = f.read(chunk_data_len - 2)
                    chksum = f.read(4)
                    dataNum += 1
                    if dataNum == 1:
                        # mystery data!!!!
                        pass
                    elif dataNum == 2:
                        # mystery utf16 database??
                        self.readdATAbase(data, path, zero)
                    else:
                        print(f"C2F: found dATA chunk number {dataNum}???")    
                else:          
                    # Seek to next chunk at current position + data + CRC
                    f.seek(chunk_data_len + 4, 1)

    def readdATAbase(self, data, path, zero):

        lenInPages = len(data)//1024
        #print("lenInPages",lenInPages)

        encoding = 1 if zero else 2 # UTF-8, UTF-16 ???

        header = b"SQLite format 3\0" # magic
        header += struct.pack(">h", 1024) # page size
        header += struct.pack(">b", 1) # not WAL
        header += struct.pack(">b", 1) # not WAL
        header += struct.pack(">b", 0) # reserved bytes
        header += struct.pack(">b", 64) # 64
        header += struct.pack(">b", 32) # 32
        header += struct.pack(">b", 32) # 32
        header += struct.pack(">i", 1) # file change counter
        header += struct.pack(">i", lenInPages+1) # size of database in pages
        header += struct.pack(">i", 0) # first freelist page
        header += struct.pack(">i", 0) # freelist pages
        header += struct.pack(">i", 1) # schema cookie
        header += struct.pack(">i", 4) # schema format
        header += struct.pack(">i", 0) # default page cache size
        header += struct.pack(">i", 0) # page for vaccuum
        header += struct.pack(">i", encoding) # text encoding
        header += struct.pack(">i", 0) # user version
        header += struct.pack(">i", 0) # incremental vaccuum mode
        header += struct.pack(">i", 0) # app id
        header += b"\0" * 20 # reserved
        header += struct.pack(">i", 1) # version valid for
        header += struct.pack(">i", 3008008) # sqlite version
        
        header += b"\x0d" + b"\0\0" + b"\0\0" + struct.pack(">i", 1024) + b"\0"
        header += b"\0" * (924 - 8)

        #data = header + data

        databasePath = path+".sqlite"
        with open(databasePath, 'wb') as f:
            f.write(data)

        return

        connection = sqlite3.connect(databasePath)

        connection.row_factory = sqlite3.Row
        if not zero:
            connection.text_factory = lambda data: str(data, encoding="utf-16-le")

        cursor = connection.cursor()

        for row in cursor.execute("SELECT * FROM sqlite_schema"):
            for key in row.keys():
                value = row[key]
                print(f"{key}: {value}")


        for row in cursor.execute("SELECT * FROM Material"):
            for key in row.keys():
                value = row[key]
                print(f"{key}: {value}")

        connection.close()

    
    def loadResource(self, uuid, cursor):
            if cursor.execute("SELECT name FROM sqlite_schema WHERE type == 'table' AND name = 'MaterialFile'").fetchone() is not None:
                for row in cursor.execute("SELECT * FROM MaterialFile"):
                    rowUuid = row['CatalogPath'][-36:]
                    if rowUuid != uuid:
                        continue

                    #FileData = a tar file...
                    materialFileData = BytesIO(row['FileData'])
                    materialTar = tarfile.TarFile(fileobj=materialFileData)

                    if 'thumbnail/thumbnail.png' in materialTar.getnames():
                        reader = materialTar.extractfile('thumbnail/thumbnail.png')
                        self.resourceDimensions[uuid] = self.getDimensionsOfPNG(reader)
                        return reader.read()
            return b''

    def getDimensionsOfPNG(self, reader):
        PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
        if reader.read(8) != PNG_MAGIC:
            print("Not a .png file!")
            return (0,0)

        while buf := reader.read(4):
            chunk_data_len = int.from_bytes(buf, 'big')
            chunk_id = reader.read(4)

            if chunk_id == b"IHDR":
                width = struct.unpack(">i", reader.read(4))[0]
                height = struct.unpack(">i", reader.read(4))[0]
                break
            else:
                # Seek to next chunk at current position + data + CRC
                reader.seek(chunk_data_len + 4, 1)

        reader.seek(0, 0)

        return [width, height]
        


if __name__ == "__main__":
    main()

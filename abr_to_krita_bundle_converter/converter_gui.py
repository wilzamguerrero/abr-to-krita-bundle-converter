# SPDX-FileCopyrightText: 2024 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later


from abr.abr_parser import ABRBrushParser
from kpp.krita_resource_bundle_creator import KritaResourceBundleCreator
from abr_to_kpp import ABRBrushConverter

try:
    from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QApplication
    from PyQt6.QtCore import qDebug, QSettings, Qt
except:
    from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QApplication
    from PyQt5.QtCore import qDebug, QSettings, Qt

import os.path
import traceback

class ConverterGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.settings = QSettings(os.path.join(os.path.dirname(__file__), "settings.ini"), QSettings.Format.IniFormat)

    def showDialog(self):
        lastDir = os.path.dirname(self.settings.value("abrPath", ""))
        path, _ = QFileDialog.getOpenFileName(None, "Select ABR brush file",
                                              directory=lastDir,
                                              filter="Photoshop brush files (*.abr)")
        if not path:
            return

        self.settings.setValue("abrPath", path)

        bundlePath = os.path.splitext(path)[0] + ".bundle"

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            warnings = self.doConversion(path, bundlePath)
            QApplication.restoreOverrideCursor()
            if warnings:
                msg = f"Finished with warnings:\n\nBundle saved to:\n{bundlePath}\n\n" + "\n".join(warnings)
                QMessageBox.warning(None, "Conversion Complete", msg)
            else:
                QMessageBox.information(None, "Conversion Complete",
                                        f"Finished successfully!\n\nBundle saved to:\n{bundlePath}")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            qDebug(traceback.format_exc())
            QMessageBox.critical(None, "Conversion Error",
                                 f"An error occurred during conversion:\n\n{e}")

    def doConversion(self, path, bundlePath):
        warnings = []

        bundleCreator = KritaResourceBundleCreator(bundlePath)
        bundleCreator.setDesc(f"Generated from {os.path.basename(path)}")
        bundleCreator.createZip()

        parser = ABRBrushParser(path)
        parser.openFile()

        descEnd = parser.gotoBlock("desc")
        if descEnd == 0:
            parser.closeFile()
            raise RuntimeError(f"No 'desc' block found in {os.path.basename(path)}. Is this a valid ABR file?")
        parser.readDesc(parser.fileHandle, descEnd)

        numBrushes = len(parser.desc['Brsh'])

        sampUuidMd5 = {}
        sampUuidPNG = {}
        pattUuidMd5 = {}

        sampEnd = parser.gotoBlock("samp")
        if sampEnd > 0:
            try:
                sampNames = []
                while parser.fileHandle.seek(0, 1) < sampEnd:
                    (brushtipPNG, brushtipName, brushtipUuid) = parser.readBrushtip(parser.fileHandle, returnImage=True, invert=True)
                    if brushtipName in sampNames:
                        brushtipName = f"{brushtipName} {brushtipUuid[0:7]}"
                    sampNames.append(brushtipName)
                    md5sum = bundleCreator.addResourceFromData(brushtipPNG, 'brushes', f"{brushtipName}.png")
                    sampUuidMd5[brushtipUuid] = md5sum
                    sampUuidPNG[brushtipUuid] = brushtipPNG
                parser.verifyBytesRead(parser.fileHandle, sampEnd, 'samp')
            except Exception as e:
                qDebug(f"Warning: Error reading brush tips: {e}")
                warnings.append(f"Some brush tips could not be read: {e}")

        pattEnd = parser.gotoBlock("patt")
        if pattEnd > 0:
            try:
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
            except Exception as e:
                qDebug(f"Warning: Error reading patterns: {e}")
                warnings.append(f"Some patterns could not be read: {e}")

        parser.closeFile()

        tagName = os.path.splitext(os.path.basename(path))[0]

        names = []
        for i in range(numBrushes):
            try:
                name = parser.desc['Brsh'][i]['Objc']['brushPreset'][0]['Nm  ']['TEXT']
                qDebug(f"### Brush {i+1}/{numBrushes}: {name}")
                name = name.replace("/", "_")
                if name in names:
                    name = f"{name} Duplicate"
                names.append(name)
                converter = ABRBrushConverter(parser, '', '', name=name,
                                              bundleCreator=bundleCreator,
                                              sampUuidMd5=sampUuidMd5, pattUuidMd5=pattUuidMd5,
                                              sampUuidPNG=sampUuidPNG)
                converter.convertSettings(i)
                converter.saveKPP()
                bundleCreator.addTag(tagName, "paintoppresets", f"{name}.kpp")
            except Exception as e:
                qDebug(f"Warning: Failed to convert brush {i}: {e}")
                warnings.append(f"Brush {i} failed: {e}")

        bundleCreator.finishZip()

        return warnings


if __name__ == "__main__":

    try:
        from PyQt6.QtCore import Qt, QLibraryInfo
        from PyQt6.QtWidgets import QApplication
    except:
        from PyQt5.QtCore import Qt, QLibraryInfo
        from PyQt5.QtWidgets import QApplication
    import sys

    if QLibraryInfo.version().majorVersion() == 5: # PyQt5
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication([])

    app.setApplicationName("ABR to Krita Bundle Converter")

    gui = ConverterGUI()
    gui.showDialog()

    sys.exit(app.exec())

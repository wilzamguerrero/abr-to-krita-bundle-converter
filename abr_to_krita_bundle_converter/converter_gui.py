# SPDX-FileCopyrightText: 2024 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later


IS_KRITA = __name__ != "__main__"

from abr.abr_parser import ABRBrushParser
from kpp.krita_resource_bundle_creator import KritaResourceBundleCreator
from abr_to_kpp import ABRBrushConverter

try:
    from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QMessageBox, QApplication, QProgressBar
    from PyQt6.QtCore import qDebug
    from PyQt6.QtCore import QSettings, Qt
except:
    from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QMessageBox, QApplication, QProgressBar
    from PyQt5.QtCore import qDebug
    from PyQt5.QtCore import QSettings, Qt

import os.path
import sys
import traceback


class _SafeStdout:
    """Wrapper for sys.stdout that handles UnicodeEncodeError gracefully.
    Krita Flatpak may set stdout to ASCII encoding, which crashes print()
    on non-ASCII brush names (Korean, special symbols, etc.)."""
    def __init__(self, stream):
        self._stream = stream
    def write(self, text):
        try:
            return self._stream.write(text)
        except UnicodeEncodeError:
            return self._stream.write(
                text.encode('ascii', errors='replace').decode('ascii'))
    def flush(self):
        if hasattr(self._stream, 'flush'):
            self._stream.flush()
    def __getattr__(self, name):
        return getattr(self._stream, name)


class ConverterGUI(QWidget):

    dialog = None

    def __init__(self):
        super().__init__()

        self.settings = QSettings(os.path.join(os.path.dirname(__file__), "settings.ini"), QSettings.Format.IniFormat)

    def showDialog(self):
        if self.dialog is None:
            self.dialog = self.createDialog()

        self.dialog.show()

    def createDialog(self):
        dialog = QDialog()

        layout = QVBoxLayout()

        self.pathLayout = PathInputLayout(None, self.settings.value("abrPath", ""),
                                     ".abr path:", \
                                     "Path to a Photoshop .abr brush file", \
                                     "Photoshop brush files (*.abr)")
        layout.addLayout(self.pathLayout)

        self.progressBar = QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setTextVisible(True)
        layout.addWidget(self.progressBar)

        self.convertButton = QPushButton("Convert")
        self.convertButton.setToolTip("Convert the ABR file to a Krita .bundle")
        self.convertButton.clicked.connect(self.doConversion)
        layout.addWidget(self.convertButton)

        closeButton = QPushButton("Close")
        closeButton.setDefault(True)
        closeButton.clicked.connect(self.closeDialog)
        layout.addWidget(closeButton)

        dialog.setLayout(layout)

        dialog.setWindowTitle("ABR to Krita Bundle Converter")

        return dialog

    def closeDialog(self):
        self.settings.setValue("abrPath", self.pathLayout.path())
        self.dialog.accept()

    def doConversion(self):
        path = self.pathLayout.path()
        if not path or not os.path.isfile(path):
            QMessageBox.warning(self.dialog, "Error", "Please select a valid .abr file.")
            return

        # Auto-generate bundle path: same folder, same name, .bundle extension
        bundlePath = os.path.splitext(path)[0] + ".bundle"

        self.convertButton.setEnabled(False)
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)
        self.progressBar.setFormat("Starting...")
        QApplication.processEvents()
        try:
            warnings = self.doConversionImpl(path, bundlePath)
            if warnings:
                msg = f"Finished with warnings:\n\nBundle saved to:\n{bundlePath}\n\n" + "\n".join(warnings)
                QMessageBox.warning(self.dialog, "Conversion Complete", msg)
            else:
                QMessageBox.information(self.dialog, "Conversion Complete",
                                        f"Finished successfully!\n\nBundle saved to:\n{bundlePath}")
        except Exception as e:
            qDebug(traceback.format_exc())
            QMessageBox.critical(self.dialog, "Conversion Error", \
                                 f"An error occurred during conversion:\n\n{e}")
        finally:
            self.convertButton.setEnabled(True)
            self.progressBar.setVisible(False)

    def doConversionImpl(self, path, bundlePath):
        # Wrap stdout to prevent UnicodeEncodeError in ASCII-only environments
        old_stdout = sys.stdout
        sys.stdout = _SafeStdout(sys.stdout)
        try:
            return self._doConversionWork(path, bundlePath)
        finally:
            sys.stdout = old_stdout

    def _doConversionWork(self, path, bundlePath):
        warnings = []

        bundleCreator = KritaResourceBundleCreator(bundlePath)
        bundleCreator.setDesc(f"Generated from {os.path.basename(path)}")
        bundleCreator.createZip()

        self.progressBar.setFormat("Parsing ABR file...")
        QApplication.processEvents()

        parser = ABRBrushParser(path)
        parser.openFile()

        descEnd = parser.gotoBlock("desc")
        if descEnd == 0:
            parser.closeFile()
            raise RuntimeError(f"No 'desc' block found in {os.path.basename(path)}. Is this a valid ABR file?")
        parser.readDesc(parser.fileHandle, descEnd)

        numBrushes = len(parser.desc['Brsh'])
        self.progressBar.setMaximum(numBrushes + 2)  # +2 for samp and patt phases

        sampUuidMd5 = {}
        sampUuidPNG = {}
        pattUuidMd5 = {}

        self.progressBar.setFormat("Reading brush tips...")
        self.progressBar.setValue(0)
        QApplication.processEvents()

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
                    QApplication.processEvents()
                parser.verifyBytesRead(parser.fileHandle, sampEnd, 'samp')
            except Exception as e:
                safeErr = str(e).encode('ascii', errors='replace').decode('ascii')
                qDebug(f"Warning: Error reading brush tips: {safeErr}")
                warnings.append(f"Some brush tips could not be read: {safeErr}")

        self.progressBar.setFormat("Reading patterns...")
        self.progressBar.setValue(1)
        QApplication.processEvents()

        pattEnd = parser.gotoBlock("patt")
        if pattEnd > 0:
            pattNames = []
            while parser.fileHandle.seek(0, 1) < pattEnd:
                try:
                    images = parser.readPattern(parser.fileHandle, returnImage=True)
                    for (patternPNG, patternName, patternUuid) in images:
                        if patternName in pattNames:
                            patternName = f"{patternName} {patternUuid[0:7]}"
                        pattNames.append(patternName)
                        md5sum = bundleCreator.addResourceFromData(patternPNG, 'patterns', f"{patternName}.png")
                        pattUuidMd5[patternUuid] = md5sum
                    QApplication.processEvents()
                except Exception as e:
                    safeErr = str(e).encode('ascii', errors='replace').decode('ascii')
                    qDebug(f"Warning: Error reading a pattern: {safeErr}")
                    warnings.append(f"A pattern could not be read: {safeErr}")
                    # Skip to end of patt block since we can't recover the position
                    parser.fileHandle.seek(pattEnd)
                    break

        parser.closeFile()

        tagName = os.path.splitext(os.path.basename(path))[0]

        nameCounts = {}
        for i in range(numBrushes):
            try:
                name = parser.desc['Brsh'][i]['Objc']['brushPreset'][0]['Nm  ']['TEXT']
                safeName = name.encode('ascii', errors='replace').decode('ascii')
                qDebug(f"### Brush {i+1}/{numBrushes}: {safeName}")
                name = name.replace("/", "_")
                if name in nameCounts:
                    nameCounts[name] += 1
                    name = f"{name} ({nameCounts[name]})"
                else:
                    nameCounts[name] = 1
                converter = ABRBrushConverter(parser, '', '', name=name,
                                              bundleCreator=bundleCreator,
                                              sampUuidMd5=sampUuidMd5, pattUuidMd5=pattUuidMd5,
                                              sampUuidPNG=sampUuidPNG)
                converter.convertSettings(i)
                converter.writer.setName(name)
                converter.saveKPP()
                bundleCreator.addTag(tagName, "paintoppresets", f"{name}.kpp")
            except Exception as e:
                safeErr = str(e).encode('ascii', errors='replace').decode('ascii')
                qDebug(f"Warning: Failed to convert brush {i}: {safeErr}")
                warnings.append(f"Brush {i} failed: {e}")
            self.progressBar.setValue(i + 2)
            self.progressBar.setFormat(f"Converting brushes... {i+1}/{numBrushes}")
            if (i + 1) % 20 == 0:
                QApplication.processEvents()

        self.progressBar.setFormat("Writing bundle...")
        self.progressBar.setValue(numBrushes + 2)
        QApplication.processEvents()

        bundleCreator.finishZip()

        return warnings

class PathInputLayout(QHBoxLayout):

    def __init__(self, parent, value, labelText, toolTipText, filter=None):
        super().__init__(parent)

        self.filter = filter

        self.pathEdit = QLineEdit(value)
        pathLabel = QLabel(labelText)
        pathLabel.setToolTip(toolTipText)
        self.addWidget(pathLabel)
        self.addWidget(self.pathEdit)

        pathButton = QPushButton()
        if IS_KRITA:
            pathButton.setIcon(Application.icon("document-open"))
        else:
            pathButton.setText("Open")
        pathButton.setToolTip("Choose a file")
        pathButton.pressed.connect(self.getPath)
        self.addWidget(pathButton)

    def path(self):
        return self.pathEdit.text()

    def getPath(self):
        path, _filter = QFileDialog.getOpenFileName(None, "Choose a file to open", \
                                                    directory=os.path.dirname(self.pathEdit.text()), \
                                                    filter=self.filter, \
                                                    options=QFileDialog.Option.DontUseNativeDialog)
        if path:
            self.pathEdit.setText(path)


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

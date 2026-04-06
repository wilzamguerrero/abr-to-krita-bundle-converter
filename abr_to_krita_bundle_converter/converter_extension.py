# SPDX-FileCopyrightText: 2024 Freya Lupen <penguinflyer2222@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from krita import Extension

EXTENSION_ID = 'pykrita_abr_to_krita_bundle_converter'
MENU_ENTRY = 'Convert ABR brushes to bundle...'

from .converter_gui import ConverterGUI

class ABRToKritaBundleConverter(Extension):

    gui = None

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction(EXTENSION_ID, MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.action_triggered)

    def action_triggered(self):
        if self.gui is None:
            self.gui = ConverterGUI()
        
        self.gui.showDialog()

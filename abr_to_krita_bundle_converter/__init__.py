import sys
from os.path import dirname

# To make absolute imports work...
sys.path.append(dirname(__file__))

from .converter_extension import ABRToKritaBundleConverter

from krita import Krita

app = Krita.instance()
app.addExtension(ABRToKritaBundleConverter(app))

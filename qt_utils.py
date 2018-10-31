from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from video_capture import QVideoWidget
import os


def load_ui(filename):
    loader = QUiLoader()

    loader.registerCustomWidget(QVideoWidget)

    # read file
    filepath = os.path.join(os.path.dirname(__file__), filename)
    file = QFile(filepath)
    file.open(QFile.ReadOnly)

    # load window
    return loader.load(file)

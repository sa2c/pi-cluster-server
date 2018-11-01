import sys, random

from PySide2.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PySide2.QtCore import QTimer
from PySide2.QtGui import QIcon

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def plot(self, *args, **kwargs):
        self.axes.plot(*args, **kwargs)
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PlotCanvas()

    def update_data():
        data = [random.random() for i in range(25)]
        ex.plot(data,'-r')

    update_data()

    QTimer.singleShot(1000, update_data)

    ex.show()
    sys.exit(app.exec_())

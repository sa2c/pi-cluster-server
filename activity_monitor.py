from matplotlib_widget import PlotCanvas
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import random, sys


class ActivityPlotter(PlotCanvas):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ax = self.figure.add_axes([0, 0, 1, 1])
        self.ax.axis('on')

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)

    def update_plot(self):
        npi = 10
        x = range(npi)
        y = [random.random() for i in range(npi)]

        self.ax.clear()
        self.ax.plot(x, y, color='blue')
        self.redraw_plot()

    def redraw_plot(self):
        self.figure.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = ActivityPlotter()
    window.update_plot()
    window.show()

    sys.exit(app.exec_())

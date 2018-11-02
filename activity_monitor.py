from matplotlib_widget import PlotCanvas
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import numpy as np
import random, sys


class ActivityPlotter(PlotCanvas):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ax = self.figure.add_axes([0, 0, 1, 1])
        self.ax.axis('on')

    @Slot(np.ndarray)
    def update_plot(self, data):
        npi = 10
        x = range(npi)
        y = data

        self.ax.clear()
        self.ax.plot(x, y, color='blue')
        self.redraw_plot()

    def redraw_plot(self):
        self.figure.canvas.draw()


class ActivityFetchThread(QThread):
    """ continuously captures video and a depth map from kinect. Signals output
    the depth map and frame as a QPixmap.
    """
    activity_updated = Signal(np.ndarray)

    def run(self):
        while True:
            data = fetch_from_ssh()
            activity_updated.emit(data)
            time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = ActivityPlotter()

    a = ActivityFetchThread(window)
    a.activity_updated.connect(window.update_plot)
    a.start()

    window.show()

    sys.exit(app.exec_())

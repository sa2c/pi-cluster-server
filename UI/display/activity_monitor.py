from display.matplotlib_widget import PlotCanvas
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import numpy as np
import sys
import time
import io, os, tempfile

from simulation_proxy import fetch_activity


class ActivityPlotter(PlotCanvas):
    def __init__(self, parent=None):
        super().__init__(parent)
        a = ActivityFetchThread(self)
        a.activity_updated.connect(self.update_plot)
        a.start()

    @Slot(np.ndarray)
    def update_plot(self, cpu_usage):

        ax = self.figure.add_axes([0, 0, 1, 1])
        ax.clear()
        ax.set_ylim([0, 100])

        # gets the CPU usage from all the nodes and plots the data
        num_nodes = len(cpu_usage)

        #cpu_usage_global = np.zeros((timeperiod,num_nodes), dtype=float)

        nodes = np.linspace(1, num_nodes, num_nodes)
        ax.bar(nodes, cpu_usage)
        ax.set_xlabel("Node number")
        ax.set_ylabel("CPU usage (%)")
        self.draw()

    def redraw_plot(self):
        self.figure.canvas.draw()


class ActivityFetchThread(QThread):
    """ continuously captures video and a depth map from kinect. Signals output
    the depth map and frame as a QPixmap.
    """
    activity_updated = Signal(np.ndarray)

    def run(self):
        while True:
            data = fetch_activity()
            self.activity_updated.emit(data)
            time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = ActivityPlotter()

    window.show()

    sys.exit(app.exec_())

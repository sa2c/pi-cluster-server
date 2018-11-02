from matplotlib_widget import PlotCanvas
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import numpy as np
import random, sys
from fabric import Connection
import time

frontend = None
already_set_up = False
cluster_address = "pi@137.44.2.181"

def setup():
    ''' Copies cpuloadinfo.sh to the cluster'''
    global already_set_up
    global frontend
    print('creating fabric connection object "frontend"')
    frontend = Connection(host=cluster_address,connect_kwargs={"password":"sa2cpi"})
    print('Setting up cpuloadinfo.sh')
    frontend.put('cpuloadinfo.sh')
    already_set_up = True


def fetch_from_ssh():
    global already_set_up
    global frontend
    if not already_set_up:
        setup()
    print('Getting cpu usage data')
    cpu_usage = frontend.run('''bash cpuloadinfo.sh''', hide=True).stdout.split('\n')[1:-1]
    cpu_usage = [float(cpu_usage_meas.split(' ')[1]) for cpu_usage_meas in cpu_usage]
    return cpu_usage

class ActivityPlotter(PlotCanvas):
    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(np.ndarray)
    def update_plot(self, cpu_usage):

        ax = self.figure.add_subplot(111)
        ax.clear()


        # gets the CPU usage from all the nodes and plots the data
        num_nodes  = len(cpu_usage)

        #cpu_usage_global = np.zeros((timeperiod,num_nodes), dtype=float)

        time = np.linspace(1,num_nodes,num_nodes)
        ax.bar(time, cpu_usage)
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
            data = fetch_from_ssh()
            self.activity_updated.emit(data)
            time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = ActivityPlotter()

    a = ActivityFetchThread()
    a.activity_updated.connect(window.update_plot)
    a.start()

    window.show()

    sys.exit(app.exec_())

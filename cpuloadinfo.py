
import sys
import os
import numpy as np
import time
import sys, random
from fabric import Connection

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
 
 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
 
import random




# gets the CPU usage information for one node
def get_cpu_usage_node(cluster_address, timeperiod, cpu_usage):

    #cluster_address = "pi@137.44.2.181"
    cluster = Connection(host=cluster_address,connect_kwargs={"password":"sa2cpi"})

    for ii in range(timeperiod):
        #cpu_usage[ii] = psutil.cpu_percent(interval=0.1)

        #cpu_usage[ii] = float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$3+$4)*100/($2+$3+$4+$5)} END {print usage }' ''').readline())
        cpu_usage[ii] = round(float(cluster.run('''grep 'cpu ' /proc/stat | awk '{usage=($2+$3+$4)*100/($2+$3+$4+$5)} END {print usage }' ''', hide=True).stdout),4)
        #time.sleep(0.1)

    return
###################################################
###################################################


class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.left = 0
        self.top = 0
        self.title = 'CPU usage from all nodes'
        self.width = 500
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        m = PlotCanvas(self, width=5, height=4)
 
        self.show()
 
 
class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()
 
    def plot(self):
        ax = self.figure.add_subplot(111)

        # gets the CPU usage from all the nodes and plots the data
        cluster_address = "pi@137.44.2.181"
        num_nodes=5
        timeperiod=10

        cpu_usage_global = np.zeros((timeperiod,num_nodes), dtype=float)

        for ii in range(num_nodes):
            get_cpu_usage_node(cluster_address, timeperiod, cpu_usage_global[:,ii])
            print(cpu_usage_global[:,ii])

        time = np.linspace(1,timeperiod,timeperiod)
        ax.plot(time, cpu_usage_global)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("CPU usage (%)")
        #ax.set_title('CPU usage from all nodes')
        self.draw()


#############################################
#############################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


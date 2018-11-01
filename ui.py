from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from detail_form import DetailForm
from video_capture import VideoCaptureThread
from control_window import ControlWindow
import os

from queue_run import local_path, queue_run


def get_run_completion_percentage(index):
    ''' Read the completion percentage of the run
    '''
    output = get_cfd_output(index)

    found = False
    try:
        for line in output.split("\n"):
            if "MAIN:  Time:" in line:
                timestring = line.split(' ')[3]
                found = True
        if found:
            numbers = timestring.split('/')
            percentage = float(numbers[0]) / float(numbers[1])
        else:
            percentage = 0
    except:
        percentage = 0
    return percentage


existing_runs = set(os.listdir("{}/signal/".format(local_path)))

def run_complete(path):
    runs = set(os.listdir(path))
    for run in runs - existing_runs:
        index = run.replace("run", '')
        print("Run {} is complete!".format(index))
        existing_runs.add(run)


class RunCompleteWatcher(QFileSystemWatcher):
    ''' Periodically polls the cluster to check for finished jobs
        Gets the resulting images as numpy arrays and 
        communicates them through a signal
    '''

    def __init__(self):
        path = "{}/signal/".format(local_path)
        filepath = "{}/signal_file".format(path)
        super().__init__([path, filepath])

        self.directoryChanged.connect(run_complete)


def test_submit():
    contour = np.loadtxt("scf1540984574-outline-coords.dat")
    queue_run(contour, 2)
    while True:
        print(get_run_completion_percentage(2))
        time.sleep(1)


def test_app():
    app = QApplication(sys.argv)
    label = QLabel("<font color=red size=40>Hello World!</font>")
    label.show()
    rcw = RunCompleteWatcher()
    sys.exit(app.exec_())


#test_submit()
#test_app()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # initialise another thread for video capture
    th = VideoCaptureThread()

    window = ControlWindow({})

    th.changeFramePixmap.connect(window.ui.video_rgb.setImage)
    th.changeDepthPixmap.connect(window.ui.video_depth.setImage)

    th.changeFramePixmap.connect(window.viewfinder.main_video.setImage)
    th.changeDepthPixmap.connect(window.viewfinder.depth_video.setImage)

    th.setParent(window)
    th.start()

    window.show()
    sys.exit(app.exec_())

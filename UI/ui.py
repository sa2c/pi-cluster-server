from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from kinectlib.kinectlib import *
from display.detail_form import DetailForm
from display.video_capture import VideoCaptureThread, QVideoWidget
from display.control_window import ControlWindow
from display.pyside_dynamic import loadUiWidget
from display.activity_monitor import ActivityPlotter
from display.viewfinder import ViewfinderWindow
from display.results_window import ResultsWindow
from controller import Controller
from cluster_notify import ClusterNotifyThread
import os

from settings import local_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create("Fusion"))
    # initialise another thread for video capture

    cluster_notify = ClusterNotifyThread()

    video_source = VideoCaptureThread()

    controller = Controller()

    viewfinder = ViewfinderWindow(video_source)

    window = ControlWindow(controller, viewfinder, video_source)

    #results = ResultsWindow()
    #cluster_notify.simulations_changed.connect(results.simulations_changed)

    video_source.setParent(window)
    video_source.start()

    #cluster_notify.start()

    window.show()
    viewfinder.show()
    #results.show()
    sys.exit(app.exec_())

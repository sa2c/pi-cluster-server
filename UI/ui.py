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
import os

from settings import local_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create("Fusion"))
    # initialise another thread for video capture
    th = VideoCaptureThread()

    window = ControlWindow()

    th.changeFramePixmap.connect(window.ui.video_rgb.setImage)
    th.changeDepthPixmap.connect(window.ui.video_depth.setImage)

    th.changeFramePixmap.connect(window.viewfinder.ui.main_video.setImage)
    th.changeDepthPixmap.connect(window.viewfinder.ui.depth_video.setImage)

    th.setParent(window)
    th.start()

    window.show()
    sys.exit(app.exec_())

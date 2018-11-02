from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from detail_form import DetailForm
from video_capture import VideoCaptureThread
from control_window import ControlWindow
from leaderboard import get_test_simulations
import os

from queue_run import local_path, queue_run

directory = 'outbox/signal'
while not os.path.exists(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        print(f'directory creation failed: {directory}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create("Fusion"))
    # initialise another thread for video capture
    th = VideoCaptureThread()

    simulations = {}

    window = ControlWindow()
    window.viewfinder.ui.leaderboard.update(simulations.values())

    th.changeFramePixmap.connect(window.ui.video_rgb.setImage)
    th.changeDepthPixmap.connect(window.ui.video_depth.setImage)

    th.changeFramePixmap.connect(window.viewfinder.ui.main_video.setImage)
    th.changeDepthPixmap.connect(window.viewfinder.ui.depth_video.setImage)

    th.setParent(window)
    th.start()

    window.show()
    sys.exit(app.exec_())

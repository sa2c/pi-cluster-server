from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from kinectlib.kinectlib import *
from display.detail_form import DetailForm
from display.video_capture import VideoCaptureThread, QVideoWidget
from display.control_window import ControlWindow
from display.leaderboard import get_test_simulations
from display.pyside_dynamic import loadUiWidget
from display.activity_monitor import ActivityPlotter
import os
from cluster_manager import queue_run

from settings import local_path

directory = 'outbox/signal'
while not os.path.exists(directory):
    try:
        os.makedirs(directory)
    except OSError as e:
        print(f'directory creation failed: {directory}')


def create_secondary_panel(parent, video_cap_thread):
    window = QDialog(parent)
    panel = loadUiWidget(
        '../designer/secondary_panel.ui',
        customWidgets=[QVideoWidget, ActivityPlotter])
    window.setLayout(QVBoxLayout())
    window.layout().addWidget(panel)
    window.setStyleSheet('background-color: #efebd8;')

    th.changeFramePixmap.connect(panel.video_rgb.setImage)
    th.changeDepthPixmap.connect(panel.video_depth.setImage)

    window.show()

    return window


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

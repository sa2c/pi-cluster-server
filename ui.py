from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from fabric import Connection
from detail_form import DetailForm
from video_capture import VideoCaptureThread
from control_window import ControlWindow
import os

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # initialise another thread for video capture
    th = VideoCaptureThread()

    data = np.load('kinect_to_points/color_kinect_data.npy')
    depths = np.load('kinect_to_points/kinect_data.npy')
    depthimages = [depth_to_depthimage(depth) for depth in depths]
    simulations = {
        '23454325': {
            'name': 'Bob Jones',
            'score': 10.5,
            'time': '10:00 12/15/2018',
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '3445345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'time': '11:15 12/15/2018',
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        },
        '234523452': {
            'name': 'Bob Jones',
            'score': 10.5,
            'time': '10:00 12/15/2018',
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '23452345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'time': '11:15 12/15/2018',
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        }
    }

    window = ControlWindow(simulations)

    th.changeFramePixmap.connect(window.ui.video_rgb.setImage)
    th.changeFramePixmap.connect(window.viewfinder.main_video.setImage)
    th.changeDepthPixmap.connect(window.ui.video_depth.setImage)

    th.setParent(window)
    th.start()

    window.show()
    sys.exit(app.exec_())

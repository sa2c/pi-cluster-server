from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from display.video_capture import VideoCaptureThread, QVideoWidget
from display.pyside_dynamic import loadUiWidget
from display.activity_monitor import ActivityPlotter
from display.matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot

script_directory = os.path.dirname(os.path.abspath(__file__))


class ViewfinderWindow(QMainWindow):
    def __init__(self, video_source, parent=None):
        super().__init__(parent)
        self.ui = loadUiWidget(
            os.path.join(script_directory, '../designer/viewfinder.ui'),
            customWidgets=[
                QVideoWidget
            ])
        self.setCentralWidget(self.ui)

        self.freeze = False

        # connect the video source output to the viewfinder
        video_source.changeFramePixmap.connect(self.set_video)
        video_source.changeDepthPixmap.connect(self.set_depth)

    def set_depth(self, image):
        if not self.freeze:
            self.ui.depth_video.setImage(image)

    def set_video(self, image):
        if not self.freeze:
            self.ui.main_video.setImage(image)

    def set_static(self, video, depth):
        self.freeze = False
        self.set_video(video)
        self.set_depth(depth)
        self.freeze = True

if __name__ == '__main__':
    app = QApplication(sys.argv)

    video_source = VideoCaptureThread()

    window = ViewfinderWindow(video_source)

    video_source.setParent(window)
    video_source.start()

    window.show()
    app.exec_()

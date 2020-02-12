from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
from display.video_capture import VideoCaptureThread, QVideoWidget
from display.pyside_dynamic import loadUiWidget


class ViewfinderWindow(QMainWindow):
    def __init__(self, video_source, parent=None):
        super().__init__(parent)
        self.ui = loadUiWidget('viewfinder.ui', customWidgets=[QVideoWidget])
        self.setCentralWidget(self.ui)

        self.freeze = False

        # connect the video source output to the viewfinder
        video_source.changeFramePixmap.connect(self.set_frame)

    def set_frame(self, frame, depthimage):
        self.set_video(frame)
        self.set_depth(depthimage)

    def set_depth(self, image):
        if not self.freeze:
            self.ui.depth_video.setImage(image)

    def set_video(self, image):
        if not self.freeze:
            self.ui.main_video.setImage(image)

    def set_static(self, rgb_frame, depthimage):
        self.ui.main_video.setStaticImage(rgb_frame)
        self.ui.depth_video.setStaticImage(depthimage)

    def resume_dynamic(self):
        self.ui.main_video.resumeDynamicUpdate()
        self.ui.depth_video.resumeDynamicUpdate()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    video_source = VideoCaptureThread()

    window = ViewfinderWindow(video_source)

    video_source.setParent(window)
    video_source.start()

    window.show()
    app.exec_()

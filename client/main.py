from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
from display.video_capture import VideoCaptureThread
from display.control_window import ControlWindow
from display.viewfinder import ViewfinderWindow
from controller import Controller
from snapshots import handler as snap_handler

from settings import local_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create("Fusion"))
    # initialise another thread for video capture

    video_source = VideoCaptureThread()

    # Call write_video_maybe every time that video_source emits a frame
    video_source.changeFramePixmap.connect(snap_handler.write_video_maybe)

    controller = Controller(calibration_callback=snap_handler.set_background)

    viewfinder = ViewfinderWindow(video_source)

    window = ControlWindow(controller, viewfinder, video_source)

    video_source.setParent(window)
    video_source.start()

    window.show()
    viewfinder.show()
    sys.exit(app.exec_())

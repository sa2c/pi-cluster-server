from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *


def frame_to_QPixmap(frame):
    # Convert frame to QImage
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                    QImage.Format_RGB888)
    image = qimage.scaled(320, 240, Qt.KeepAspectRatio)
    return QPixmap.fromImage(image)


class VideoCaptureThread(QThread):
    changeFramePixmap = Signal(QPixmap, np.ndarray)
    changeDepthPixmap = Signal(QPixmap, np.ndarray)

    def run(self):
        background = measure_depth(20)

        while True:
            self.capture_video_frame()
            self.capture_depth(background)
            time.sleep(0.05)

    def capture_video_frame(self):
        # Capture video frame
        frame = get_video()

        p = frame_to_QPixmap(frame)

        # Emit video frame QImage
        self.changeFramePixmap.emit(p, frame)

    def capture_depth(self, background):
        # measure depth
        depth = measure_depth()

        # create depth image
        depthimage = depth_to_depthimage(depth)
        p = frame_to_QPixmap(depthimage)

        # create depth image
        depth = remove_background(depth, background)

        self.changeDepthPixmap.emit(p, depth)


class QVideoWidget(QLabel):
    @Slot(QPixmap, np.ndarray)
    def setImage(self, image):
        self.setPixmap(image)


def load_ui(filename):
    loader = QUiLoader()
    loader.registerCustomWidget(QVideoWidget)

    # read file
    filepath = os.path.join(os.path.dirname(__file__), filename)
    file = QFile(filepath)
    file.open(QFile.ReadOnly)

    # load window
    return loader.load(file)


class ControlWindow(QMainWindow):
    def __init__(self, video_thread, parent=None):
        self.offset = [0, 0]
        self.scale = [1, 1]
        self.captured = None

        super().__init__(parent)
        self.ui = load_ui('designer/control_panel.ui')
        self.setCentralWidget(self.ui)

        self.ui.capture_button.released.connect(self.capture_action)

        self.calibrate()

        th.changeFramePixmap.connect(self.ui.video_rgb.setImage)
        th.changeDepthPixmap.connect(self.ui.video_depth.setImage)

    def capture_action(self):
        self.capture_depth = measure_depth()
        self.capture_rgb_frame = get_video()
        self.process()

    def process(self):
        # set rgb image visible
        clean_depth = remove_background(self.capture_depth, self.background)
        depthimage = depth_to_depthimage(self.capture_depth)

        # compute contour
        contour = normalised_depth_to_contour(clean_depth)

        outline = contour

        # apply offset and scale to contour
        outline[0, :] = outline[0, :] * self.scale[0]
        outline[0, :] = outline[0, :] + self.offset[0]
        outline[1, :] = outline[1, :] * self.scale[1]
        outline[1, :] = outline[1, :] + self.offset[1]

        # add contour to images
        cv2.drawContours(depthimage, contour, -1, (0, 0, 255), 2)
        cv2.drawContours(self.capture_rgb_frame, contour, -1, (0, 0, 255), 2)

        # set image
        image = frame_to_QPixmap(self.capture_rgb_frame)
        self.ui.captured_rgb.setImage(image)
        self.ui.captured_depth.setImage(frame_to_QPixmap(depthimage))

    def calibrate(self):
        self.background = measure_depth(20)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.offset[1] -= 5
        if event.key() == Qt.Key_Down:
            self.offset[1] += 5
        if event.key() == Qt.Key_Left:
            self.offset[0] -= 5
        if event.key() == Qt.Key_Right:
            self.offset[0] += 5

        self.process()

        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # initialise another thread for video capture
    th = VideoCaptureThread()
    window = ControlWindow(th)

    th.start()
    window.show()

    sys.exit(app.exec_())

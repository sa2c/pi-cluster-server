from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from kinect_to_points.kinect_lib import *


class QVideoWidget(QLabel):
    @Slot(QImage)
    def setImage(self, image):
        x = self.width()
        y = self.height()
        qimage = image.scaled(x, y, Qt.KeepAspectRatio)
        image = QPixmap.fromImage(qimage)
        self.setPixmap(image)


class VideoCaptureThread(QThread):
    """ continuously captures video and a depth map from kinect. Signals output
    the depth map and frame as a QPixmap.
    """
    changeFramePixmap = Signal(QImage)
    changeDepthPixmap = Signal(QImage)

    def run(self):
        while True:
            self.capture_video_frame()
            self.capture_depth()
            time.sleep(0.1)

    def capture_video_frame(self):
        # Capture video frame
        frame = get_video()

        p = frame_to_qimage(frame)

        # Emit video frame QImage
        self.changeFramePixmap.emit(p)

    def capture_depth(self):
        # measure depth
        depth = measure_depth()

        # create depth image
        depthimage = depth_to_depthimage(depth)
        p = frame_to_qimage(depthimage)

        self.changeDepthPixmap.emit(p)


def frame_to_qimage(frame):
    # Convert frame to QImage
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                    QImage.Format_RGB888)
    return qimage

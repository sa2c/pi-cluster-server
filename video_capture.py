from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from kinect_to_points.kinect_lib import *


class QVideoWidget(QLabel):
    @Slot(QPixmap)
    def setImage(self, image):
        self.setPixmap(image)


class VideoCaptureThread(QThread):
    """ continuously captures video and a depth map from kinect. Signals output
    the depth map and frame as a QPixmap.
    """
    changeFramePixmap = Signal(QPixmap)
    changeDepthPixmap = Signal(QPixmap)

    def run(self):
        while True:
            self.capture_video_frame()
            self.capture_depth()
            time.sleep(0.1)

    def capture_video_frame(self):
        # Capture video frame
        frame = get_video()

        p = frame_to_QPixmap(frame)

        # Emit video frame QImage
        self.changeFramePixmap.emit(p)

    def capture_depth(self):
        # measure depth
        depth = measure_depth()

        # create depth image
        depthimage = depth_to_depthimage(depth)
        p = frame_to_QPixmap(depthimage)

        self.changeDepthPixmap.emit(p)


def frame_to_QPixmap(frame):
    # Convert frame to QImage
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                    QImage.Format_RGB888)
    image = qimage.scaled(320, 240, Qt.KeepAspectRatio)
    return QPixmap.fromImage(image)

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from kinect_to_points.kinect_lib import *


class QVideoWidget(QLabel):
    def __init__(self, parent=None):
        self.dynamic_update = True
        super().__init__(parent)

    @Slot(np.ndarray)
    def setImage(self, image):
        if self.dynamic_update:
            self._set_image(image)

    def _set_image(self, image):
        x = self.width()
        y = self.height()

        iy,ix,_ = image.shape

        # fit to frame keeping aspect ratio
        r = ix / iy
        if x > r*y:
            x = int(r*y)
        else:
            y = int(x/r)
        
        resized = cv2.resize(image, (x, y))

        # Encode
        _, buf = cv2.imencode('.ppm',resized)

        # Convert to QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buf.tostring())
        self.setPixmap(pixmap)

    def setStaticImage(self, image):
        self.dynamic_update = False
        self._set_image(image)

    def resumeDynamicUpdate():
        self.dynamic_update = True



class VideoCaptureThread(QThread):
    """ continuously captures video and a depth map from kinect. Signals output
    the depth map and frame as a QPixmap.
    """
    changeFramePixmap = Signal(np.ndarray)
    changeDepthPixmap = Signal(np.ndarray)

    def run(self):
        while True:
            self.capture_video_frame()
            self.capture_depth()
            time.sleep(0.1)

    def capture_video_frame(self):
        # Capture video frame
        frame = get_video()

        # Emit video frame
        self.changeFramePixmap.emit(frame)

    def capture_depth(self):
        # measure depth
        depth = measure_depth()

        # create depth image
        depthimage = depth_to_depthimage(depth)

        # Emit video frame
        self.changeDepthPixmap.emit(depthimage)


def frame_to_qimage(frame):
    # Convert frame to QImage
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                    QImage.Format_RGB888)
    return qimage

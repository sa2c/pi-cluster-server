from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from kinectlib.kinectlib import device, measure_depth, depth_to_depthimage
import time
import cv2
import numpy as np


class QVideoWidget(QLabel):
    def __init__(self, parent=None):
        self.dynamic_update = True
        self.mask = None
        super().__init__(parent)

    @Slot(np.ndarray)
    def setImage(self, image):
        if self.dynamic_update:
            self._set_image(image)

    def _set_image(self, image):
        if self.mask is not None:
            image = image - self.mask

        x = self.width()
        y = self.height()

        iy, ix, _ = image.shape

        # fit to frame keeping aspect ratio
        r = ix / iy
        if x > r * y:
            x = int(r * y)
        else:
            y = int(x / r)

        resized = cv2.resize(image, (x, y))

        # Encode
        _, buf = cv2.imencode('.ppm', resized)

        # Convert to QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(buf.tostring())
        self.setPixmap(pixmap)

    def _set_mask(self, mask):
        self.mask = mask

    def setStaticImage(self, image):
        self.dynamic_update = False
        self._set_image(image)

    def resumeDynamicUpdate(self):
        self.dynamic_update = True


class VideoCaptureThread(QThread):
    """ continuously captures video and a depth map from kinect. Signals output
    the depth map and frame as a QPixmap.
    """
    changeFramePixmap = Signal(np.ndarray,np.ndarray)

    def run(self):
        while True:
            self.capture_video_frame()
            time.sleep(0.1)

    def capture_video_frame(self):
        # Capture video frame
        frame = device.get_video()

        # measure depth
        depth = measure_depth()

        # create depth image
        depthimage = depth_to_depthimage(depth)

        # Emit video frame
        self.changeFramePixmap.emit(frame, depthimage)

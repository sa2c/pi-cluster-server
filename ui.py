from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from fabric import Connection


def get_cfd_output():
    ''' Get the current stdout of the ongoing run
        or the previpous run.
    '''
    cluster = Connection("pi@10.0.0.253")

    with cluster.cd('Documents/picluster/cfd/'):
        return cluster.run('cat fabric_run_output', hide=True)

class ClusterSitterThread(QThread):
    ''' Copies contour.txt to the cluster and starts
        the cfd run

        Need to add a signal to report execution as finished
        (or can I just check if the thread is alive?)
    '''

    def __init__(self, index):
        super().__init__()
        self.index = index

    def run(self):
        cluster = Connection("pi@10.0.0.253")

        cluster.put('contour.txt',remote='Documents/picluster/cfd/run-outline-coords.dat')
        with cluster.cd('Documents/picluster/cfd/'):
            print("Starting run")
            cluster.run('python runcfd.py run > fabric_run_output', hide=True)
            print("Run ended")
            cluster.run('rm run-outline-coords.dat', hide=True)




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
        self.process_image()

    def process_image(self):
        rgb_frame = np.copy(self.capture_rgb_frame)

        # set rgb image visible
        clean_depth = remove_background(self.capture_depth, self.background)
        depthimage = depth_to_depthimage(self.capture_depth)

        # compute contour
        contour = normalised_depth_to_contour(clean_depth)

        outline, transformed_outline = contour_to_outline(
            contour, self.scale, self.offset)

        # add contour to images
        cv2.drawContours(depthimage, [outline], -1, (0, 0, 255), 2)
        cv2.drawContours(rgb_frame, [transformed_outline], -1, (0, 0, 255), 2)

        # set image
        image = frame_to_QPixmap(rgb_frame)
        self.ui.captured_rgb.setImage(image)
        self.ui.captured_depth.setImage(frame_to_QPixmap(depthimage))

        self.image = frame_to_QPixmap(rgb_frame)
        self.ui.captured_rgb.setImage(self.image)

    def calibrate(self):
        self.background = measure_depth(20)

    def keyPressEvent(self, event):

        motion = 1
        large_motion = 10

        if event.text() == 'k':
            self.offset[1] -= large_motion
        elif event.text() == 'j':
            self.offset[1] += large_motion
        elif event.text() == 'h':
            self.offset[0] -= large_motion
        elif event.text() == 'l':
            self.offset[0] += large_motion
        elif event.text() == 'K':
            self.offset[1] -= motion
        elif event.text() == 'J':
            self.offset[1] += motion
        elif event.text() == 'H':
            self.offset[0] -= motion
        elif event.text() == 'L':
            self.offset[0] += motion

        self.process_image()

        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # initialise another thread for video capture
    th = VideoCaptureThread()
    window = ControlWindow(th)

    th.setParent(window)
    th.start()
    window.show()

    sys.exit(app.exec_())

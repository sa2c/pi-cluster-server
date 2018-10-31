from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from fabric import Connection

cluster_address = "localhost"
cluster_path = "picluster2"
nmeasurements = 20


def get_cfd_output( index ):
    ''' Get the current stdout of the ongoing run
        or the previous run.
    '''
    cluster = Connection(cluster_address)

    directory = '{}/outbox/run{}/'.format(cluster_path,index)
    with cluster.cd(directory):
        return cluster.run('cat output', hide=True).stdout

def get_run_completion_percentage( index ):
    ''' Read the completion percentage of the run
    '''
    output = get_cfd_output( index )
    
    percentage = 0
    for line in output.split("\n"):
        if "MAIN:  Time:" in line:
            timestring = line.split(' ')[3]

    numbers = timestring.split('/')
    percentage = float(numbers[0])/float(numbers[1])
    return percentage


def queue_run( contour, index ):
    cluster = Connection(cluster_address)

    # save contour to file and copy to the cluster inbox
    filename = "contour.dat"
    write_outline( filename, contour )

    remote_name = '{}/inbox/run{}'.format(cluster_path,index)
    cluster.put(filename,remote=remote_name)


class ClusterSitterThread(QThread):
    ''' Periodically polls the cluster to check for finished jobs
        Gets the resulting images as numpy arrays and 
        communicates them through a signal
    '''

    def run(self):
        pass



def frame_to_QPixmap(frame):
    # Convert frame to QImage
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                    QImage.Format_RGB888)
    image = qimage.scaled(320, 240, Qt.KeepAspectRatio)
    return QPixmap.fromImage(image)


class VideoCaptureThread(QThread):
    """ continuously captures video and a depth map from kinect. Signals output
    the depth map and frame as a QPixmap.
    """
    changeFramePixmap = Signal(QPixmap)
    changeDepthPixmap = Signal(QPixmap)

    def run(self):
        while True:
            self.capture_video_frame()
            self.capture_depth(background)
            time.sleep(0.1)

    def capture_video_frame(self):
        # Capture video frame
        frame = get_video()

        p = frame_to_QPixmap(frame)

        # Emit video frame QImage
        self.changeFramePixmap.emit(p)

    def capture_depth(self, background):
        # measure depth
        depth = measure_depth()

        # create depth image
        depthimage = depth_to_depthimage(depth)
        p = frame_to_QPixmap(depthimage)

        self.changeDepthPixmap.emit(p)


class QVideoWidget(QLabel):
    @Slot(QPixmap)
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
        self.ui.process_button.released.connect(self.run_cfd_action)

        self.background = measure_depth(nmeasurements)

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
        self.contour = transformed_outline

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
        self.background = measure_depth(nmeasurements)

    def run_cfd_action(self):
        self.index = int( time.time() )
        queue_run( self.contour, self.index )

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
    cluster_sitter = ClusterSitterThread()
    window = ControlWindow(th)

    th.setParent(window)
    th.start()
    window.show()

    sys.exit(app.exec_())

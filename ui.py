from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from fabric import Connection
from detail_form import DetailForm
from video_capture import VideoCaptureThread
from control_window import ControlWindow

cluster_address = "localhost"
cluster_path = "picluster2"
nmeasurements = 20


def get_cfd_output(index):
    ''' Get the current stdout of the ongoing run
        or the previous run.
    '''
    cluster = Connection(cluster_address)

    directory = '{}/outbox/run{}/'.format(cluster_path, index)
    with cluster.cd(directory):
        return cluster.run('cat output', hide=True).stdout


def get_run_completion_percentage(index):
    ''' Read the completion percentage of the run
    '''
    output = get_cfd_output(index)

    percentage = 0
    for line in output.split("\n"):
        if "MAIN:  Time:" in line:
            timestring = line.split(' ')[3]

    numbers = timestring.split('/')
    percentage = float(numbers[0]) / float(numbers[1])
    return percentage


def queue_run(contour, index):
    cluster = Connection(cluster_address)

    # save contour to file and copy to the cluster inbox
    filename = "contour.dat"
    write_outline(filename, contour)

    remote_name = '{}/inbox/run{}'.format(cluster_path, index)
    cluster.put(filename, remote=remote_name)


class ClusterSitterThread(QThread):
    ''' Periodically polls the cluster to check for finished jobs
        Gets the resulting images as numpy arrays and 
        communicates them through a signal
    '''

    def run(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # initialise another thread for video capture
    th = VideoCaptureThread()
    cluster_sitter = ClusterSitterThread()

    data = np.load('kinect_to_points/color_kinect_data.npy')
    depths = np.load('kinect_to_points/kinect_data.npy')
    depthimages = [depth_to_depthimage(depth) for depth in depths]
    simulations = {
        '23454325': {
            'name': 'Bob Jones',
            'score': 10.5,
            'time': '10:00 12/15/2018',
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '3445345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'time': '11:15 12/15/2018',
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        },
        '234523452': {
            'name': 'Bob Jones',
            'score': 10.5,
            'time': '10:00 12/15/2018',
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '23452345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'time': '11:15 12/15/2018',
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        }
    }

    window = ControlWindow(simulations)

    th.changeFramePixmap.connect(window.ui.video_rgb.setImage)
    th.changeFramePixmap.connect(window.viewfinder.main_video.setImage)
    th.changeDepthPixmap.connect(window.ui.video_depth.setImage)

    th.setParent(window)
    th.start()

    window.show()
    sys.exit(app.exec_())

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from video_capture import frame_to_qimage, QVideoWidget
from pyside_dynamic import loadUi
from kinect_to_points.kinect_lib import depth_to_depthimage

image_width = 300
image_height = 300


class LeaderboardWidget(QListWidget):
    def __init__(self, parent=None):
        """ Initialised with an iterable of simulation dicts to display """

        super().__init__(parent)

        # setup list item styles
        self.stylesheets = [
            "background-color: #FCF7F8;", "background-color: #90C2E7;"
        ]

    def update(self, simulations):

        self.clear()

        for i, sim in enumerate(simulations):
            rgb_image = frame_to_qimage(sim['rgb_frame'])
            depth_image = frame_to_qimage(sim['depth_frame'])

            widget = QWidget()
            loadUi(
                'designer/leaderboard_list_item.ui',
                widget,
                customWidgets={'QVideoWidget': QVideoWidget})

            # set background color
            widget.setStyleSheet(self.stylesheets[i % 2])

            # populate data
            widget.name.setText(sim['name'])
            widget.score.setText(f'score: {sim["score"]}')
            widget.rank.setText(f'#{i + 1}')

            # set image dimensions
            widget.rgb_image.setFixedHeight(image_width)
            widget.rgb_image.setFixedWidth(image_height)
            widget.depth_image.setFixedHeight(image_width)
            widget.depth_image.setFixedWidth(image_height)

            # set images
            widget.rgb_image.setImage(rgb_image)
            widget.depth_image.setImage(depth_image)

            # add item
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, widget)


def get_test_simulations():
    print('loading simulations...')
    data = np.load('sim.npy')
    depths = np.load('sim.npy')
    depthimages = [depth_to_depthimage(depth) for depth in depths]

    simulations = {
        '23454325': {
            'name': 'Bob Jones',
            'score': 10.5,
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '3445345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        },
        '234523452': {
            'name': 'Bob Jones',
            'score': 10.5,
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '23452345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        }
    }

    print('simulations loaded')
    return simulations


if __name__ == '__main__':
    app = QApplication(sys.argv)

    lb = LeaderboardWidget()
    lb.update(simulations.values())
    lb.resize(2000, 1000)

    def change_name():
        simulations[0]['name'] = 'Another Name'
        lb.update(simulations)

    QTimer.singleShot(3000, change_name)

    lb.show()

    sys.exit(app.exec_())

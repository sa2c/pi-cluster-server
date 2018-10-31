from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import depth_to_depthimage


def frame_to_QPixmap(frame):
    # Convert frame to QImage
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    qimage = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                    QImage.Format_RGB888)
    image = qimage.scaled(320, 240, Qt.KeepAspectRatio)
    return QPixmap.fromImage(image)

def load_leaderboard_widget():
    filename = 'designer/leaderboard_list_item.ui'
    loader = QUiLoader()
    #loader.registerCustomWidget(QVideoWidget)

    # read file
    filepath = os.path.join(os.path.dirname(__file__), filename)
    file = QFile(filepath)
    file.open(QFile.ReadOnly)

    # load window
    return loader.load(file)


class LeaderboardWidget(QListWidget):
    def __init__(self, simulations, parent=None):
        """ Initialised with an iterable of simulation dicts to display """

        super().__init__(parent)

        # setup list item styles
        self.stylesheets = [ "background-color: #FCF7F8;", "background-color: #90C2E7;" ]

        self.setSimulations(simulations)


    def setSimulations(self, simulations):

        self.clear()

        for i, sim in enumerate(simulations):
            rgb_image = frame_to_QPixmap(sim['rgb_frame'])
            depth_image = frame_to_QPixmap(sim['depth_frame'])

            widget = load_leaderboard_widget()

            # set background color
            widget.setStyleSheet(self.stylesheets[i%2])

            # populate data
            widget.name.setText(sim['name'])
            widget.score.setText(f'score: {sim["score"]}')
            widget.time.setText(sim['time'])
            widget.rank.setText(f'#{i + 1}')

            # set images
            widget.rgb_image.setPixmap(rgb_image)
            widget.depth_image.setPixmap(depth_image)

            # add item
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.addItem(item)
            self.setItemWidget(item, widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    data = np.load('kinect_to_points/color_kinect_data.npy')
    depths = np.load('kinect_to_points/kinect_data.npy')
    depthimages = [ depth_to_depthimage(depth) for depth in depths ]

    simulations = [ {
        'name' : 'Bob Jones',
        'score' : 10.5,
        'time' : '10:00 12/15/2018',
        'rgb_frame' : data[0],
        'depth_frame' : depthimages[0]
        }, {
        'name' : 'Terry Berry',
        'score' : 9.5,
        'time' : '11:15 12/15/2018',
        'rgb_frame' : data[1],
        'depth_frame' : depthimages[1]
        }, {
        'name' : 'Bob Jones',
        'score' : 10.5,
        'time' : '10:00 12/15/2018',
        'rgb_frame' : data[0],
        'depth_frame' : depthimages[0]
        }, {
        'name' : 'Terry Berry',
        'score' : 9.5,
        'time' : '11:15 12/15/2018',
        'rgb_frame' : data[1],
        'depth_frame' : depthimages[1]
        }]
    lb = LeaderboardWidget(simulations)
    lb.resize(2000,1000)

    def change_name():
        simulations[0]['name'] = 'Another Name'
        lb.setSimulations(simulations)

    QTimer.singleShot(3000, change_name)

    lb.show()

    sys.exit(app.exec_())



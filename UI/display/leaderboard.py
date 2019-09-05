from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
from display.video_capture import QVideoWidget
from display.pyside_dynamic import loadUiWidget
from display.video_capture import QVideoWidget

image_width  = 100
image_height = 100


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
            rgb_image = np.array(sim['rgb'], dtype=np.uint8)
            depth_image = np.array(sim['depth'], dtype=np.uint8)

            widget = loadUiWidget(
                'leaderboard_list_item.ui',
                customWidgets=[QVideoWidget]
            )

            # set background color
            widget.setStyleSheet(self.stylesheets[i % 2])

            # populate data
            drag = sim["drag"]

            widget.name.setText(sim['name'])
            widget.score.setText(f'drag: {drag:.2f}')
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

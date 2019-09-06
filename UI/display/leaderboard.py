from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtUiTools import QUiLoader
import cv2, sys, time, os
import numpy as np
import settings
from display.video_capture import QVideoWidget
from display.pyside_dynamic import loadUiWidget
from display.video_capture import QVideoWidget

image_width = 100
image_height = 100


class LeaderboardListItem(QWidget):
    clicked = Signal(int)

    def __init__(self, rank, parent=None):

        super().__init__(parent)

        self.rank = rank

        widget = loadUiWidget('leaderboard_list_item.ui',
                              customWidgets=[QVideoWidget])

        self.widget = widget
        self.widget.setObjectName("ListWidget")

        # Add widget and set parent
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.widget)
        self.layout().setMargin(0)

        self.selected = False
        self.active = False

    def setActive(self, bool):
        self.active = bool
        self._updateBorder()

    def setSelected(self, bool):
        self.selected = bool
        self._updateBorder()

    def _updateBorder(self):
        if self.selected and self.active:
            self.widget.setStyleSheet("#ListWidget { border: 5px solid blue; }");
        elif self.active:
            self.widget.setStyleSheet("#ListWidget { border: 5px solid green; }");
        else:
            self.widget.setStyleSheet("#ListWidget { }");

    def setSimulation(self, sim):
        rgb_image = np.array(sim['rgb'], dtype=np.uint8)
        depth_image = np.array(sim['depth'], dtype=np.uint8)

        # populate data
        drag = sim["drag"]

        self.widget.name.setText(sim['name'])
        self.widget.score.setText(f'drag: {drag:.2f}')
        self.widget.rank.setText(f'#{self.rank + 1}')

        # set image dimensions
        scale = 2
        self.widget.rgb_image.setFixedHeight(image_width * scale)
        self.widget.rgb_image.setFixedWidth(image_height * scale)
        self.widget.depth_image.setFixedHeight(image_width * scale)
        self.widget.depth_image.setFixedWidth(image_height * scale)

        # set images
        self.widget.rgb_image.setImage(rgb_image)
        self.widget.depth_image.setImage(depth_image)

        self.setActive(True)

    def clearSimulation(self):
        self.widget.name.setText("")
        self.widget.score.setText("")
        self.widget.rank.setText("")
        self.widget.rgb_image.setText("")
        self.widget.depth_image.setText("")

        self.setActive(False)

    def mouseReleaseEvent(self, e):
        if self.active:
            self.clicked.emit(self.rank)
        super().mouseReleaseEvent(e)

class LeaderboardWidget(QScrollArea):
    selection_changed = Signal(int)

    def __init__(self, parent=None):
        """ Initialised with an iterable of simulation dicts to display """

        super().__init__(parent)

        self.container = QWidget(self)
        self.container.setLayout(QVBoxLayout())

        self.widgets = [
            LeaderboardListItem(rank, parent=self)
            for rank in range(settings.leaderboard_number)
        ]

        for widget in self.widgets:
            self.container.layout().addWidget(widget)
            widget.clicked.connect(self.change_selection)

        self.setWidget(self.container)

    def change_selection(self, selection):
        for widget in self.widgets:
            widget.setSelected(False)

        self.widgets[selection].setSelected(True)

        self.selection_changed.emit(selection)

    def setSimulations(self, simulations):
        for i, widget in enumerate(self.widgets):
            if i < len(simulations):
                sim = simulations[i]
                widget.setSimulation(sim)
            else:
                widget.clearSimulation()


def load_pickle(filename):
    import pickle
    with open(filename, 'rb') as handle:
        simulation = pickle.load(handle)

    return simulation


if __name__ == '__main__':
    app = QApplication(sys.argv)

    simulation = {
        'rgb': load_pickle('rgb_image.pickle'),
        'depth': load_pickle('depth_image.pickle'),
        'name': 'MARK',
        'drag': 34.3434
    }

    simulations = [simulation, simulation]

    lb = LeaderboardWidget()
    lb.setSimulations(simulations)
    lb.resize(2000, 1000)
    lb.selection_changed.connect(lambda i: print(i))

    # def change_name():
    #     simulations[0]['name'] = 'Another Name'
    #     lb.setSimulations(simulations)

    # QTimer.singleShot(3000, change_name)

    lb.show()

    #item = LeaderboardListItem(1)
    #item.setSimulation(simulation)
    #item.show()

    sys.exit(app.exec_())

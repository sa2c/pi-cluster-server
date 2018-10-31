from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import datetime
import calendar
from qt_utils import load_ui
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from video_capture import QVideoWidget, frame_to_qimage
from detail_form import DetailForm
from leaderboard import LeaderboardWidget

nmeasurements = 20


class ControlWindow(QMainWindow):
    def __init__(self, simulations, parent=None):
        self.offset = [0, 0]
        self.scale = [1, 1]

        super().__init__(parent)
        self.ui = load_ui('designer/control_panel.ui')
        self.setCentralWidget(self.ui)

        self.ui.capture_button.released.connect(self.capture_action)
        self.ui.process_button.released.connect(self.run_cfd_action)
        self.ui.details_button.released.connect(self.fill_in_details_action)

        self.background = measure_depth(nmeasurements)

        self.calibrate()

        # create viewfinder
        self.viewfinder = load_ui('designer/viewfinder.ui')
        self.viewfinder.show()

        # create leaderboard
        self.simulations = simulations
        self.leaderboard = LeaderboardWidget(self.best_simulations())
        self.leaderboard.show()

        self.reset_action()

    def best_simulations(self):
        # returns all simulations for now
        return self.simulations.values()

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

        # set images
        qimage = frame_to_qimage(rgb_frame)
        self.ui.captured_rgb.setImage(qimage)

        qimage = frame_to_qimage(depthimage)
        self.ui.captured_depth.setImage(qimage)

    def calibrate(self):
        self.background = measure_depth(nmeasurements)

    def fill_in_details_action(self):
        prev_name = self.current_name
        prev_email = self.current_email

        dialog = DetailForm(self)
        accepted = dialog.exec()

        if not accepted:
            self.name_changed_action(prev_name, prev_email)
            print('name change cancelled')

    def run_cfd_action(self):
        index = get_epoch()
        self.simulations[index] = {
            'index': index,
            'name': self.current_name,
            'email': self.current_email,
        }
        queue_run(index)

    def get_epoch():
        now = datetime.datetime.utcnow()
        timestamp = calendar.timegm(now.utctimetuple())
        return timestamp

    def reset_action(self):
        self.name_changed_action('', '')

    def name_changed_action(self, name, email):
        self.current_name = name
        self.current_email = email
        self.viewfinder.name.setText(f'Name: {name}')

    def keyPressEvent(self, event):

        motion = 1
        large_motion = 10

        if event.text() == 'k':
            self.offset[1] -= large_motion
            self.process_image()
            event.accept()
        elif event.text() == 'j':
            self.offset[1] += large_motion
            self.process_image()
            event.accept()
        elif event.text() == 'h':
            self.offset[0] -= large_motion
            self.process_image()
            event.accept()
        elif event.text() == 'l':
            self.offset[0] += large_motion
            self.process_image()
            event.accept()
        elif event.text() == 'K':
            self.offset[1] -= motion
            self.process_image()
            event.accept()
        elif event.text() == 'J':
            self.offset[1] += motion
            self.process_image()
            event.accept()
        elif event.text() == 'H':
            self.offset[0] -= motion
            self.process_image()
            event.accept()
        elif event.text() == 'L':
            self.offset[0] += motion
            self.process_image()
            event.accept()

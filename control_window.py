from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import datetime
import calendar
from pyside_dynamic import loadUi
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from video_capture import QVideoWidget, frame_to_qimage
from detail_form import DetailForm
from leaderboard import LeaderboardWidget
from queue_run import queue_run
from viewfinder import ViewfinderDialog
from cluster_run import queue_run, RunCompleteWatcher
from color_calibration import ColorCalibration

nmeasurements = 20


class ControlWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = [0, 0]
        self.scale = [0.95, 0.9]

        # set control window size
        self.resize(1920, 1080)

        self.contour = np.array([[]])

        self.ui = QWidget()
        loadUi(
            'designer/control_panel.ui',
            self.ui,
            customWidgets={'QVideoWidget': QVideoWidget})
        self.setCentralWidget(self.ui)

        # instance variables
        self.outline = None
        self.transformed_outline = None
        self.simulations = {}

        self.ui.capture_button.released.connect(self.capture_action)
        self.ui.process_button.released.connect(self.run_cfd_action)
        self.ui.details_button.released.connect(self.fill_in_details_action)
        self.ui.calibrate_button.released.connect(self.calibrate)
        self.ui.show_button.released.connect(self.show_capture_action)
        self.ui.toggle_view_button.released.connect(self.toggle_views)
        self.ui.color_calibrate_button.released.connect(
            self.calibrate_color_action)

        self.background = measure_depth(nmeasurements)

        self.calibrate()

        # create viewfinder
        self.viewfinder = ViewfinderDialog()
        self.viewfinder.show()

        # create color calibration window
        self.calibration_window = ColorCalibration()
        self.calibration_window.color_changed.connect(set_color_scale)

        # create file system watcher
        self.run_watcher = RunCompleteWatcher(self)
        self.run_watcher.completed.connect(self.run_completed)

        self.reset_action()

    def toggle_views(self):
        if self.viewfinder.leftStack.currentIndex() == 1:
            self.viewfinder.switch_to_viewfinder()
            self.ui.toggle_view_button.setText('Simulation View')
        else:
            self.viewfinder.switch_to_simulation_view()
            self.ui.toggle_view_button.setText('Viewfinder')

    def run_completed(self, index):
        print(f'finished {index}')
        self.viewfinder.show_completed(index)
        self.leaderboard.update(self.best_simulations())

    def best_simulations(self):
        # returns all simulations for now
        return self.simulations.values()

    def show_capture_action(self):
        # get rgb image with current transformed outline
        rgb_frame = np.copy(self.capture_rgb_frame)
        cv2.drawContours(rgb_frame, [self.transformed_outline], -1,
                         (0, 0, 255), 2)

        # set images
        qimage = frame_to_qimage(rgb_frame)
        self.viewfinder.main_video.setStaticImage(qimage)

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

        self.outline, self.transformed_outline = contour_to_outline(
            contour, self.scale, self.offset)

        # add contour to images
        cv2.drawContours(depthimage, [self.outline], -1, (0, 0, 255), 2)
        cv2.drawContours(rgb_frame, [self.transformed_outline], -1,
                         (0, 0, 255), 2)

        # Remember the contour for submission of the run
        self.contour = self.transformed_outline

        # set images
        qimage = frame_to_qimage(rgb_frame)
        self.ui.captured_rgb.setImage(qimage)

        qimage = frame_to_qimage(depthimage)
        self.ui.captured_depth.setImage(qimage)

    def calibrate(self):
        self.background = measure_depth(nmeasurements)

    def calibrate_color_action(self):
        old = get_color_scale()

        accepted = self.calibration_window.exec()

        if not accepted:
            set_color_scale(old)

    def fill_in_details_action(self):
        prev_name = self.current_name
        prev_email = self.current_email

        dialog = DetailForm(self)
        accepted = dialog.exec()

        if not accepted:
            self.name_changed_action(prev_name, prev_email)
            print('name change cancelled')

    def run_cfd_action(self):
        index = self.get_epoch()
        self.simulations[index] = {
            'index': index,
            'name': self.current_name,
            'email': self.current_email,
        }
        queue_run(self.contour, index)

    def get_epoch(self):
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
        elif event.text() == '+':
            self.scale[0] += 0.05
            self.scale[1] += 0.05
            self.process_image()
            event.accept()
        elif event.text() == '-':
            self.scale[0] -= 0.05
            self.scale[1] -= 0.05
            self.process_image()
            event.accept()

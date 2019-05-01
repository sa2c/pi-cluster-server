from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import datetime
import calendar
import cv2, sys, time, os
import numpy as np
import kinectlib.kinectlib as kinect
from display.pyside_dynamic import loadUiWidget
from display.video_capture import QVideoWidget
from display.detail_form import DetailForm
from display.leaderboard import LeaderboardWidget
from display.viewfinder import ViewfinderDialog
from display.color_calibration import ColorCalibration
from display.simulation_selector import SimulationSelector
from display.matplotlib_widget import PlotCanvas
from computedrag import compute_drag_for_simulation
from images_to_pdf.pdfgen import PDFPrinter
from cluster_manager import *
from postplotting import vtk_to_plot
import controller


class ControlWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.controller = controller.Controller()

        # set control window size
        self.resize(1920, 1080)

        self.ui = loadUiWidget(
            'designer/control_panel.ui',
            customWidgets=[QVideoWidget, SimulationSelector])
        self.setCentralWidget(self.ui)

        # instance variables
        self.ui.capture_button.released.connect(self.capture_action)
        self.ui.process_button.released.connect(self.run_cfd_action)
        self.ui.details_button.released.connect(self.fill_in_details_action)
        self.ui.calibrate_button.released.connect(self.controller.calibrate)
        self.ui.show_button.released.connect(self.show_capture_action)
        self.ui.color_calibrate_button.released.connect(
            self.calibrate_color_action)
        
        # create viewfinder
        self.viewfinder = ViewfinderDialog()
        self.viewfinder.show()
        self.viewfinder.start_progress_checking()

        # connect view selector
        self.ui.view_selector.simulation_view_changed.connect(
            self.viewfinder.switch_to_simulation_view)
        self.ui.view_selector.viewfinder_view_selected.connect(
            self.viewfinder.switch_to_viewfinder)

        # create color calibration window
        self.calibration_window = ColorCalibration()
        self.calibration_window.color_changed.connect(kinect.set_color_scale)

        # create file system watcher
        self.run_watcher = RunCompleteWatcher(self)
        self.run_watcher.started.connect(self.run_started)
        self.run_watcher.completed.connect(self.run_completed)

        self.reset_action()

    def run_completed(self, index):
        print(f'finished {index}')
        self.viewfinder.finish_simulation(index)
        self.ui.view_selector.simulation_finished_action(index)

        self.controller.run_completed(index)

        self.leaderboard.update(self.controller.best_simulations())

    def run_started(self, signal):
        index, slot = signal
        print(f'started {index} in {slot}')
        self.viewfinder.start_simulation(index, slot - 1)

    def show_capture_action(self):
        self.ui.view_selector.set_to_viewfinder()
        if self.viewfinder.ui.main_video.dynamic_update:
            # Show capture
            rgb_frame, depthimage = self.__get_static_images(
                contour_on_rgb=False)

            # set images
            self.viewfinder.ui.main_video.setStaticImage(rgb_frame)
            self.viewfinder.ui.depth_video.setStaticImage(depthimage)

            # change button text
            self.ui.show_button.setText('&Resume Video')
            self.ui.capture_button.setEnabled(False)
        else:
            # resume video feed
            self.viewfinder.ui.main_video.resumeDynamicUpdate()
            self.viewfinder.ui.depth_video.resumeDynamicUpdate()
            self.ui.capture_button.setEnabled(True)

            # change button text
            self.ui.show_button.setText('&Show Capture')

    def capture_action(self):

        rgb_frame, depthimage = self.controller.capture()

        # set images
        self.ui.captured_rgb.setImage(rgb_frame)
        self.ui.captured_depth.setImage(depthimage)
    
    def calibrate_color_action(self):
        old = kinect.get_color_scale()

        accepted = self.calibration_window.exec()

        if not accepted:
            kinect.set_color_scale(old)

    def fill_in_details_action(self):
        prev_name = self.controller.current_name
        prev_email = self.controller.current_email

        dialog = DetailForm(self)
        accepted = dialog.exec()

        if not accepted:
            self.name_changed_action(prev_name, prev_email)
            print('name change cancelled')

    def run_cfd_action(self):

        index = self.get_epoch()

        # save simulation details for later
        rgb_frame, depthimage = self.__get_static_images()
        simulation = {
            'index': index,
            'name': self.current_name,
            'email': self.current_email,
            'rgb': rgb_frame,
            'depth': self.capture_depth,
            'background': self.background,
            'contour': self.contour
        }

        save_simulation(simulation)

        self.viewfinder.queue_simulation(index, self.current_name)
        queue_run(self.contour, simulation['index'])

    def get_epoch(self):
        now = datetime.datetime.utcnow()
        timestamp = calendar.timegm(now.utctimetuple())
        return timestamp

    def reset_action(self):
        self.name_changed_action('', '')

    def name_changed_action(self, name, email):
        print(name,email)
        self.controller.current_name = name
        self.controller.current_email = email
        self.viewfinder.ui.name.setText(f'Name: {name}')
        self.viewfinder.ui.email.setText(f'e-mail (optional): {email}')

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
        elif event.text() == 'd':
            # show details
            self.fill_in_details_action()
        elif event.text() == 'c':
            self.capture_action()
        elif event.text() == 's' or event.text() == 'r':
            # Show or resume
            self.show_capture_action()
        elif event.text() == 'g':
            self.run_cfd_action()
        elif event.text() == 'v':
            self.toggle_views()

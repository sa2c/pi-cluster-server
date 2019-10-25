from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import kinectlib.kinectlib as kinect
from display.pyside_dynamic import loadUiWidget
from display.video_capture import QVideoWidget
from display.detail_form import DetailForm
from display.color_calibration import ColorCalibration
import simulation_proxy


class ControlWindow(QMainWindow):
    def __init__(self, controller, viewfinder, video_source, parent=None):
        super().__init__(parent)

        self.controller = controller

        # set control window size
        self.resize(1920, 1080)

        self.ui = loadUiWidget(
            'control_panel.ui',
            customWidgets=[QVideoWidget])
        self.setCentralWidget(self.ui)

        # connect signals
        self.ui.capture_button.released.connect(self.capture_action)
        self.ui.process_button.released.connect(self.run_cfd_action)
        self.ui.print_button.released.connect(self.print_action)
        self.ui.details_button.released.connect(self.fill_in_details_action)
        self.ui.calibrate_button.released.connect(self.controller.calibrate)
        self.ui.show_button.released.connect(self.show_capture_action)
        self.ui.color_calibrate_button.released.connect(
            self.calibrate_color_action)

        # create viewfinder
        self.viewfinder = viewfinder
        self.viewfinder.show()

        # create color calibration window
        self.calibration_window = ColorCalibration()
        self.calibration_window.color_changed.connect(
            kinect.device.set_color_scale)

        self.reset_action()

        # connect video sources
        video_source.changeFramePixmap.connect(self.ui.video_rgb.setImage)
        video_source.changeDepthPixmap.connect(self.ui.video_depth.setImage)



    def show_capture_action(self):
        if self.viewfinder.ui.main_video.dynamic_update:
            # Show capture
            rgb_frame, depthimage = self.controller.get_capture_images()

            # set images
            self.viewfinder.set_static(rgb_frame, depthimage)

            # change button text
            self.ui.show_button.setText('&Resume Video')
            self.ui.capture_button.setEnabled(False)
        else:
            # resume video feed
            self.viewfinder.resume_dynamic()
            self.ui.capture_button.setEnabled(True)

            # change button text
            self.ui.show_button.setText('&Show Capture')

    def capture_action(self):
        rgb_frame, depthimage = self.controller.capture()

        # set images
        self.ui.captured_rgb.setImage(rgb_frame)
        self.ui.captured_depth.setImage(depthimage)

    def calibrate_color_action(self):
        old = kinect.device.get_color_scale()

        accepted = self.calibration_window.exec()

        if not accepted:
            kinect.device.set_color_scale(old)

    def print_action(self):
        self.controller.print_simulation(index)

    def fill_in_details_action(self):
        prev_name, prev_email = self.controller.get_user_details()

        dialog = DetailForm(self)
        accepted = dialog.exec()

        if not accepted:
            self.name_changed_action(prev_name, prev_email)
            print('name change cancelled')

    def run_cfd_action(self):
        index = self.controller.start_simulation()

    def reset_action(self):
        self.name_changed_action('', '')

    def name_changed_action(self, name, email):
        self.controller.set_user_details(name, email)
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

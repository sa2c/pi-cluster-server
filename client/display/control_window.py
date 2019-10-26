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

        self.ui = loadUiWidget('control_panel.ui',
                               customWidgets=[QVideoWidget])
        self.setCentralWidget(self.ui)

        # connect signals
        self.ui.capture_button.released.connect(self.capture_action)
        self.ui.process_button.released.connect(self.run_cfd_action)
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
            rgb_with_contour = self.controller.get_rgb_image_with_scaled_contour(rgb_frame)
            self.viewfinder.set_static(rgb_with_contour, depthimage)

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

        # set depth
        self.ui.captured_depth.setImage(depthimage)

        # set rgb
        self.update_rgb_image(rgb_frame)

    def update_rgb_image(self, rgb_frame=None):
        if rgb_frame is None:
            rgb_frame, depthimage = self.controller.get_capture_images()

        rgb_with_contour = self.controller.get_rgb_image_with_scaled_contour(rgb_frame)

        self.ui.captured_rgb.setImage(rgb_with_contour)

    def calibrate_color_action(self):
        old = kinect.device.get_color_scale()

        accepted = self.calibration_window.exec()

        if not accepted:
            kinect.device.set_color_scale(old)

    def fill_in_details_action(self):
        prev_name, prev_email = self.controller.get_user_details()

        dialog = DetailForm(self)
        accepted = dialog.exec()

        if not accepted:
            self.name_changed_action(prev_name, prev_email)
            print('name change cancelled')

        return accepted

    def run_cfd_action(self):
        name, email = self.controller.get_user_details()
        capture_frame, capture_depth = self.controller.get_capture_images()

        # capture frame if there is none
        if capture_frame is None:
            self.capture_action()

        # fill in details if there are none
        response = True
        if name is not None and len(name) == 0:
            response = self.fill_in_details_action()

        # submit unless user has pressed cancel
        if response:
            print("Submitting simulation...")
            index = self.controller.start_simulation()
            print("Simulation submitted...")
            self.controller.set_user_details('', '')

    def reset_action(self):
        self.name_changed_action('', '')

    def name_changed_action(self, name, email):
        self.controller.set_user_details(name, email)
        self.viewfinder.ui.name.setText(f'Name: {name}')
        self.viewfinder.ui.email.setText(f'e-mail (optional): {email}')

    def keyPressEvent(self, event):
        if event.text() == 'k':
            self.controller.move_offset_up()
        elif event.text() == 'j':
            self.controller.move_offset_down()
        elif event.text() == 'h':
            self.controller.move_offset_left()
        elif event.text() == 'l':
            self.controller.move_offset_right()
        elif event.text() == 'K':
            self.controller.move_offset_up(large=True)
        elif event.text() == 'J':
            self.controller.move_offset_down(large=True)
        elif event.text() == 'H':
            self.controller.move_offset_left(large=True)
        elif event.text() == 'L':
            self.controller.move_offset_right(large=True)
        elif event.text() == '+':
            self.controller.scale_up(0.01)
        elif event.text() == '_':
            self.controller.scale_down(0.01)
        elif event.text() == '=':
            self.controller.scale_up(0.05)
        elif event.text() == '-':
            self.controller.scale_down(0.05)
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

        self.update_rgb_image()
        event.accept()

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import datetime
import calendar
from pyside_dynamic import loadUiWidget
import cv2, sys, time, os
import numpy as np
from kinect_to_points.kinect_lib import *
from video_capture import QVideoWidget
from detail_form import DetailForm
from leaderboard import LeaderboardWidget
from queue_run import queue_run
from viewfinder import ViewfinderDialog
from cluster_run import queue_run, RunCompleteWatcher, run_filepath, save_simulation, load_drag, save_drag
from color_calibration import ColorCalibration
from simulation_selector import SimulationSelector
from cfd.computedrag import compute_drag_for_simulation
from images_to_pdf.pdfgen import PDFGenerator
from cluster_run import *
from matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot

nmeasurements = 20


class ControlWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.offset = [0, 0]
        self.scale = [1.0, 1.0]
        self.drag = load_drag()
        self.current_name = 'Simulation'

        # set control window size
        self.resize(1920, 1080)

        self.contour = np.array([[]])

        self.ui = loadUiWidget(
            'designer/control_panel.ui',
            customWidgets=[QVideoWidget, SimulationSelector])
        self.setCentralWidget(self.ui)

        # instance variables
        self.outline = None
        self.transformed_outline = None
        self.ui.capture_button.released.connect(self.capture_action)
        self.ui.process_button.released.connect(self.run_cfd_action)
        self.ui.details_button.released.connect(self.fill_in_details_action)
        self.ui.calibrate_button.released.connect(self.calibrate)
        self.ui.show_button.released.connect(self.show_capture_action)
        self.ui.color_calibrate_button.released.connect(
            self.calibrate_color_action)

        self.background = measure_depth(nmeasurements)

        self.calibrate()

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
        self.calibration_window.color_changed.connect(set_color_scale)

        # create file system watcher
        self.run_watcher = RunCompleteWatcher(self)
        self.run_watcher.started.connect(self.run_started)
        self.run_watcher.completed.connect(self.run_completed)

        self.reset_action()

    def run_completed(self, index):
        print(f'finished {index}')
        self.viewfinder.finish_simulation(index)
        self.ui.view_selector.simulation_finished_action(index)

        np.append(self.drag, [index, compute_drag_for_simulation(index)])
        save_drag(self.drag)

        simulation = load_simulation(index)

        rgb = simulation['rgb']
        depth = simulation['depth']
        background = simulation['background']

        rgb, depth = self.__get_static_images_with_input(
            rgb, depth, background, contour_on_rgb=True)

        #a = PlotCanvas()
        #vtk_filename = run_filepath(index, 'elmeroutput0010.vtk')
        #vtk_to_plot(a, vtk_filename, 16, True, False, True, None)
        #a.figure
        #data = np.fromstring(a.canvas.tostring_rgb(), dtype=np.uint8, sep='')
        #data = data.reshape(fig.canvas.get_width_height()[::-1] + (3, ))

        #a = PlotCanvas()
        #vtk_to_plot(a, vtk_filename, 16, True,False,True,None)

        #generator = PDFGenerator('test_pil.pdf', rgb, depth, data, data,
        #                         'Test user with PIL', 69)
        #generator.run()

        self.leaderboard.update(self.best_simulations())

    def run_started(self, signal):
        index, slot = signal
        print(f'started {index} in {slot}')
        self.viewfinder.start_simulation(index, slot - 1)

    def best_simulations(self):
        nsims = 10
        drag = np.array(self.drag)
        drag_sorted_indices = np.argsort(drag[:, 1])
        drag_sorted_indices.reverse()
        best_indices = drag[drag_sorted_indices[0:nsims], :]

        simulations = {}
        for index in best_indices:
            simulations[index] = load_simulation(index)

        return simulations

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
        self.capture_depth = measure_depth()
        self.capture_rgb_frame = get_video()

        self.process_image()

    def process_image(self):
        rgb_frame, depthimage = self.__get_static_images()

        # set images
        self.ui.captured_rgb.setImage(rgb_frame)

        self.ui.captured_depth.setImage(depthimage)

    def __get_static_images_with_input(self,
                                       rgb_frame,
                                       capture_depth,
                                       background,
                                       contour_on_rgb=True):
        rgb_frame = np.copy(rgb_frame)

        # set rgb image visible
        clean_depth = remove_background(capture_depth, background)
        depthimage = depth_to_depthimage(capture_depth)

        # compute contour
        contour = normalised_depth_to_contour(clean_depth)

        self.outline, self.transformed_outline = contour_to_outline(
            contour, self.scale, self.offset)

        # add contour to images
        cv2.drawContours(depthimage, [self.outline], -1, (0, 0, 255), 2)

        if contour_on_rgb:
            cv2.drawContours(rgb_frame, [self.transformed_outline], -1,
                             (0, 0, 255), 2)

        # Remember the contour for submission of the run
        self.contour = self.transformed_outline

        return rgb_frame, depthimage

    def __get_static_images(self, contour_on_rgb=True):
        rgb_frame, depthiamge = self.__get_static_images_with_input(
            self.capture_rgb_frame,
            self.capture_depth,
            self.background,
            contour_on_rgb=True)
        return rgb_frame, depthiamge

    def calibrate(self):
        self.background = measure_depth(nmeasurements)
        #XXXX.set_mask(self.background)

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
        self.current_name = name
        self.current_email = email
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

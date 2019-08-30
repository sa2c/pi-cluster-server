import numpy as np
import kinectlib.kinectlib as kinect
from images_to_pdf.pdfgen import PDFPrinter
import cluster_manager
from display.matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot
import matplotlib.pyplot as plt

from settings import nmeasurements


class Controller(object):
    def __init__(self, parent=None):

        # instance variables
        self.offset = [15, 0]
        self.scale = [1.0, 1.0]
        self.current_name = 'Simulation'
        self.current_email = ''
        self.outline = None
        self.transformed_outline = None
        self.contour = np.array([[]])

        self.calibrate()

    def calibrate(self):
        self.background = kinect.measure_depth(nmeasurements)

    def capture(self):
        rgb, rgb_with_outline, depth, outline = kinect.images_and_outline(
            self.background,
            self.scale,
            self.offset)

        # Set as current capture images
        self.capture_frame = rgb
        self.capture_frame_with_outline = rgb_with_outline
        self.capture_depth = depth

        # Set contour for simulation
        self.contour = outline

        return self.capture_frame, self.capture_depth

    def capture_and_show(self):
        self.capture()
        plt.imshow(self.capture_depth)
        plt.show()

    def get_capture_images(self):
        return self.capture_frame, self.capture_depth

    def set_user_details(self, name, email):
        self.current_name = name
        self.current_email = email

    def get_user_details(self):
        return self.current_name, self.current_email

    def start_simulation(self):

        # save simulation details for later

        index = cluster_manager.dispatch_simulation({
            'name': self.current_name,
            'email': self.current_email,
            'rgb': self.capture_frame,
            'rgb_with_contour': self.capture_frame_with_outline,
            'depth': self.capture_depth,
            'background': self.background,
            'contour': self.contour
        })

        return index

    def best_simulations(self):
        nsims = 10
        return cluster_manager.best_simulations(nsims)

    def list_simulations(self):
        return cluster_manager.all_available_indices_and_names()

    def get_activity(self):
        return cluster_manager.fetch_activity()

    def get_simulation(self, index):
        return cluster_manager.load_simulation(index)
    
    def get_simulation_name(self, index):
        return cluster_manager.load_simulation_name(index)

    def get_completion_percentage(self, index):
        return cluster_manager.get_run_completion_percentage(index)

    def restart_slot(self, slot):
        return cluster_manager.restart_slot(slot)

    def print_running_jobs(self):
        signals = cluster_manager.get_signals()
        starts = []
        ends = []
        for signal in signals:
            index, signal_type, _ = cluster_manager.get_signal_info(signal)
            if signal_type == 'start':
                starts += [index]
            if signal_type == 'end':
                ends += [index]
        for index in starts:
            if index not in ends:
                print(
                    index,
                    self.get_simulation_name(index),
                    self.get_completion_percentage(index)
                )



    def print_simulation(self, index, send_to_printer = True):
        simulation = cluster_manager.load_simulation(index)
        rgb = simulation['rgb']
        depth = simulation['depth']
        rgb = simulation['rgb_with_contour']

        a = PlotCanvas()
        vtk_filename = cluster_manager.run_filepath(index, 'elmeroutput0010.vtk')
        vtk_to_plot(a, vtk_filename, 16, True, False, True, None)
        data = np.fromstring(a.tostring_rgb(), dtype=np.uint8, sep='')
        data = data.reshape(a.get_width_height()[::-1] + (3, ))

        a = PlotCanvas()
        vtk_to_plot(a, vtk_filename, 16, True,False,True,None)

        filename = str(index)+'.pdf'

        generator = PDFPrinter(filename, rgb, depth, data, data,
                                simulation['name'], simulation['drag'])
        generator.run(send_to_printer = send_to_printer)

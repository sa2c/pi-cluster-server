import numpy as np
import kinectlib.kinectlib as kinect
import cluster_manager
import datetime
import calendar
from computedrag import compute_drag_for_simulation
from images_to_pdf.pdfgen import PDFPrinter
from display.matplotlib_widget import PlotCanvas
from postplotting import vtk_to_plot
import matplotlib.pyplot as plt

from settings import nmeasurements




class Controller(object):
    def __init__(self, parent=None):

        # instance variables
        self.offset = [0, 0]
        self.scale = [1.0, 1.0]
        self.current_name = 'Simulation'
        self.current_email = ''
        self.outline = None
        self.transformed_outline = None
        self.contour = np.array([[]])

        self.drag = np.empty((0,2))
        self.list_drag()

        if self.kinect_connected():
            self.calibrate()

    def kinect_connected(self):
        return kinect.freenect_loaded

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

        index = self.get_epoch()

        # save simulation details for later
        simulation = {
            'index': index,
            'name': self.current_name,
            'email': self.current_email,
            'rgb': self.capture_frame,
            'rgb_with_contour': self.capture_frame_with_outline,
            'depth': self.capture_depth,
            'background': self.background,
            'contour': self.contour
        }

        cluster_manager.save_simulation(simulation)

        cluster_manager.queue_run(self.contour, simulation['index'])

        return index

    def best_simulations(self):
        nsims = 10
        drag = np.array(self.drag)
        nsims = min(10, drag.shape[0])
        drag_sorted_indices = np.argsort(drag[:, 1])
        best_indices = drag[drag_sorted_indices[0:nsims], 0]

        simulations = []
        for index in best_indices:
            i = int(index)
            simulations.append(cluster_manager.load_simulation(i))

        return simulations

    def get_epoch(self):
        now = datetime.datetime.utcnow()
        timestamp = calendar.timegm(now.utctimetuple())
        return timestamp

    def calculate_drag(self, index):
        drag = compute_drag_for_simulation(index)
        
        simulation = cluster_manager.load_simulation(index)
        simulation['score'] = drag
        simulation['index'] = index        
        cluster_manager.save_simulation(simulation)        
        return drag

    def simulation_postprocess(self, index):
        drag = self.calculate_drag(index)
        self.drag = np.append(self.drag, np.array([[index, drag]]), axis = 0)

    def list_drag(self):
        for index, name in self.list_simulations():
            drag = self.calculate_drag(index)
            self.drag = np.append(self.drag, np.array([[index, drag]]), axis = 0)
            simulation = cluster_manager.load_simulation(index)

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
        vtk_to_plot(a, vtk_filename, 1, True, False, True, None)
        data = np.fromstring(a.tostring_rgb(), dtype=np.uint8, sep='')
        data = data.reshape(a.get_width_height()[::-1] + (3, ))

        a = PlotCanvas()
        vtk_to_plot(a, vtk_filename, 1, True,False,True,None)

        filename = str(index)+'.pdf'

        generator = PDFPrinter(filename, rgb, depth, data, data,
                                simulation['name'], simulation['drag'])
        generator.run(send_to_printer = send_to_printer)

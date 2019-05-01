import numpy as np
import kinectlib.kinectlib as kinect
import cluster_manager

from settings import nmeasurements


class Controller(object):
    def __init__(self, parent=None):

        # instance variables
        self.offset = [0, 0]
        self.scale = [1.0, 1.0]
        self.drag = cluster_manager.load_drag()
        self.current_name = 'Simulation'
        self.outline = None
        self.transformed_outline = None
        self.contour = np.array([[]])

        self.calibrate()

    def calibrate(self):
        self.background = kinect.measure_depth(nmeasurements)

    def capture(self):
        rgb_frame, depthimage, outline = kinect.images_and_outline(
            self.background,
            self.scale,
            self.offset,
            contour_on_rgb=True)
        
        # Set contour for simulation
        self.contour = outline

        return rgb_frame, depthimage

    def run_completed(self, index):
        simulation = cluster_manager.load_simulation(index)

        rgb = simulation['rgb']
        depth = simulation['depth']
        background = simulation['background']

        np.append(self.drag, [index, cluster_manager.compute_drag_for_simulation(index)])
        cluster_manager.save_drag(self.drag)

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

        #generator = PDFPrinter('test_pil.pdf', rgb, depth, data, data,
        #                         'Test user with PIL', 69)
        #generator.run()

    def best_simulations(self):
        nsims = 10
        drag = np.array(self.drag)
        drag_sorted_indices = np.argsort(drag[:, 1])
        drag_sorted_indices.reverse()
        best_indices = drag[drag_sorted_indices[0:nsims], :]

        simulations = {}
        for index in best_indices:
            simulations[index] = cluster_manager.load_simulation(index)

        return simulations
import os
import shutil
from controller import Controller
import settings
import cluster_manager
from tempfile import mkdtemp

from computedrag import compute_drag_for_simulation 

tmpdir = mkdtemp()+'/'

class TestSimulation(object):

    def setup(self):
        self.controller = Controller()

        settings.cluster_path = mkdtemp()+'/'
        settings.cluster_address = 'localhost'
        cluster_manager.cluster_path = settings.cluster_path
        cluster_manager.cluster_address = 'localhost'

        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)
        os.makedirs(settings.cluster_path+'/inbox')
        os.makedirs(settings.cluster_path+'/signal')
        os.makedirs(settings.cluster_path+'/signal_out')
        os.makedirs(settings.cluster_path+'/outbox')

        if not os.path.exists('signal'):
            os.makedirs('signal')

        self.complete_index = '1234'

        self.complete_runpath = 'outbox/run' + self.complete_index
        if os.path.exists(self.complete_runpath):
            shutil.rmtree(self.complete_runpath)
        os.makedirs(self.complete_runpath)
        shutil.copy('test/data/elmeroutput0010.vtk', self.complete_runpath)
        shutil.copy('test/data/test.poly', self.complete_runpath)

    def teardown(self):
        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)

        shutil.rmtree(self.complete_runpath)


class TestController(TestSimulation):

    def test_init(self):
        assert self.controller.offset == [0, 0]
        assert self.controller.scale == [1.0, 1.0]
        assert len(self.controller.contour.shape) == 2

        assert isinstance(self.controller.current_name, str)

        assert self.controller.background.shape == (480, 640)

    def test_calibrate(self):
        self.controller.background = None
        self.controller.calibrate()

        assert self.controller.background.shape == (480, 640)

    def test_capture(self):
        frame, depth_rgb = self.controller.capture()

        assert frame.shape == (480, 640, 3)
        assert depth_rgb.shape == (480, 640, 3)

    def test_get_user_details(self):
        frame, depth_rgb = self.controller.capture()

        assert frame.shape == (480, 640, 3)
        assert depth_rgb.shape == (480, 640, 3)

    def test_start_simulation(self):
        # Get the background
        self.controller.calibrate()
        frame, depth_rgb = self.controller.capture()
        self.controller.name_changed('Tester', 'anemail@dotcom.com')

        index = self.controller.start_simulation()

        assert os.path.exists(settings.cluster_path+'inbox')
        assert os.path.exists(settings.cluster_path+'inbox/run'+str(index))
        assert os.path.exists(settings.cluster_path+'signal/run'+str(index))

        loaded_simulation = cluster_manager.load_simulation(index)

        assert loaded_simulation['name'] == 'Tester'

        shutil.rmtree('outbox/run'+str(index))
        shutil.rmtree(settings.cluster_path+'inbox/run'+str(index))
        shutil.rmtree(settings.cluster_path+'signal/run'+str(index))

    def test_postprocess(self):
        assert True


class TestController(TestSimulation):
    
    def test_compute_drag(self):
        drag = compute_drag_for_simulation(self.complete_index)
        assert drag == 180.0

import os, shutil
from tempfile import mkdtemp
import numpy as np
from fabric import Connection
import pytest
import settings
import kinectlib.kinectlib as kinect
import simulation_proxy

class TestClusterManager(object):

    test_index = '0'
    test_directory = 'simulations/run' + test_index

    def setup(self):
        kinect.setup_mock()
        simulation_proxy.cluster_address = 'localhost'
        simulation_proxy.cluster_path = mkdtemp()
        settings.cluster_address = 'localhost'
        settings.cluster_path = simulation_proxy.cluster_path
        self.remote_directory = '{}/simulations/run{}'.format(
            settings.cluster_path,
            self.test_index
        )

        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)
        os.makedirs(settings.cluster_path+'/inbox')
        os.makedirs(settings.cluster_path+'/signal_in')
        os.makedirs(settings.cluster_path+'/signal_out')
        os.makedirs(settings.cluster_path+'/simulations')

        if os.path.exists(self.test_directory):
            shutil.rmtree(self.test_directory)

    def teardown(self):
        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)

        if os.path.exists(self.test_directory):
            shutil.rmtree(self.test_directory)

    def test_save_and_load_simulation(self):
        directory = simulation_proxy.run_directory(self.test_index)
        simulation_proxy.save_simulation({
            'name': 'test',
            'index': '0'
        })

        assert os.path.exists(self.test_directory+'/name.npy')
        assert os.path.exists(self.test_directory+'/simulation.npy')

        loaded_simulation = simulation_proxy.load_simulation(self.test_index)

        assert loaded_simulation['name'] == 'test'
        assert loaded_simulation['index'] == '0'

        loaded_name = simulation_proxy.load_simulation_name(self.test_index)

        assert loaded_name == 'test'

        
    def test_all_available_indices_and_names(self):
        directory = simulation_proxy.run_directory(self.test_index)
        simulation_proxy.save_simulation({
            'name': 'test',
            'index': '0'
        })
        sims = simulation_proxy.all_available_indices_and_names()

        assert len(sims) > 0
        assert len(sims[0]) == 2

    def test_run_directory(self):
        ''' Gets or Creates a run directory '''
        if os.path.exists(self.test_directory):
            shutil.rmtree(self.test_directory)

        directory = simulation_proxy.run_directory(self.test_index)

        assert directory == self.test_directory
        assert os.path.exists(directory)

        directory = simulation_proxy.run_directory(self.test_index)

        assert directory == self.test_directory
        assert os.path.exists(directory)

        shutil.rmtree(self.test_directory)

    def test_get_run_completion_percentage(self):
        ''' Checks the output file for completion percentage '''
        os.makedirs(self.remote_directory)
        percentage = simulation_proxy.get_run_completion_percentage(self.test_index)

        assert percentage == 0

        with open(self.remote_directory+"/output","w+") as f:
            f.write("MAIN:  Time: 10/100\n")
        percentage = simulation_proxy.get_run_completion_percentage(self.test_index)

        assert percentage == 10

    def test_queue_run(self):
        # Get the background
        background_depth = kinect.get_mock_background_depth()
        background_depth = kinect.threshold(background_depth)
        scale = [1.0, 1.0]
        offset = [0, 0]

        # Wind the mock forward. It should contain an object by frame 20
        kinect.mock_kinect_index = 20

        rgb_frame, rgb_frame_with_outline, depthimage, outline = kinect.images_and_outline(background_depth, scale, offset)

        simulation_proxy.queue_run(outline, self.test_index)

        assert os.path.exists(settings.cluster_path+'/inbox')
        assert os.path.exists(settings.cluster_path+'/inbox/run0')
        assert os.path.exists(settings.cluster_path+'/signal_in/run0')
        
    def test_write_outline(self):
        simulation_proxy.write_outline(
            'contour.dat',
            np.array([[[1,0],[1,1],[0,1],[0,0]]])
        )
        assert os.path.exists('contour.dat')

    def test_fetch_activity(self):
        cluster = Connection(settings.cluster_address)
        remote_name = settings.cluster_path+'/cpuloadinfo.sh'
        cluster.put('test/mock_cpuloadinfo.sh', remote=remote_name)
        simulation_proxy.fetch_activity()

    def test_signals(self):
        new_signals = simulation_proxy.get_new_signals()

        assert len(new_signals) == 0

        simulation_proxy.create_incoming_signal( 0, 'start', 3)
        new_signals = simulation_proxy.get_new_signals()

        assert len(new_signals) == 1

        signal = new_signals.pop()
        index, signal_type, slot = simulation_proxy.get_signal_info( signal )

        simulation_proxy.remove_incoming_signal(signal)

        assert index == 0
        assert signal_type == 'start'
        assert slot == 3

    def test_download_results(self):
        outbox = settings.cluster_path+'/simulations/run'+self.test_index
        if os.path.exists(outbox):
            shutil.rmtree(outbox)
        os.makedirs(outbox)
        os.makedirs(self.test_directory)

        open(outbox+'/testfile','a').close()

        simulation_proxy.download_results(self.test_index)

        assert os.path.exists(self.test_directory+'/testfile')

    @pytest.mark.skip()
    def test_queue_running(self):
        assert simulation_proxy.queue_running()








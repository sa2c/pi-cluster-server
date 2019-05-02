import kinectlib.kinectlib as kinect
import os, shutil
from tempfile import mkdtemp
import numpy as np

tmpdir = mkdtemp()+'/'

import settings
settings.cluster_address = 'localhost'
settings.cluster_path = tmpdir

import cluster_manager


class TestClusterManager(object):

    test_index = '0'
    test_directory = 'outbox/run' + test_index
    remote_directory = '{}/outbox/run{}'.format(
        settings.cluster_path,
        test_index
    )

    def setup(self):
        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)
        os.makedirs(settings.cluster_path+'/inbox')
        os.makedirs(settings.cluster_path+'/signal')
        os.makedirs(settings.cluster_path+'/signal_out')
        os.makedirs(self.remote_directory)

        if os.path.exists('signal'):
            shutil.rmtree('signal')
        os.makedirs('signal')

        if os.path.exists(self.test_directory):
            shutil.rmtree(self.test_directory)

    def teardown(self):
        if os.path.exists('signal'):
            shutil.rmtree('signal')
        os.makedirs('signal')

        if os.path.exists(settings.cluster_path):
            shutil.rmtree(settings.cluster_path)

    def test_save_and_load_simulation(self):
        directory = cluster_manager.run_directory(self.test_index)
        cluster_manager.save_simulation({
            'name': 'test',
            'index': '0'
        })

        assert os.path.exists(self.test_directory+'/name.npy')
        assert os.path.exists(self.test_directory+'/simulation.npy')

        loaded_simulation = cluster_manager.load_simulation(self.test_index)

        assert loaded_simulation['name'] == 'test'
        assert loaded_simulation['index'] == '0'

        loaded_name = cluster_manager.load_simulation_name(self.test_index)

        assert loaded_name == 'test'

        
    def test_all_available_indices_and_names(self):
        directory = cluster_manager.run_directory(self.test_index)
        cluster_manager.save_simulation({
            'name': 'test',
            'index': '0'
        })
        sims = cluster_manager.all_available_indices_and_names()

        assert len(sims) > 0
        assert len(sims[0]) == 2

    def test_run_directory(self):
        ''' Gets or Creates a run directory '''
        if os.path.exists(self.test_directory):
            shutil.rmtree(self.test_directory)

        directory = cluster_manager.run_directory(self.test_index)

        assert directory == self.test_directory
        assert os.path.exists(directory)

        directory = cluster_manager.run_directory(self.test_index)

        assert directory == self.test_directory
        assert os.path.exists(directory)

        shutil.rmtree(self.test_directory)

    def test_get_run_completion_percentage(self):
        ''' Checks the output file for completion percentage '''
                
        percentage = cluster_manager.get_run_completion_percentage(self.test_index)

        assert percentage == 0

        with open(self.remote_directory+"/output","w+") as f:
            f.write("MAIN:  Time: 10/100\n")
        percentage = cluster_manager.get_run_completion_percentage(self.test_index)

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

        cluster_manager.queue_run(outline, self.test_index)

        percentage = cluster_manager.get_run_completion_percentage(self.test_index)

        assert percentage == 0
        assert os.path.exists(settings.cluster_path+'inbox/run0')
        assert os.path.exists(settings.cluster_path+'signal/run0')
        
    def test_write_outline(self):
        cluster_manager.write_outline(
            'contour.dat',
            np.array([[[1,0],[1,1],[0,1],[0,0]]])
        )
        assert os.path.exists('contour.dat')

    def test_fetch_activity(self):
        remote_name = settings.cluster_path+'/cpuloadinfo.sh'
        cluster_manager.cluster.put('test/mock_cpuloadinfo.sh', remote=remote_name)
        cluster_manager.fetch_activity()

    def test_signals(self):
        new_signals = cluster_manager.get_new_signals()

        assert len(new_signals) == 0

        cluster_manager.create_incoming_signal( 0, 'start', 3)
        new_signals = cluster_manager.get_new_signals()

        assert len(new_signals) == 1

        signal = next(iter(new_signals))
        index, signal_type, slot = cluster_manager.get_signal_info( next(iter(new_signals)) )

        cluster_manager.remove_incoming_signal(signal)

        assert index == 0
        assert signal_type == 'start'
        assert slot == 3

        








def get_test_simulations():
    print('loading simulations...')
    data = np.load('sim.npy')
    depths = np.load('sim.npy')
    depthimages = [depth_to_depthimage(depth) for depth in depths]

    simulations = {
        '23454325': {
            'name': 'Bob Jones',
            'score': 10.5,
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '3445345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        },
        '234523452': {
            'name': 'Bob Jones',
            'score': 10.5,
            'rgb_frame': data[0],
            'depth_frame': depthimages[0]
        },
        '23452345': {
            'name': 'Terry Berry',
            'score': 9.5,
            'rgb_frame': data[1],
            'depth_frame': depthimages[1]
        }
    }

    print('simulations loaded')
    return simulations

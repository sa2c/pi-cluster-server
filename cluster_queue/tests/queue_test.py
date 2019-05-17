import pytest
import os, sys, shutil

import settings

settings.nnodes = 4
settings.nslots = 4
settings.IPs = [ "127.0.0.1" for i in range(settings.nnodes) ]
settings.cfdcommand = "ls" #Instead of actually running cfd


import cluster_queue


class TestQueue(object):

    def setup(self):
        cluster_queue.free_nodes = set(range(len(settings.IPs)))

    def test_nodes_available(self):
        assert cluster_queue.nodes_available() == 4
        cluster_queue.free_nodes.pop()
        assert cluster_queue.nodes_available() == 3

    def test_reserve_nodes(self):
        my_nodes = cluster_queue.reserve_nodes(2)
        assert len(my_nodes) == 2
        assert cluster_queue.nodes_available() == 2
        assert my_nodes & cluster_queue.free_nodes == set([])
    
    def test_write_hostfile(self):
        name = "runtest54321"
        filename = "hostfile_"+name
        if os.path.exists(filename):
            os.remove(filename)
        
        cluster_queue.write_hostfile([0,1,2,3], name)

        assert os.path.exists(filename)
        with open(filename) as f:
            content = f.read()
            for i, line in enumerate(content.split('\n')):
                if i<4:
                    assert line == "127.0.0.1 slots=4"

    def test_runcfd(self):
        process = cluster_queue.run_cfd("identifier")
        assert process.wait() == 0

    def test_check_signals(self):
        if os.path.exists('signal_in'):
            shutil.rmtree('signal_in')
        os.makedirs('signal_in')
        os.makedirs('inbox', exist_ok=True)

        assert cluster_queue.check_signals() == []

        cluster_queue.create_file("inbox/testsignal")
        cluster_queue.create_file("signal_in/testsignal")

        run, = cluster_queue.check_signals()
        process, signal, slot = run

        assert signal == 'testsignal'
        assert slot > 0
        assert process.wait() == 0


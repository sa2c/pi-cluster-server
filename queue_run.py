from fabric import Connection
import numpy as np
import os


cluster_address = "pi@10.0.0.253"
cluster_path = "Documents/picluster"
local_path = os.environ['PWD']
nmeasurements = 20

cluster = Connection(cluster_address)


def get_cfd_output(index):
    ''' Get the current stdout of the ongoing run
        or the previous run.
    '''
    directory = '{}/outbox/run{}'.format(cluster_path, index)
    with cluster.cd(directory):
        return cluster.run('cat output', hide=True).stdout


def write_outline(filename, outline):
    flipped_outline = outline.reshape((-1, 2))
    flipped_outline[:, 1:] = 480 - flipped_outline[:, 1:]
    np.savetxt(filename, flipped_outline, fmt='%i %i')


def queue_run(contour, index):
    # save contour to file and copy to the cluster inbox
    filename = "contour.dat"
    write_outline(filename, contour)

    # copy the contour
    remote_name = '{}/inbox/run{}'.format(cluster_path, index)
    cluster.put(filename, remote=remote_name)

    # copy a signal file accross
    remote_name = '{}/signal/run{}'.format(cluster_path, index)
    cluster.put(filename, remote=remote_name)

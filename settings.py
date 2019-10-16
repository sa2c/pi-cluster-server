import os

def fetch_environ(var, val):
    """
    Test is environment variable flag is set to a specific value.
    Otherwise return False (if not set or set to another value).
    Value should be a string, and case is ignored.
    """
    if var in os.environ and os.environ[var].upper() == val.upper():
        return True
    else:
        return False

######################################################################
# HTTP server settings
######################################################################

port = 3524

devel = fetch_environ('devel', 'True')

if devel:
    print('** WARNING: Running in development mode **')

######################################################################
# Cluster queue settings                                             #
######################################################################

IPs = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
nnodes = len(IPs)

cores_per_node = 4

nodes_per_job = 1

cluster_path = '/home/mark/code/picluster/cluster_queue'

root_dir = os.path.dirname(os.path.abspath(__file__))

cfdcommand = "python " + root_dir + "/cfd/runcfd.py {id} {ncores} {hostfile} 2>{output}.err >> {output}"

######################################################################
# CFD settings                                                       #
######################################################################

base_path = os.path.dirname(os.path.realpath(__file__))

# Output files
poly_fname = "simulation.poly"

# Configuration files
elmer_sif_file = '{root_dir}/cfd/config.sif'.format(root_dir=root_dir)

# Executables
triangle_exe = '{root_dir}/cfd/triangle-lib/triangle'.format(root_dir=root_dir)
elmer_postprocess_serial_exe = '{root_dir}/cfd/elmerpostprocessserial'.format(root_dir=root_dir)
elmer_postprocess_parallel_exe = '{root_dir}/cfd/elmerpostprocessparallel'.format(root_dir=root_dir)

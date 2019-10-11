import os

######################################################################
# Cluster queue settings                                             #
######################################################################

IPs = ["127.0.0.1", "127.0.0.1", "127.0.0.1"]
nnodes = len(IPs)

cores_per_node = 4

nodes_per_job = 1

cluster_path = '/home/mark/code/picluster/cluster_queue'

devel = True

root_dir = os.path.dirname(os.path.abspath(__file__))

cfdcommand = "python " + root_dir + "/cfd/runcfd.py {id} {ncores} {hostfile} 2>{output}.err >> {output}"

######################################################################
# CFD settings                                                       #
######################################################################

base_path = os.path.dirname(os.path.realpath(__file__))

# Output files
poly_fname = "simulation.poly"

# Configuration files
elmer_sif_file = f"{root_dir}/cfd/config.sif"

# Executables
triangle_exe = f"{root_dir}/cfd/triangle-lib/triangle"
elmer_postprocess_serial_exe = f"{root_dir}/cfd/elmerpostprocessserial"
elmer_postprocess_parallel_exe = f"{root_dir}/cfd/elmerpostprocessparallel"

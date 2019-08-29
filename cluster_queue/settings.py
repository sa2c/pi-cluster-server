import os

local_path = os.getcwd()
diskaddress = "127.0.0.1:"+local_path+"/"

IPs = [ "127.0.0.1", "127.0.0.1", "127.0.0.1" ]
nnodes = len(IPs)

cores_per_node = 4

nodes_per_job = 1


cfdcommand = "python runcfd.py {id} {ncores} {hostfile} {diskaddress} >> ../simulations/{id}/output"

cluster_path = '/home/mark/code/picluster/cluster_queue'

devel = True


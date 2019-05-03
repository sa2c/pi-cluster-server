import os, sys
import subprocess

from settings import *

# The set of free nodes
free_nodes = set(range(len(IPs)))


def reserve_nodes( n_nodes ):
    my_nodes = set([])
    for ip in range(n_nodes):
	    node = free_nodes.pop()
	    my_nodes.add(node)
    return my_nodes

def write_hostfile( nodes, id ):
    hostfilename="hostfile_"+id
    with open(hostfilename, "w") as f:
        for node in nodes:
            ip = IPs[node]
            line = "{} slots={}\n".format(ip,nslots)
            f.write(line)
    return hostfilename

def nodes_available():
    return( len(free_nodes) )

def run_cfd( id ):
    my_nodes = reserve_nodes( nodes_per_job )
    os.chdir('cfd')
    hostfilename = write_hostfile( my_nodes, id )
    command = "python runcfd.py {} {} {} >> ../outbox/$id/output".format(
        id,
        nodes_per_job*nslots,
        hostfilename
    )
    subprocess.run(command, shell=True)



print(free_nodes)
my_nodes = reserve_nodes(2)
print(my_nodes)
print(write_hostfile( my_nodes, "id"))
print(free_nodes)
print(run_cfd( "id" ))

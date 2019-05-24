import os

local_path = os.getcwd()
diskaddress = "127.0.0.1:"+local_path+"/"

IPs = [ "127.0.0.1", "127.0.0.1", "127.0.0.1" ]
nnodes = len(IPs)

nslots = 4

nodes_per_job = 1


cfdcommand = "python runcfd.py {id} {ncores} {hostfile} {diskaddress} >> ../simulations/{id}/output"

os.makedirs('signal_out', exist_ok=True)
os.makedirs('signal_in', exist_ok=True)
os.makedirs('inbox', exist_ok=True)
os.makedirs('simulations', exist_ok=True)



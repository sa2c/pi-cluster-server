import os

local_path = os.getcwd()
diskaddress = "127.0.0.1:"+local_path+"/"

nnodes = 4
nslots = 4

nodes_per_job = 1

IPs = [ "127.0.0.1" for i in range(nnodes) ]

cfdcommand = "python runcfd.py {id} {ncores} {hostfile} {diskaddress} >> ../simulations/{id}/output"
#cfdcommand = "sleep 10 >> ../simulations/{id}/output"

os.makedirs('signal_out', exist_ok=True)
os.makedirs('signal_in', exist_ok=True)
os.makedirs('inbox', exist_ok=True)
os.makedirs('simulations', exist_ok=True)



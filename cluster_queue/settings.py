import os

local_path = os.environ['PWD']

nnodes = 4
nslots = 4

nodes_per_job = 1

IPs = [ "127.0.0.1" for i in range(nnodes) ]

cfdcommand = "python runcfd.py {id} {ncores} {hostfile} >> ../outbox/{id}/output"
#cfdcommand = "sleep 10 >> ../outbox/{id}/output"

os.makedirs('signal_out', exist_ok=True)
os.makedirs('signal', exist_ok=True)
os.makedirs('inbox', exist_ok=True)
os.makedirs('outbox', exist_ok=True)



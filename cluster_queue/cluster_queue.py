import os, sys
import subprocess
import time
import shutil
import glob
import model

from settings import *
import utils

# The set of free nodes
nodes = set(range(len(IPs)))
nslots = int(len(nodes) / nodes_per_job)

# Divide nodes to slots
ips_in_slot = []
for slot in range(nslots):
    my_nodes = set([])
    for ip in range(nodes_per_job):
	    node = nodes.pop()
	    my_nodes.add(node)
    ips_in_slot.append(my_nodes)

free_slots = set(range(nslots))

def reserve_nodes():
	return free_slots.pop()

def write_hostfile( nodes, id ):

    hostfilename=f'{model.run_directory(id)}/hostfile'

    with open(hostfilename, "w") as f:
        for node in nodes:
            ip = IPs[node]
            line = "{} slots={}\n".format(ip,cores_per_node)
            f.write(line)
    return hostfilename


def slots_available():
    return( len(free_slots) )

def create_file(filename):
    open(filename, 'a').close()


def check_ping():
    signals = os.listdir('signal_in')
    for signal in signals:
        if signal == "ping":
            create_file("signal_out/pong")
            os.remove("signal/ping")

def run_simulation(sim_id, my_slot=None):
    print("Starting", sim_id)

    if my_slot==None :
        my_slot = reserve_nodes()

    my_nodes = ips_in_slot[my_slot]

    hostfilename = write_hostfile( my_nodes, sim_id )

    process = model.run_simulation(sim_id, hostfilename)

    return [(process, slot)]


def restart_slot(runs, slot):
    print("Restarting slot", slot)

    # Rerun and replace process in runs
    for run in runs:
        process, signal, run_slot = run
        if run_slot == slot:
            runs.remove(run)
            process.kill()
            process, slot = run_cfd( signal, slot )
            runs += [(process, signal, slot)]

    return []


def kill_slot(slot):
    for node in ips_in_slot[slot]:
        command = "ssh {} killall ElmerSolver_mpi".format(IPs[node])
        process = subprocess.run(command, shell=True)


def run_queue():
    while True:
        try:
            print("Open slots:", free_slots)

            os.chdir(local_path)
            check_ping()

            # Run waiting simulations
            next = model.waiting_simulations()

            for simulation in simulations:
                if slots_available():
                    runs += run_simulation(simulation)

            # Remove finished simulations
            for run in runs:
                process, slot = run
                if process.poll() is not None:
                    runs.remove(run)
                    free_slots.add(slot)

            time.sleep(1)

        except KeyboardInterrupt:
            print("Stopping queue")
            print("Killing all simulations")
            for run in runs:
                process, signal, run_slot = run
                print(run_slot)
                process.kill()

            print("Removing start signals")
            signals = os.listdir('signal_out')
            for signal in signals:
                if "start" in signal:
                    os.remove('signal_out/'+signal)

            break





if __name__ == '__main__':
    run_queue()


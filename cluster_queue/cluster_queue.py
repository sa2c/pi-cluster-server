import os, sys
import subprocess
import time
import shutil
import glob

from settings import *

# The set of free nodes
nodes = set(range(len(IPs)))
nslots = int(len(nodes) / nodes_per_job)

# Currently running
runs = []

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
    hostfilename="hostfile_"+id
    with open(hostfilename, "w") as f:
        for node in nodes:
            ip = IPs[node]
            line = "{} slots={}\n".format(ip,cores_per_node)
            f.write(line)
    return hostfilename


def slots_available():
    return( len(free_slots) )


def run_cfd( id, my_slot = None ):
    if my_slot==None :
        my_slot = reserve_nodes()
    my_nodes = ips_in_slot[my_slot]
    try:
        os.makedirs('simulations/'+id)
    except FileExistsError:
        pass
    os.chdir('cfd')
    hostfilename = write_hostfile( my_nodes, id )
    command = cfdcommand.format(
        id=id,
        ncores=nodes_per_job*cores_per_node,
        hostfile=hostfilename,
        diskaddress=diskaddress
    )
    process = subprocess.Popen(command, shell=True)
    os.chdir(local_path)
    return [process, my_slot]


def create_file(filename):
    open(filename, 'a').close()


def check_ping():
    signals = os.listdir('signal_in')
    for signal in signals:
        if signal == "ping":
            create_file("signal_out/pong")
            os.remove("signal/ping")
            

def check_signals():
    signals = os.listdir('signal_in')

    for signal in signals:
        if "restart" in signal:
            slot = signal.replace("restart", '')
            try:
                os.remove('signal_in/'+signal)
            except:
                return []
            restart_slot(int(slot)-1)
            return []

    for signal in signals:
        if "run" in signal:
            return run_signal(signal)

    return []


def run_signal(signal):
    print("Starting", signal)
    try:
        os.remove('signal_in/'+signal)
    except:
        return []
    
    shutil.copyfile(
        'inbox/'+signal,
        'cfd/'+signal+'-outline-coords.dat'
    )
    run, slot = run_cfd(signal)
    create_file("signal_out/{}_start_{}".format(signal,slot+1))
    return [(run, signal, slot)]


def restart_slot(slot):
    global runs
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
    global runs
    while True:
        try:
            print("Open slots:", free_slots)

            os.chdir(local_path)
            check_ping()
            runs += check_signals()
        
            for run in runs:
                process, signal, slot = run
                if process.poll() is not None:
                    print("finished", signal)
                    filelist =  glob.glob('cfd/'+signal+'/mesh/*.vtk')
                    filelist +=  glob.glob('cfd/'+signal+'/*.poly')
                    for f in filelist:
                        shutil.copy(f, 'simulations/'+signal+'/')

                    create_file("signal_out/{}_end_{}".format(signal,slot+1))
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


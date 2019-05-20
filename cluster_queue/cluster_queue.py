import os, sys
import subprocess
import time
import shutil
import glob

from settings import *

# The set of free nodes
free_nodes = set(range(len(IPs)))
nslots = int(len(free_nodes) / nodes_per_job)

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
    try:
        os.makedirs('outbox/'+id)
    except FileExistsError:
        pass
    os.chdir('cfd')
    hostfilename = write_hostfile( my_nodes, id )
    command = cfdcommand.format(
        id=id,
        ncores=nodes_per_job*nslots,
        hostfile=hostfilename,
        diskaddress=diskaddress
    )
    process = subprocess.Popen(command, shell=True)
    os.chdir(local_path)
    return process


def create_file(filename):
    open(filename, 'a').close()


def check_ping():
    signals = os.listdir('signal_in')
    for signal in signals:
        if signal == "ping":
            create_file("signal_out/pong")
            os.remove("signal/ping")
  

def check_signals():
    slot = 1 + nslots - int(nodes_available()/nodes_per_job)
    signals = os.listdir('signal_in')
    if( len(signals) > 0):
        signal = signals[0]
        print("Starting", signal)
        try:
            os.remove('signal_in/'+signal)
        except:
            return []

        create_file("signal_out/{}_start_{}".format(signal,slot))
        shutil.copyfile(
            'inbox/'+signal,
            'cfd/'+signal+'-outline-coords.dat'
        )
        run = run_cfd(signal)
        return [(run,signal,slot)]
    else:
        return []


def run_queue():
    runs = []
    while True:
        os.chdir(local_path)
        check_ping()
        if nodes_available() >= nodes_per_job :
            runs += check_signals()
        time.sleep(1)
        
        for run in runs:
            process, signal, slot = run
            if process.poll() is not None:
                print("finished", signal)
                filelist =  glob.glob('cfd/'+signal+'/mesh/*.vtk')
                filelist +=  glob.glob('cfd/'+signal+'/*.poly')
                for f in filelist:
                    shutil.copy(f, 'outbox/'+signal+'/')

                create_file("signal_out/{}_end_{}".format(signal,slot))
                runs.remove(run)





if __name__ == '__main__':
    run_queue()


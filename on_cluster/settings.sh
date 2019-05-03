
# All IPs of all compute nodes.
NNODES=4        # Nodes on the cluster
NSLOTS=4       # Slots per node
NODES_REMOVE='' # ips to remove (just in case)

NODESPERJOB=1

# ips
for i in `seq $NNODES`
do
   #IPs[$i]=10.0.0.$i
   IPs[$i]=127.0.0.1
done


# settings specific to cpuloadinfo.sh
INTERVAL=0.1 # seconds.tenths
COLUMN=8 # idle cpu percentage column in the output files

# Create a directory for storing results and intermediate files
RESDIR=cpu_load_data_dir

# apply NODES_REMOVE to the list 

for NODE in $NODES_REMOVE
do
    unset IPs[$NODE]
done
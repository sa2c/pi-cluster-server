
# THIS SCRIPT MUST BE RUN ON THE MASTER NODE

# settings

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


INTERVAL=0.1 # seconds.tenths
COLUMN=8 # idle cpu percentage column in the output files

# Create a directory for storing results and intermediate files
RESDIR=cpu_load_data_dir

# apply NODES_REMOVE to the list 

for NODE in $NODES_REMOVE
do
    unset IPs[$NODE]
done

mkdir -p $RESDIR

out_ip_name(){
  echo $RESDIR/out_$1
}

# collecting data
for ip in ${IPs[*]}
do
    ssh $ip "top -n 2 -d $INTERVAL -b | grep '%Cpu'| tail -n 1" > $(out_ip_name $ip) &
done

wait

# computing averages
echo '#ip cpu_usage' 
for ip in ${IPs[*]}
do
	echo $ip $(awk '{a+=100.0-$'$COLUMN'}END{print a/NR}'  $(out_ip_name $ip)) 
done


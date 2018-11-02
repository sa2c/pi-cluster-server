
# THIS SCRIPT MUST BE RUN ON THE MASTER NODE

# settings

# All IPs of all compute nodes.
NNODES=14
NODES_REMOVE='' # ips to remove (just in case)
INTERVAL=0.1 # seconds.tenths
COLUMN=8 # idle cpu percentage column in the output files

RESDIR=cpu_load_data_dir
mkdir -p $RESDIR
out_ip_name(){
  echo $RESDIR/out_$1
}

# ips
for i in `seq $NNODES`
do
   IPs[$i]=10.0.0.$i
done

# you can change the list of ips

for NODE in $NODES_REMOVE
do
    unset IPs[$NODE]
done

# working on active nodes
# measuring
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


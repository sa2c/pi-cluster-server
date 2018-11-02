
# THIS SCRIPT MUST BE RUN ON THE MASTER NODE

# settings

# All IPs of all compute nodes.
NNODES=14
NODES_REMOVE='' # ips to remove (just in case)
NO_OF_MEAS=3
INTERVAL=1.0 # seconds.tenths
COLUMN=2 # userspace cpu load column in the output files

RESDIR=cpu_times
mkdir -p 
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
    ssh $ip "top -n $NO_OF_MEAS -d $INTERVAL -b | grep '%Cpu'" > $(out_ip_name $ip) &
done 

wait

# computing averages
echo '#ip cpu_usage' > cpu_usage
for ip in ${IPs[*]}
do
	echo $ip $(awk '{a+=$'$COLUMN'}END{print a/NR}'  $(out_ip_name $ip)) >> cpu_usage
done

cat cpu_usage


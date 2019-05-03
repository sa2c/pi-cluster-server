
# THIS SCRIPT MUST BE RUN ON THE MASTER NODE

# settings
. settings.sh

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


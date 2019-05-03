#!/bin/bash
# Check of there are input files in the inbox and if so, run 
# the cfd simulation. The output file goes to the outbox and
# the input file gets removed.

. settings.sh

mkdir -p signal_out
mkdir -p signal
mkdir -p inbox
mkdir -p outbox

# Create a lists of free and reserved nodes
for i in `seq $NNODES`
do
   FREE[$i]=$i
done


reserve_nodes(){
	my_nodes=()
	for ip in $(seq $1)
	do
		node=${FREE[0]}
		unset FREE[0]
		my_nodes+=($node)
	done
}

write_hostfile(){
	# Write a hostfile for $1 nodes (with unique identifier $2)
	# Sets hostfilename to the name of the new hostfile
	for ip in $(seq $1)
	do
		node=${FREE[0]}
	  	echo ${IPs[$ip]} slots=$NSLOTS >> hostfile_$2
		unset FREE[$node]
	done
	hostfilename=hostfile_$2
}

nodes_available(){
	# Check if there are $1 nodes available
	nfree=${#FREE[@]}
	if [ $nfree -ge $1 ]; then
		return 0
	else
		return 1
	fi
}

run_cfd(){
	local my_nodes
	id=$i
	reserve_nodes $NODESPERJOB
	cd cfd
	write_hostfile $NODESPERJOB $id
	python runcfd.py $id $NODESPERJOB $hostfilename >> ../outbox/$id/output
	
	sleep 5
	# Move cfd image output to outbox
	cd $WORKDIR
	mv cfd/${file}/mesh/*.png outbox/${file}/
	mv cfd/${file}/mesh/*.vtk outbox/${file}/
}

# The event loop
while false
do
	cd $WORKDIR
	#if nodes_available() $NODESPERJOB
	# Check files in signal
	files=$(ls signal | awk '{print $1;}')
	for file in $files
	do
		echo $file
		# remove the file. If this fails, someone else is probably
		# running this job.
		if rm signal/$file
		then
			# Trigger the start simulation signal
			touch signal_out/${file}_start_$slot

			# Create output directory
			mkdir -p outbox/${file}

			run_cfd $file

			# Copy the input file into cfd and run
			cp inbox/$file cfd/${file}-outline-coords.dat
			
			# Send an empty signal file to the UI machine
			touch send_signal/${file}_end_$slot
			scp send_signal/${file}_end_$slot ${UI_ADDRESS}:${UI_OUTPUTDIR}signal/
		fi
	done
	sleep 1
done


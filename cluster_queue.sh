#!/bin/bash
# Check of there are input files in the inbox and if so, run 
# the cfd simulation. The output file goes to the outbox and
# the input file gets removed.

UI_ADDRESS=kinectwrangler@10.0.0.252
UI_OUTPUTDIR=picluster/
WORKDIR=$(pwd)

mkdir -p send_signal

mkdir -p signal
mkdir -p inbox
mkdir -p outbox

while true
do
	cd $WORKDIR
	# Check for first file in signal
	files=$(ls signal | awk '{print $1;}')
	for file in $files
	do
		echo $file
		# remove the file. If this fails, someone else is probably
		# running this job.
		if rm signal/$file
		then
			# Push the start simulation signal
			touch send_signal/${file}_start
			scp send_signal/${file}_start ${UI_ADDRESS}:${UI_OUTPUTDIR}signal/

			# Create output directory
			mkdir -p outbox/${file}

			# Copy the input file into cfd and run
			cp inbox/$file cfd/${file}-outline-coords.dat
			cd cfd && python runcfd.py $file 4 hostfile1 >> ../outbox/$file/output

			# Move cfd image output to outbox
			cd $WORKDIR
			mv cfd/${file}/mesh/*.png outbox/${file}/
			mv cfd/${file}/mesh/*.vtk outbox/${file}/
			
			# Copy to the UI node
			rsync -r outbox/${file} ${UI_ADDRESS}:${UI_OUTPUTDIR}/outbox/

			# Send an empty signal file to the UI machine
			touch send_signal/${file}_end
			scp send_signal/${file}_end ${UI_ADDRESS}:${UI_OUTPUTDIR}signal/
		fi
	done
done


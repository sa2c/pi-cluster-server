#!/bin/bash
# Check of there are input files in the inbox and if so, run 
# the cfd simulation. The output file goes to the outbox and
# the input file gets removed.

UI_ADDRESS=kinectwrangler@10.0.0.252
UI_OUTPUTDIR=picluster/outbox/
UI_PW=sa2cpi
WORKDIR=$(pwd)

while true
do
	cd $WORKDIR
	files=$(ls inbox)	
	for file in $files
	do
		echo $file
		cp inbox/$file cfd/${file}-outline-coords.dat
		mkdir -p outbox/${file}/
		cd cfd && python runcfd.py $file >> ../outbox/${file}/output
		cd $WORKDIR
		mv cfd/${file}/mesh/*.png outbox/${file}/
		echo $UI_PW > rsync -r outbox/${file} ${UI_ADDRESS}:${UI_OUTPUTDIR}
		rm inbox/$file
	done
done


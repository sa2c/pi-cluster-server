#!/bin/bash
# Check of there are input files in the inbox and if so, run 
# the cfd simulation. The output file goes to the outbox and
# the input file gets removed.

UI_ADDRESS=kinectwrangler@10.0.0.252
UI_OUTPUTDIR=picluster/outbox/
UI_PW=sa2cpi
WORKDIR=$(pwd)

mkdir -p signals
mkdir -p inbox
mkdir -p outbox

while true
do
	cd $WORKDIR
	files=$(ls inbox)
	for file in $files
	do
		echo $file
		mkdir -p outbox/${file} 
		cp contour.dat cfd/${file}-outline-coords.dat
		mkdir -p outbox/
		cd cfd && python runcfd.py $file 4 >> ../outbox/$file/output
		cd $WORKDIR
		mv cfd/${file}/mesh/*.png outbox/${file}/
		echo $file > outbox/${file}/runname
		echo $UI_PW > rsync -r outbox/${file} ${UI_ADDRESS}:${UI_OUTPUTDIR}/current/${file}
		touch signals/${file}
		scp signals/${file} ${UI_ADDRESS}:${UI_OUTPUTDIR}signal/
		rm inbox/$file
	done
done


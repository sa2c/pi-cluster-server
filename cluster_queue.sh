#!/bin/bash
# Check of there are input files in the inbox and if so, run 
# the cfd simulation. The output file goes to the outbox and
# the input file gets removed.

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
		rm inbox/$file
	done
done


#!/bin/bash
# Check of there are input files in the inbox and if so, run 
# the cfd simulation. The output file goes to the outbox and
# the input file gets removed.

while true
do
	files=$(ls inbox)
	for file in $files
	do
		echo $file
		rm inbox/$file
	done
done


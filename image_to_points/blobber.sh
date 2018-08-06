#!/bin/bash

convert $1 $1.bmp
potrace $1.bmp -b svg -o $1.svg -t 10 -a 0
rm $1.bmp
python blobber.py $1.svg -o $1.dat

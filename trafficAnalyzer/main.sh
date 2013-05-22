#!/bin/bash

inputFile=$1
DUT=$2
#rm -rf tmp/* #clean up old mess
#sh dissector.sh $inputFile

FILES=tmp/*
for f in $FILES
do
      echo "Processing $f"
      ./analyzer.py -s -d $DUT -o $inputFile -f $f
      done

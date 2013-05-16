#!/bin/bash

beginblock=0


 tshark -r $1 -T fields -e udp.dstport -e frame.number | \
     while read inputLine; do
    dstport=`echo $inputLine | awk '{print $1}'`
    framenumber=`echo $inputLine | awk '{print $2}'`

    if [ $dstport -eq 1337 ]; then
        if [ $beginblock -eq 0 ]; then
            #beginning of block
            beginblock=$framenumber
        else
            #end of bloc
            
            echo "editcap -r ./$1  tmp/$beginblock-$framenumber.pcap $beginblock-$framenumber"
            editcap -r ./$1  tmp/$beginblock-$framenumber.pcap $beginblock-$framenumber
            beginblock=$framenumber
        fi
        
    fi
    
    done;


#!/bin/bash

beginblock=0
export lastFrameNumber=0
export lastBlockBegin=0

 #tshark -r $1 -T fields -e frame.number -e udp.dstport | \
     while read inputLine; do
    dstport=`echo $inputLine | awk '{print $2}'`

    if [ !  -z $dstport ]; then
        if [ $dstport -eq 1337 ]; then
            
            framenumber=`echo $inputLine | awk '{print $1}'`
            lastFrameNumber=$framenumber #Duuuh, ugly
            if [ $beginblock -eq 0 ]; then
                #beginning of block
                beginblock=$framenumber
            else
                #end of bloc
            
                packetDistance=$[framenumber - beginblock]
                if [ $packetDistance > 1 ]; then #check for duplicate udp packets
                :
                   # echo  "editcap -r ./$1  tmp/$beginblock-$[ framenumber - 1 ].pcap $beginblock-$[ framenumber - 1 ] "
                   editcap -F libpcap -r ./$1  tmp/$beginblock-$[ framenumber - 1 ].pcap $beginblock-$[ framenumber - 1 ]
                fi
                beginblock=$framenumber
                lastBlockBegin=$framenumber
            fi
        
        fi
    fi
done< <(tshark -r $1 -T fields -e frame.number -e udp.dstport)
#get the last bit:

lastFrameNumber=`capinfos -c $1 | awk END'{print $4}'`
echo $lastframeNumber
#echo "editcap -F libpcap -r ./$1  tmp/$lastBlockBegin-$[ lastFrameNumber - 1 ].pcap $lastBlockBegin-$[ lastFrameNumber - 1 ]"
editcap -F libpcap -r ./$1  tmp/$lastBlockBegin-$lastFrameNumber.pcap $lastBlockBegin-$lastFrameNumber

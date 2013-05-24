#!/bin/bash


interceptionHostIp=10.23.23.160
interceptionHostRoot="~/mobileTraffic/interception/"
dutIP=10.0.0.42
filename=`date +"%y-%m-%d--%H"`"_"$1
counter=0

function run_test {

    cat top500.txt | \
    while read URL; do
        counter=$[counter + 1]

        echo "requesting $URL, request ID $counter"
        echo -n "$URL | request_ID: $counter" | nc -4u  -w1 10.0.0.23 1337
        ssh -i ~/.ssh/id_rsa_experiment $dutIP firefox-bin $URL & 
        sleep 60s
        ssh -i ~/.ssh/id_rsa_experiment $dutIP wmctrl -c firefox  & #kills the process of the currently active tab
        sleep 4s
  done;
    echo "method terminated normally"
}

function notify_client {
  filename=$1
  filesize=$(getRemoteFileSize $filename)
  sh nma.sh MobileTraffic "The experiment $1 is ready. Size: $filesize" 2

}



function start_capture {
filename=$1
ssh -i ~/.ssh/id_rsa_experiment $interceptionHostIp sudo nohup sh $interceptionHostRoot/startup.sh $filename &

}

function stop_capture {

ssh -i ~/.ssh/id_rsa_experiment $interceptionHostIp sudo killall tcpdump

}


function getRemoteFileSize {

filename=$1
FILESIZE=$(ssh -i ~/.ssh/id_rsa_experiment $interceptionHostIp stat -c%s "~/captures/$1.pcap")
echo $FILESIZE
}

function copyResult {

filename=$1
scp -i ~/.ssh/id_rsa_experiment $interceptionHostIp:~/captures/$filename.pcap captures/$filename.pcap

}

function basic_measurement_cycle {
sudo  route -n add 10.0.0.0/8 10.23.23.160 ## required for udp
filename=`date +"%y-%m-%d--%H"`"_desktop_measurement"
start_capture $filename
sleep 10s
run_test
stop_capture
notify_client $filename
copyResult $filename
}


 if [ $1 == "--selftest" ]; then
 filename=13-04-03--05_basic_measurement

getRemoteFileSize "$filename"
 echo $filesize
 fi
if [ $1 == "--basicTest" ]; then
for i in {1..1}
do
   basic_measurement_cycle
done
else
echo "Usage: --basicTest for basic test"
echo "--selfTest for selftest"
fi



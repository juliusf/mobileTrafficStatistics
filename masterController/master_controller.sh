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

        echo "requesting $URL on desktop, request ID $counter"
        echo -n "ID: $counter | DESKTOP | $URL" | nc -4u  -w1 10.0.0.23 1337
        ssh -i ~/.ssh/id_rsa_experiment $dutIP firefox-bin $URL & 
        sleep 60s
        ssh -i ~/.ssh/id_rsa_experiment $dutIP wmctrl -c firefox  & #kills the process of the currently active tab
        sleep 10s      
        
        #mobile part begins here
        
        echo "requesting $URL on mobile, request ID $counter"
        echo -n "ID: $counter | MOBILE | $URL" | nc -4u  -w1 10.0.0.23 1337
        timelimit -T 60 -t 55 adb shell am start -a android.intent.action.VIEW -d $URL 
        sleep 60s
        #adb shell killall org.mozilla.firefox  #kills the process of the currently active tab
        adb shell am force-stop org.mozilla.firefox
        sleep 10s

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



for i in {1..1}
do
   basic_measurement_cycle
done
#!/bin/bash


interceptionHostIp=10.23.23.160
interceptionHostRoot="~/mobileTraffic/interception/"
filename=`date +"%y-%m-%d--%H"`"_"$1
counter=0

function run_test {

    cat top500.txt | \
    while read URL; do
        counter=$[counter + 1]
        echo "`date`: ending udp identifier"
        ret=1
        while [ $ret != 0 ]; do
            timelimit -T 45 -t 30 echo -n "$URL | id= $counter" | nc -4u  -w1 10.0.0.23 1337
            ret=$?
            echo $ret
        done;
        echo "`date`: requesting $URL, request ID $counter"
        timelimit -T 60 -t 55 adb shell am start -a android.intent.action.VIEW -d $URL 
        sleep 60s
        #adb shell killall org.mozilla.firefox  #kills the process of the currently active tab
        adb shell am force-stop org.mozilla.firefox
        sleep 5s
        #clear_firefox_data || errorHandler
  done;

}

function notify_client {
  filename=$1
  filesize=$(getRemoteFileSize $filename)
  sh nma.sh MobileTraffic "The experiment $1 is ready. Size: $filesize" 2

}


function clear_chrome_data {

adb shell killall com.android.chrome
adb shell rm -rf /data/data/com.android.chrome/cache
adb push com.android.chrome/cache/ /data/data/com.android.chrome/cache

}

function clear_firefox_data {

adb shell killall org.mozilla.firefox
adb shell rm -rf /data/data/org.mozilla.firefox/cache
#adb push com.android.chrome/cache/ /data/data/com.android.chrome/cache

}

function start_capture {
filename=$1
ssh -i ~/.ssh/id_rsa_experiment $interceptionHostIp sudo nohup sh $interceptionHostRoot/startup.sh $filename &

}

function stop_capture {

ssh -i ~/.ssh/id_rsa_experiment $interceptionHostIp sudo killall tcpdump

}

function errorHandler {

  sh nma.sh MobileTraffic "The experiment $1 FAILED! Dumping syslog..." 2
  adb pull /devlog/system_log
  exit -1
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
filename=`date +"%y-%m-%d--%H"`"_basic_measurement"
clear_chrome_data
start_capture  $filename
sleep 10s
run_test
stop_capture
notify_client $filename
copyResult $filename
}

function firefox_measurement_cycle {
sudo  route -n add 10.0.0.0/8 10.23.23.160 ## required for udp
filename=`date +"%y-%m-%d--%H"`"_firefox_measurement"
#clear_chrome_data
start_capture  $filename
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
    firefox_measurement_cycle
done
else
echo "Usage: --basicTest for basic test"
echo "--selfTest for selftest"
fi



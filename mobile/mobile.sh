#!/bin/bash


interceptionHostIp=10.23.23.160
interceptionHostRoot="~/mobileTraffic/interception/"
filename=`date +"%y-%m-%d--%H"`"_"$1

function run_test {

    cat top500.txt | \
    while read URL; do
        
        echo -n "$URL" | nc -4u -w1 $interceptionHostIp 1337
        adb shell am start -a android.intent.action.VIEW -d $URL || errorHandler
        sleep 60s
        adb shell killall com.android.chrome:sandboxed_process0 || errorHandler #kills the process of the currently active tab
        clear_chrome_data || errorHandler
  done;

}

function notify_client {
  
  sh nma.sh MobileTraffic "The experiment $1 is ready" 0

}


function clear_chrome_data {

adb shell killall com.android.chrome
adb shell rm -rf /data/data/com.android.chrome/cache
adb push com.android.chrome /data/data/com.android.chrome/cache

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
return $FILESIZE
}

function basic_measurement_cycle {

filename=`date +"%y-%m-%d--%H"`"_basic_measurement"
clear_chrome_data
start_capture  $filename
run_test
stop_capture
notify_client $filename

}


 if [$1 == "--selftest" ]; then
 filesize=getRemoteFileSize 13-04-03--05_basic_measurement
 echo filesize
 fi
if [ $1 == "--basicTest" ]; then
for i in {1..3}
do
   basic_measurement_cycle
done
else
echo "Usage: --basicTest for basic test"
echo "--selfTest for selftest"
fi



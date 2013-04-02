#!/bin/bash


interceptionHostIp=10.23.23.160
interceptionHostRoot="~/mobileTraffic/interception/"
filename=`date +"%y-%m-%d--%H"`"_"$1

function run_test {

    cat top500.txt | \
    while read URL; do
        sleep 5s
        echo -n "$URL" | nc -4u -w1 $interceptionHostIp 1337
        adb shell am start -a android.intent.action.VIEW -d $URL
        sleep 60s
        adb shell killall com.android.chrome:sandboxed_process0 #kills the process of the currently active tab
  done;

}

function notify_client {
  
  sh nma.sh MobileTraffic "The experiment is ready" "1"

}


function clear_chrome_data {

adb shell killall com.android.chrome
adb shell rm -rf /data/data/com.android.chrome
adb push com.android.chrome /data/data/com.android.chrome

} 

function start_capture {

ssh -i ~/.ssh/id_rsa_experiment 10.23.23.160 sudo nohup sh $interceptionHostRoot/startup.sh $filename &

}
##running the functions
  start_capture
 echo foobar
  #reinstall_chrome
  #clear_chrome_data
  #run_test
  #notify_client
  #reinstall_chrome

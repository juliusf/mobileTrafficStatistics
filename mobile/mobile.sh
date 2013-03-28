#!/bin/bash

function run_test {

    cat top500.txt | \
    while read URL; do
        sleep 5s
        adb shell am start -a android.intent.action.VIEW -d $URL
        sleep 60s
        adb shell killall com.android.chrome:sandboxed_process0
  done;
}

function notify_client {
  
  sh MobileTraffic "The experiment is ready" "1"
}

function reinstall_chrome {

  adb uninstall com.android.chrome
  adb install com.android.chrome-1.apk
}

function clear_chrome_data {
adb shell killall com.android.chrome
adb shell rm -rf /data/data/com.android.chrome
adb push com.android.chrome /data/data/com.android.chrome


} 
##running the functions
  #reinstall_chrome
  clear_chrome_data
  run_test
  #notify_client
  #reinstall_chrome

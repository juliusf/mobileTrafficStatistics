#!/bin/bash
./multi_analyzer.py -f gold/13-06-07--17_desktop_measurement.pcap
./multi_analyzer.py -f gold/13-06-12--10_desktop_measurement_good_one.pcap
./multi_analyzer.py -f gold/13-06-15--23_desktop_measurement.pcap

./sqlAnalyzer.py -d -f gold/13-06-07--17_desktop_measurement.pcap.sqlite
./sqlAnalyzer.py -d -f gold/13-06-12--10_desktop_measurement_good_one.pcap.sqlite
./sqlAnalyzer.py -d -f gold/13-06-15--23_desktop_measurement.pcap.sqlite

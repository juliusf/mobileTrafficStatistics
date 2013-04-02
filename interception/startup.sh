#!/bin/bash

savePath="captures/"$1".pcap"
sudo echo 1 > /proc/sys/net/ipv4/ip_forward 1
sudo ifconfig eth1 10.0.0.254 netmask 255.255.255.0
sudo iptables -A FORWARD -i eth1 -j ACCEPT
sudo iptables -A FORWARD -o eth1 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo tcpdump -i eth1 '(proto TCP and port 80 or 8080 or 443) or (proto UDP and port 53 or 1337)' -w $savePath 


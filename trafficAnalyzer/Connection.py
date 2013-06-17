#!/usr/bin/python2.7
from scapy.packet import *

class Connection(object):
    def __init__(self):
        self._dst_IP = ""
        self._curr_dst_IP = ""
        self._curr_src_IP = ""
        self._curr_dst_port = 0
        self._curr_src_port = 0
        self._current_volume = 0
        self._current_packet_number = 0
        self._DNS = ""
        self._rDNS = ""
        self._parentBatchID = 0
        self._is_CDN_connection = False
        

    def get_volume(self):
        return self._current_volume

    def increase_volume(self, volume):
        self._current_volume += volume

    def set_volume(self, volume):
        self._current_volume = volume

    def set_dst_ip(self, ip):
        self._dst_IP = ip

    def get_dst_ip(self):
        return self._dst_IP

    def set_dst_ip(self, ip):
        self._dst_IP = ip

    def get_dns(self):
        return self._DNS
        
    def __str__(self):
        return "current_dst_IP: " + self._curr_dst_IP + " current_src_IP: " + self._curr_dst_IP + "current_dst_port: " + str(self._curr_dst_port) + "current_sport:" + str(self._curr_dst_port) 

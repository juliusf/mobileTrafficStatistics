#!/bin/python2.7    

from scapy.all import *

def updateRequestDomain():
    #Update Database here
    print  'updateRequest'

pkts = utils.rdpcap("13-04-11--18_basic_measurement.pcap")

requestDomain = ""


def extractHttp():

    

for pkt in pkts:
    #packet data extraction
    ipdata = pkt[IP]
    src =  pkt.getlayer(IP).src
    dst = pkt.getlayer(IP).dst
    dport = 0
    sport = 0
    l4 = ""
    if pkt.haslayer(UDP):
        l4 = "UDP"

    if pkt.haslayer(TCP):
        l4 = "TCP"

    if l4 == "UDP":
       dport = pkt.getlayer(UDP).dport
       sport = pkt.getlayer(UDP).sport

    if l4 == "TCP":
        dport = pkt.getlayer(TCP).dport
        sport = pkt.getlayer(TCP).sport

    #check for new url request block:

    if l4 == "UDP" and dport == 1337:
        updateRequestDomain()
        requestURL =  pkt.getlayer(UDP).payload
    else:
        if pkt.haslayer(Raw):
            print pkt.getlayer(Raw)


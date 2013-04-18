#!/bin/python2.7    

from scapy.all import *
from scapyhttp.HTTP import HTTP
from RequestBatch import RequestBatch
import optparse


current_packet = None
request_batch = RequestBatch()

def main():
    #global vars
    global current_packet
    global request_batch

    #commandline option parser
    parser = optparse.OptionParser()
    parser.add_option('-p', '--plot', help='creates gnuplot DAT file')
    (opts, args) = parser.parse_args()
    
    packets = utils.rdpcap("13-04-11--18_basic_measurement.pcap")
    request_batch = RequestBatch()

    for pkt in packets:
        #packet data extraction
        current_packet = pkt
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
            update_requestdomain(pkt.getlayer(Raw))
            
        else:
            #HTTP GET extraction
            if pkt.haslayer(HTTP):
               extract_http()
            #DNS Query Count
            if l4 == "UDP" and dport == 53:
                request_batch.increment_dnsrequests()

            #DownstreamVolume

            if dst == "10.0.0.23" :
                request_batch.increase_downstreamvolume(len(pkt.getlayer(IP))) #TODO: w/ or /w ethernet?


def update_requestdomain(domain):
    #Update Database here
    global request_batch
    print '-'*23
    print "Statistics for: %s" % (request_batch.get_requesturl())
    print "HTTP GET Requests: %s" % (request_batch.get_getrequests())
    print "DNS Requests: %s" % (request_batch.get_dnsrequests())
    print "Downstream Volume: %s" % (request_batch.get_downstreamvolume())
    request_batch = RequestBatch()
    request_batch.set_requesturl(domain)

def extract_http():
    global current_packet
    global request_batch
    httpData = current_packet.getlayer(HTTP).payload.fields

    if 'Method' in httpData:
        request_batch.increment_getrequests()


if __name__=="__main__":
   main()
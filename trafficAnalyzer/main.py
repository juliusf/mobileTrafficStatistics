#!/usr/bin/python2.7    

from scapy.all import *
from scapyhttp.HTTP import HTTP
from RequestBatch import RequestBatch
import optparse
import matplotlib.pyplot as plt
import numpy as np
#constants
DUT_IP = "10.0.0.23"
#global vars
current_packet = None
request_batch = RequestBatch()
processed_batches = []
options = None
dns_blacklist = []

def main():
    global dns_blacklist

    #parse and populate the blacklist
    #blacklist_file = open('blacklist.txt')
    parser = optparse.OptionParser()
    #commandline options 
    parser.add_option('-f', '--file', help='the pcap file to be parsed')
    parser.add_option("-p", "--preview",
                  action="store_true", dest="preview", default=False,
                  help="Generate a preview plot of the processed")
    parser.add_option('-g', '--gnuplot', help='creates a gnuplot DAT file')

    (opts, args) = parser.parse_args()

    if opts.file is None:
        print "You haven't specified any pcap file.\n"
        parser.print_help()
        exit(-1)


    #parse the actual file   
    parse_pcap(opts.file)

    #create preview
    if opts.preview:
        plot_preview()

def parse_pcap(filename):
    #global vars
    global current_packet
    global request_batch
    
    packets = utils.rdpcap(filename)
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
            if src == DUT_IP and pkt.haslayer(HTTP):
               extract_http()
            #DNS Query Count
            if src == DUT_IP and l4 == "UDP" and dport == 53:
                request_batch.increment_dnsrequests()

            #DownstreamVolume

            if dst == DUT_IP :
                request_batch.increase_downstreamvolume(len(pkt.getlayer(IP))) 


def update_requestdomain(domain):
    #Update Database here
    global request_batch
    global processed_batches

    if request_batch._requestURL != "": # check wheter the requestbatch has been touched before
        processed_batches.append(request_batch)
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

def plot_preview():
    global processed_batches
    
    http_gets = []
    dns_reqs = []
    downstream_vols = []
    xaxis = []

    for batch in processed_batches:
        http_gets.append(batch.get_getrequests())
        dns_reqs.append(batch.get_dnsrequests())
        downstream_vols.append(batch.get_downstreamvolume())
        xaxis.append(len(http_gets))

    plt.figure(1)
    plt.subplot(311)
    plt.plot(xaxis, http_gets, 'ro')
    plt.axhline(y=np.mean(http_gets))
    plt.ylabel('Nr. of HTTP GET requests')
    plt.xlabel('Batch Nr.')

    plt.subplot(312)
    plt.plot(xaxis, dns_reqs, 'ro')
    plt.axhline(y=np.mean(dns_reqs))
    plt.ylabel('Nr. of DNS requests')
    plt.xlabel('Batch Nr.')
    
    plt.subplot(313)
    plt.plot(xaxis, downstream_vols, 'ro')
    plt.axhline(y=np.mean(downstream_vols))
    plt.ylabel('Downstream volume in Bytes')
    plt.xlabel('Batch Nr.')
    
    plt.show()

if __name__=="__main__":
   main()
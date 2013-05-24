#!/usr/bin/python2.7

from scapy.all import *
from scapyhttp.HTTP import HTTP
from RequestBatch import RequestBatch
from os import listdir
from os.path import isfile, join
from subprocess import call
import os
import optparse
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import Pmf
import sqlite3


#constants
DUT_IP = "10.0.0.23"
dut_type = None
lcurrent_packet = None
request_batch = RequestBatch()
processed_batches = []
options = None
dns_blacklist = []
ip_blacklist = []
filename = None
original_filename = None

def main():
    global dns_blacklist
    global ip_blacklist
    global DUT_IP
    global dut_type
    global filename
    global original_filename

    #parse and populate the blacklist
    print "generating blacklists..."
    f = open('dnsBlacklist.txt')
    dns_blacklist = f.readlines()
    f.close()
    f = open('ipBlacklist.txt')
    ip_blacklist = f.readlines()
    f.close()
    
    parser = optparse.OptionParser()
    #commandline options
    parser.add_option('-f', '--filename', help="specifies the filename")
    (opts, args) = parser.parse_args()
    
    #commandline options

    if opts.filename is None:
        print "you havent specified the original filename"
        parser.print_help()
        exit(-1)
    original_filename = opts.filename
    


    if  'firefox' in original_filename:
        DUT_IP = "10.0.0.23"
        dut_type = 'mobile'

    if  'desktop' in original_filename:
        DUT_IP = "10.0.0.42"
        dut_type = 'desktop'

    print "slicing pcap..."
    call(["editcap", "-F", "libpcap", "-c","50000", original_filename, "tmp/out.pcap"])
    parse_all_files()

def parse_all_files():
    global request_batch
    global processed_batches
    global filename
    request_batch = RequestBatch()
    all_files = [ f for f in listdir('tmp/') if isfile(join('tmp/',f)) ]
    all_files = sorted(all_files)
    #print all_files
    for file in all_files:
        filename = file
        parse_pcap(file)
        os.remove('tmp/' + file)


    if request_batch._requestURL != "": # check wheter the requestbatch has been touched before
        processed_batches.append(request_batch)
        add_to_database()

def parse_pcap(filename):
    #global vars
    global current_packet
    global request_batch
    print "reading pcap..."
    packets = utils.rdpcap('tmp/'+filename)
    print "parsing pcap..."
    for pkt in packets:
        #packet data extraction
        current_packet = pkt

        if not pkt.haslayer(IP):
            print "IP LAYER ERROR!"
            continue

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

            if dst == DUT_IP  and not ip_blacklisted(src):
                if not (( "173.194.69." in src or  "173.194.70." in src) and sport == 443):  #filters out the google subnets for SSL
                    request_batch.increase_downstreamvolume(len(pkt.getlayer(IP))) #without ethernet layer!

    #add the last batch
    


def update_requestdomain(domain):
    #Update Database here
    global request_batch
    global processed_batches


    if str(domain) == str(request_batch.get_requesturl()):
        print "UDP packet doubling detected!: %s" % (domain)
        return
    print "currently processing: %s" % (domain)
    if request_batch._requestURL != "": # check wheter the requestbatch has been touched before
        processed_batches.append(request_batch)
     # print '-'*23
      # print "Statistics for: %s" % (request_batch.get_requesturl())
       #print "HTTP GET Requests: %s" % (request_batch.get_getrequests())
      # print "DNS Requests: %s" % (request_batch.get_dnsrequests())
      # print "Downstream Volume: %s" % (request_batch.get_downstreamvolume())
    request_batch = RequestBatch()
    request_batch.set_requesturl(str(domain))

def extract_http():
    global current_packet
    global request_batch
    httpData = current_packet.getlayer(HTTP).payload.fields

    if 'Method' in httpData:
        request_batch.increment_getrequests()


def ip_blacklisted(ip):
    if ip in ip_blacklist:
        return True
    else:
       return False

def dns_blacklisted(domain_name):
    if domain_name in dns_blacklist:
        return True
    else:
        return False

def add_to_database():
    global processed_batches
    global dut_type
    global filename
    global original_filename
    sqlconn = sqlite3.connect('measurements.sqlite')
    c = sqlconn.cursor()
    data = []
    if dut_type == 'mobile':
        for batch in processed_batches:
            data.append( (original_filename, batch.get_requesturl(), batch.get_getrequests(), batch.get_dnsrequests(),  batch.get_downstreamvolume(), 0 ) )
        c.executemany('insert into mobileMeasurement values (?,?,?,?,?,?)', data)

    if dut_type == 'desktop':
        for batch in processed_batches:
            data.append( (original_filename, batch.get_requesturl(), batch.get_getrequests(), batch.get_dnsrequests(),  batch.get_downstreamvolume(), 0 ) )
       # print data
        c.executemany('insert into desktopMeasurement values (?,?,?,?,?,?)', data)

    sqlconn.commit()

if __name__=="__main__":
   main()

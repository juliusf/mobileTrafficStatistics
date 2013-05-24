#!/usr/bin/python2.7

from scapy.all import *
from scapyhttp.HTTP import HTTP
from RequestBatch import RequestBatch
from os import listdir
from os.path import isfile, join
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
    parse_all_files()
    parser = optparse.OptionParser()
    #commandline options
    parser.add_option('-f', '--file', help='the pcap file to be parsed')
    parser.add_option("-p", "--preview",
                  action="store_true", dest="preview", default=False,
                  help="Generate a preview plot of the processed")
    parser.add_option("-s", "--storeData",
                  action="store_true", dest="storedata", default=False,
                  help="stores the data in the database")
    parser.add_option('-g', '--gnuplot', help='creates a gnuplot DAT file')
    parser.add_option('-d', '--dut', help='specifies the data source. either "desktop" or "mobile"')
    parser.add_option('-o', '--originalFilename', help="specifies the original filename used for database storage")
    (opts, args) = parser.parse_args()

    if opts.file is None:
        print "You haven't specified any pcap file.\n"
        parser.print_help()
        exit(-1)
    filename = opts.file

    if opts.originalFilename is None:
        print "you havent specified the original filename"
        parser.print_help()
        exit(-1)
    original_filename = opts.originalFilename
    if opts.dut is None:
        print "You haven't specified a device type. Either use 'mobile' or 'desktop'"
        parser.print_help()
        exit(-1)

    if (opts.dut == 'mobile'):
        DUT_IP = "10.0.0.23"
        dut_type = 'mobile'

    if (opts.dut == 'desktop'):
        DUT_IP = "10.0.0.42"
        dut_type = 'desktop'

    #parse the actual file
    parse_pcap(opts.file)

    #create preview
    print "creating preview..."
    if opts.preview:
        plot_preview()

    if opts.storedata:
        add_to_database()

def parse_all_files():
    onlyfiles = [ f for f in listdir('tmp/') if isfile(join('tmp/',f)) ]
    print onlyfiles

def parse_pcap(filename):
    #global vars
    global current_packet
    global request_batch
    print "reading pcap..."
    packets = utils.rdpcap(filename)
    request_batch = RequestBatch()
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
    if request_batch._requestURL != "": # check wheter the requestbatch has been touched before
        processed_batches.append(request_batch)


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
            data.append( ((filename + " | "+ original_filename), batch.get_requesturl(), batch.get_getrequests(), batch.get_dnsrequests(),  batch.get_downstreamvolume(), 0 ) )
        c.executemany('insert into mobileMeasurement values (?,?,?,?,?,?)', data)

    if dut_type == 'desktop':
        for batch in processed_batches:
            data.append( ( (filename + " | "+ original_filename), batch.get_requesturl(), batch.get_getrequests(), batch.get_dnsrequests(),  batch.get_downstreamvolume(), 0 ) )
       # print data
        c.executemany('insert into desktopMeasurement values (?,?,?,?,?,?)', data)

    sqlconn.commit()

if __name__=="__main__":
   main()

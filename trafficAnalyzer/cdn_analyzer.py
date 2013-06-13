#!/usr/bin/python2.7

from scapy.all import *
from os import listdir
from os.path import isfile, join

def main():
    parser = optparse.OptionParser()
    #commandline options
    parser.add_option('-f', '--filename', help="specifies the filename")
    (opts, args) = parser.parse_args()

    if opts.filename is None:
        print "you haven't specified the original filename"
        parser.print_help()
        exit(-1)
    opts.filename


def update_requestdomain(domain):
    #Update Database here
    global request_batch
    global processed_batches
    global DUT_IP
    global contacted_hosts

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
    contacted_hosts = []

    if '| MOBILE |' in str(domain):
        DUT_IP = "10.0.0.23"

    if '| DESKTOP |' in str(domain):
        DUT_IP = "10.0.0.42"

if __name__=="__main__":
   main()
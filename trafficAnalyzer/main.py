#!/usr/bin/python2.7

from scapy.all import *
from scapyhttp.HTTP import HTTP
from RequestBatch import RequestBatch
import optparse
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import Pmf

#constants
DUT_IP = "10.0.0.23"
lcurrent_packet = None
request_batch = RequestBatch()
processed_batches = []
options = None
dns_blacklist = []
ip_blacklist = []


def main():
    global dns_blacklist
    global ip_blacklist
    global DUT_IP

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
    parser.add_option('-f', '--file', help='the pcap file to be parsed')
    parser.add_option("-p", "--preview",
                  action="store_true", dest="preview", default=False,
                  help="Generate a preview plot of the processed")
    parser.add_option('-g', '--gnuplot', help='creates a gnuplot DAT file')
    parser.add_option('-d', '--dut', help='specifies the data source. either "desktop" or "mobile"')

    (opts, args) = parser.parse_args()

    if opts.file is None:
        print "You haven't specified any pcap file.\n"
        parser.print_help()
        exit(-1)

    if opts.dut is None:
        print "You haven't specified a devce type. Either use 'mobile' or 'desktop'"
        parser.print_help()
        exit(-1)

    if (opts.dut == 'mobile'):
        DUT_IP = "10.0.0.23"

    if (opts.dut == 'desktop'):
        DUT_IP = "10.0.0.42"

    #parse the actual file
    parse_pcap(opts.file)

    #create preview
    print "creating preview..."
    if opts.preview:
        plot_preview()

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
                    request_batch.increase_downstreamvolume(len(pkt.getlayer(IP)))

    #add the last batch
    if request_batch._requestURL != "": # check wheter the requestbatch has been touched before
        processed_batches.append(request_batch)


def update_requestdomain(domain):
    #Update Database here
    global request_batch
    global processed_batches


    if domain == request_batch.get_requesturl():
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
    print '-' * 23
    print 'Statistics for http_gets:'
    print 'mean: %f' % (np.mean(http_gets))
    print 'variance: %f' % (np.var(http_gets))
    print 'standard deviation: %f' % (np.sqrt(np.var(http_gets)))

    hist_gets = Pmf.MakeHistFromList(http_gets)
    http_vals, http_freqs = hist_gets.Render()

    print '-' * 23
    print 'Statistics for dns requests:'
    print 'mean: %f' % (np.mean(dns_reqs))
    print 'variance: %f' % (np.var(dns_reqs))
    print 'standard deviation: %f' % (np.sqrt(np.var(dns_reqs)))

    hist_dns = Pmf.MakeHistFromList(dns_reqs)
    dns_vals, dns_freqs = hist_dns.Render()

    print '-' * 23
    print 'Statistics for downstream volume:'
    print 'mean: %f' % (np.mean(downstream_vols))
    print 'variance: %f' % (np.var(downstream_vols))
    print 'standard deviation: %f' % (np.sqrt(np.var(downstream_vols)))

    hist_vols = Pmf.MakeHistFromList(downstream_vols)
    vols_vals, vols_freqs = hist_vols.Render()

    plt.figure(1)
    plt.subplot(321)
    plt.plot(xaxis, http_gets, 'rx')
    plt.axhline(y=np.mean(http_gets))
    plt.ylabel('Nr. of HTTP GET requests')
    plt.xlabel('Batch Nr.')

    plt.subplot(322)
    plt.bar(http_vals, http_freqs)
    plt.xlabel('# of http GET requests')
    plt.ylabel('frequency')

    plt.subplot(323)
    plt.plot(xaxis, dns_reqs, 'gx')
    plt.axhline(y=np.mean(dns_reqs))
    plt.ylabel('Nr. of DNS requests')
    plt.xlabel('Batch Nr.')

    plt.subplot(324)
    plt.bar(dns_vals, dns_freqs)
    plt.xlabel('# of http dns requests')
    plt.ylabel('frequency')

    plt.subplot(325)
    plt.plot(xaxis, downstream_vols, 'bx')
    plt.axhline(y=np.mean(downstream_vols))
    plt.ylabel('Downstream volume in Bytes')
    plt.xlabel('Batch Nr.')

    plt.subplot(326)
    plt.bar(vols_vals, vols_freqs)
    plt.xlabel('downstream size of request')
    plt.ylabel('frequency')

    plt.show()



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

if __name__=="__main__":
   main()

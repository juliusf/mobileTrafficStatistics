#!/usr/bin/python2.7

from RequestBatch import RequestBatch
import optparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import sqlite3
import Pmf
import Cdf
import pdb
import socket
import sys

#constants
opts = None
args = None
processed_mobile_batches = []
processed_desktop_batches = []

mobile_http_gets = []
mobile_dns_reqs = []
mobile_downstream_vols = []
mobile_xaxis = []
mobile_nr_of_host_contacts = []
mobile_upstream_vols = []
mobile_nr_of_connections = []
mobile_nr_of_webbugs = []

desktop_http_gets = []
desktop_dns_reqs = []
desktop_downstream_vols = []
desktop_xaxis = []
desktop_nr_of_host_contacts = []
desktop_upstream_vols = []
desktop_nr_of_connections = []
desktop_nr_of_webbugs = []

mobile_per_connection_volume = []
desktop_per_connection_volume = []

def main():
    global opts
    global args

    # CLI Option parser
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', help='specifies the sqlite database which contains the experiment resulsts')
    parser.add_option('-d', '--dns', action="store_true", default=False, help='performs a DNS reverse lookup for every connection')
    (opts, args) = parser.parse_args()
    
    if opts.file is None:
        print "You haven't specified any sqlite file.\n"
        parser.print_help()
        exit(-1)

    #Loading of Sql
    sql = "select * from desktopMeasurement"
    read_from_sql(sql, processed_desktop_batches)
    sql = "select * from mobileMeasurement"
    read_from_sql(sql, processed_mobile_batches)
    process_batches()
    #per connection statistics
    extract_all_connections()

    if opts.dns == True:
        perform_reverse_dns_lookup("mobile")
        perform_reverse_dns_lookup("desktop")

    pp = PdfPages('multipage.pdf')
    plot_downstream_ccdf(1, 211)
    plot_downstream_comparative(1,212)
    plt.savefig(pp, format='pdf')

    plot_downstream_comparative_ccdf(2,111)
    plt.savefig(pp, format='pdf')
    
    plot_get_count_ccdf(3,211)
    plot_get_request_comparative(3,212)
    plt.savefig(pp, format='pdf')
    
    plot_get_comparative_ccdf(4,111)
    plt.savefig(pp, format='pdf')

    plot_dns_count_ccdf(5,211)
    plot_dns_request_comparative(5,212)
    plt.savefig(pp, format='pdf')

    plot_dns_comparative_ccdf(6,111)
    plt.savefig(pp, format='pdf')

    plot_nr_of_host_contacts_ccdf(7,211)
    plot_nr_of_host_contacts_comparative(7,212)
    plt.savefig(pp, format='pdf')

    plot_nr_of_host_contacts_comparative_ccdf(8,111)
    plt.savefig(pp, format='pdf')

    plot_nr_of_connections_ccdf(9,211)
    plot_nr_of_connections_comparative(9,212)
    plt.savefig(pp, format='pdf')

    plot_nr_of_connections_comparative_ccdf(10,111)
    plt.savefig(pp, format='pdf')

    plot_nr_of_webbugs_ccdf(11,211)
    plot_nr_of_webbugs_comparative(11,212)
    plt.savefig(pp, format='pdf')
    
    plot_nr_of_webbugs_comparative_ccdf(12,111)
    plt.savefig(pp, format='pdf')

    plot_per_connection_downstream_ccdf(13, 111)
    plt.savefig(pp, format='pdf')
    pp.close()





def plot_downstream_ccdf(plotnumber, subplot_number):
    global processed_mobile_batches
    global processed_desktop_batches
    global mobile_downstream_vols 
    global desktop_downstream_vols 

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(mobile_downstream_vols, 'mobile_downstream_vols')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_downstream_vols, 'desktop_downstream_vols')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Downstream Volume (Bytes)')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()
    plt.legend()

def plot_get_count_ccdf(plotnumber, subplot_number):
    global processed_mobile_batches
    global processed_desktop_batches
    global mobile_http_gets 
    global desktop_http_gets

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(mobile_http_gets, 'mobile_gets')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_http_gets, 'desktop_gets')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of http GET requests')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()
    plt.legend()

def plot_dns_count_ccdf(plotnumber, subplot_number):
    global processed_mobile_batches
    global processed_desktop_batches
    global desktop_dns_reqs 
    global mobile_dns_reqs


    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(mobile_dns_reqs, 'mobile_dns')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_dns_reqs, 'desktop_dns')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of DNS requests')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()
    plt.legend()

def plot_nr_of_connections_ccdf(plotnumber, subplot_number):
    global processed_mobile_batches
    global processed_desktop_batches
    global mobile_nr_of_connections
    global desktop_nr_of_connections

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(mobile_nr_of_connections, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_nr_of_connections, 'desktop_dns')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of Connections')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()
    plt.legend()

def plot_nr_of_host_contacts_ccdf(plotnumber, subplot_number):
    global processed_mobile_batches
    global processed_desktop_batches
    global mobile_nr_of_host_contacts
    global desktop_nr_of_host_contacts

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(mobile_nr_of_host_contacts, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_nr_of_host_contacts, 'desktop_dns')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of hosts contacted')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()
    plt.legend()

def plot_nr_of_webbugs_ccdf(plotnumber, subplot_number):
    global processed_mobile_batches
    global processed_desktop_batches
    global mobile_nr_of_webbugs
    global desktop_nr_of_webbugs

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(mobile_nr_of_webbugs, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_nr_of_webbugs, 'desktop_dns')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of Webbugs')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()
    plt.legend()
#----------------------------------------------------------------
def plot_downstream_comparative(plotnumber, subplot_number):
    downstream_requests_x = []
    downstream_requests_y = []
    
    for batch in processed_desktop_batches:
        downstream_requests_x.append(batch.get_downstreamvolume())
    for batch in processed_mobile_batches:
        downstream_requests_y.append(batch.get_downstreamvolume())
    
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    maximum = max(max(downstream_requests_y), max(downstream_requests_x) ) #super dirty hack!
    helper_x = np.arange(0,maximum, 10)
    helper_y = helper_x
    helper_y2 = helper_x / 10
    #plt.ylim([0,maximum])
    plt.xlim([1,maximum])
    plt.ylim([1,maximum])
    ax.plot(downstream_requests_x, downstream_requests_y, 'xr')
    ax.plot(helper_x, helper_y, '-g')
    ax.plot(helper_x, helper_y2, '-g')
    plt.ylabel('Downstream volume per request on mobile')
    plt.xlabel('Downstream volume per desktop')
    #plt.xscale('log')
    plt.grid()
    plt.xscale('log')
    plt.yscale('log')

def plot_get_request_comparative(plotnumber, subplot_number):
    get_requests_x = []
    get_requests_y = []

    for batch in processed_desktop_batches:
        get_requests_x.append(batch.get_getrequests())
    for batch in processed_mobile_batches:
        get_requests_y.append(batch.get_getrequests())
    
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    maximum = max(max(get_requests_y) + 50, max(get_requests_x) + 50) #super dirty hack!
    #plt.ylim([0,maximum])
    plt.xlim([1,maximum])
    plt.ylim([1,maximum])
    helper_x = range(maximum)
    helper_y = helper_x
    ax.plot(get_requests_x, get_requests_y, 'xr')
    ax.plot(helper_x, helper_y, '-g')
    plt.ylabel('# GET requests on mobile')
    plt.xlabel('# GET requests on desktop')
    #plt.xscale('log')
    plt.grid()
    plt.xscale('log')
    plt.yscale('log')

def plot_dns_request_comparative(plotnumber, subplot_number):
    dns_requests_x = []
    dns_requests_y = []
    
    for batch in processed_desktop_batches:
        dns_requests_x.append(batch.get_dnsrequests())
    for batch in processed_mobile_batches:
        dns_requests_y.append(batch.get_dnsrequests())

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    maximum = max(max(dns_requests_y) + 50, max(dns_requests_x) + 50) #super dirty hack!
    helper_x = range(maximum)
    helper_y = helper_x
    #plt.ylim([0,maximum])
    plt.xlim([1,maximum])
    plt.ylim([1,maximum])
    ax.plot(dns_requests_x, dns_requests_y, 'xr')
    ax.plot(helper_x, helper_y, '-g')
    plt.ylabel('# DNS requests on mobile')
    plt.xlabel('# DNS requests on desktop')
    #plt.xscale('log')
    plt.grid()
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_nr_of_connections_comparative(plotnumber, subplot_number):
    connections_x = []
    connections_y = []

    for batch in processed_desktop_batches:
        connections_x.append(batch.get_connection_count())
    for batch in processed_mobile_batches:
        connections_y.append(batch.get_connection_count())

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    maximum = max(max(connections_x), max(connections_y) ) #super dirty hack!
    helper_x = np.linspace(0,maximum, 1000000)
    helper_y = helper_x
    helper_y2 = helper_x / 10
    #plt.ylim([0,maximum])
    plt.xlim([1,maximum])
    plt.ylim([1,maximum])
    ax.plot(connections_x, connections_y, 'xr')
    ax.plot(helper_x, helper_y, '-g')
    ax.plot(helper_x, helper_y2, '-g')
    plt.ylabel('# of connections per request on mobile')
    plt.xlabel('# of connections per request on desktop')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_nr_of_host_contacts_comparative(plotnumber, subplot_number):
    host_contacts_x = []
    host_contacts_y = []

    for batch in processed_desktop_batches:
        host_contacts_x.append(batch.get_nr_of_host_contacts())
    for batch in processed_mobile_batches:
        host_contacts_y.append(batch.get_nr_of_host_contacts())

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    maximum = max(max(host_contacts_x), max(host_contacts_y) ) #super dirty hack!
    helper_x = np.linspace(0,maximum, 1000000)
    helper_y = helper_x
    helper_y2 = helper_x / 10
    #plt.ylim([0,maximum])
    plt.xlim([1,maximum])
    plt.ylim([1,maximum])
    ax.plot(host_contacts_x, host_contacts_y, 'xr')
    ax.plot(helper_x, helper_y, '-g')
    ax.plot(helper_x, helper_y2, '-g')
    plt.ylabel('Unique hosts contacted per request on mobile')
    plt.xlabel('Unique hosts contacted per request on desktop')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_nr_of_webbugs_comparative(plotnumber, subplot_number):
    webbugs_x = []
    webbugs_y = []

    for batch in processed_desktop_batches:
        webbugs_x.append(batch.get_nr_of_web_bugs())
    for batch in processed_mobile_batches:
         webbugs_y.append(batch.get_nr_of_web_bugs())

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    maximum = max(max(webbugs_x), max(webbugs_y) ) #super dirty hack!
    helper_x = np.linspace(0,maximum, 1000000)
    helper_y = helper_x
    #helper_y2 = helper_x / 10
    #plt.ylim([0,maximum])
    #plt.xlim([1,maximum])
    #plt.ylim([1,maximum])
    ax.plot(webbugs_x, webbugs_y, 'xr')
    ax.plot(helper_x, helper_y, '-g')
    #ax.plot(helper_x, helper_y2, '-g')
    plt.ylabel('# of Webbugs detected per request on mobile')
    plt.xlabel('# of Webbugs detected per request on desktop')
    #plt.xscale('log')
    #plt.yscale('log')
    plt.grid()
#----------------------------------------------------------------
def plot_downstream_comparative_ccdf(plotnumber, subplot_number):
    downstream_requests_x = []
    downstream_requests_y = []
    ratio = []

    for batch in processed_desktop_batches:
        downstream_requests_x.append(batch.get_downstreamvolume())
    for batch in processed_mobile_batches:
        downstream_requests_y.append(batch.get_downstreamvolume())
    for desktop, mobile in zip(downstream_requests_x, downstream_requests_y):
        ratio.append(float(mobile)/float(desktop))
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(ratio, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile/desktop ratio')
    plt.ylabel('ccdf')
    plt.xlabel('mobile/desktop ratio of downstream')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_get_comparative_ccdf(plotnumber, subplot_number):
    get_requests_x = []
    get_requests_y = []
    ratio = []

    for batch in processed_desktop_batches:
        get_requests_x.append(batch.get_getrequests())
    for batch in processed_mobile_batches:
        get_requests_y.append(batch.get_getrequests())
    for desktop, mobile in zip(get_requests_x, get_requests_y):
        if float(desktop) == 0.0:
            ratio.append(1e400)
        else:
            ratio.append(float(mobile)/float(desktop))
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(ratio, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile/desktop ratio')
    plt.ylabel('ccdf')
    plt.xlabel('mobile/desktop ratio of get requests')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_dns_comparative_ccdf(plotnumber, subplot_number):
    dns_requests_x = []
    dns_requests_y = []
    ratio = []

    for batch in processed_desktop_batches:
        dns_requests_x.append(batch.get_dnsrequests())
    for batch in processed_mobile_batches:
        dns_requests_y.append(batch.get_dnsrequests())
    for desktop, mobile in zip(dns_requests_x, dns_requests_y):
        ratio.append(float(mobile)/float(desktop))
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(ratio, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile/desktop ratio')
    plt.ylabel('ccdf')
    plt.xlabel('mobile/desktop ratio of dns requests')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_nr_of_connections_comparative_ccdf(plotnumber, subplot_number):
    connections_x = []
    connections_y = []
    ratio = []
    for batch in processed_desktop_batches:
        connections_x.append(batch.get_connection_count())
    for batch in processed_mobile_batches:
        connections_y.append(batch.get_connection_count())
    for desktop, mobile in zip(connections_x, connections_y):
        if float(desktop) == 0.0:
            ratio.append(1e400)
        else:
            ratio.append(float(mobile)/float(desktop))
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(ratio, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile/desktop ratio')
    plt.ylabel('ccdf')
    plt.xlabel('mobile/desktop ratio of connections')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_nr_of_host_contacts_comparative_ccdf(plotnumber, subplot_number):
    host_contacts_x = []
    host_contacts_y = []
    ratio = []
    for batch in processed_desktop_batches:
        host_contacts_x.append(batch.get_nr_of_host_contacts())
    for batch in processed_mobile_batches:
        host_contacts_y.append(batch.get_nr_of_host_contacts())
    for desktop, mobile in zip(host_contacts_x, host_contacts_y):
        if float(desktop) == 0.0:
            ratio.append(1e400)
        else:
            ratio.append(float(mobile)/float(desktop))
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(ratio, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile/desktop ratio')
    plt.ylabel('ccdf')
    plt.xlabel('mobile/desktop ratio of host contacts')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()

def plot_nr_of_webbugs_comparative_ccdf(plotnumber, subplot_number):
    webbugs_x = []
    webbugs_y = []
    ratio = []

    for batch in processed_desktop_batches:
        webbugs_x.append(batch.get_nr_of_web_bugs())
    for batch in processed_mobile_batches:
         webbugs_y.append(batch.get_nr_of_web_bugs())
    for desktop, mobile in zip(webbugs_x, webbugs_y):
        if float(desktop) == 0.0:
            ratio.append(1e400)
        else:
            ratio.append(float(mobile)/float(desktop))
    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(ratio, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile/desktop ratio')
    plt.ylabel('ccdf')
    plt.xlabel('mobile/desktop ratio of webbugs')
    plt.xscale('log')
    #plt.yscale('log')
    plt.grid()
#----------------------------------------------------------------
def plot_mobile_longtail_downstream():
    downstream_y = []
    downstream_x = []
    
    for batch in processed_mobile_batches:
        pass
#-----------------------------------------------------------------
def plot_per_connection_downstream_ccdf(plotnumber, subplot_number):
    global mobile_per_connection_volume
    global desktop_per_connection_volume

    plt.figure(plotnumber)
    ax = plt.subplot(subplot_number)
    x_axis, y_axis = list_to_ccdf(mobile_per_connection_volume, 'mobile_downstream_vols')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_per_connection_volume, 'desktop_downstream_vols')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Downstream Volume per connection (Bytes)')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid()
    plt.legend()
#-----------------------------------------------------------------
def read_from_sql(sql_statement, batches):
    conn = sqlite3.connect(opts.file)
    cursor = conn.cursor()
    cursor.execute(sql_statement)

    for entry in cursor.fetchall():
        batch = RequestBatch()
        batch.set_filename(entry[1])
        batch.set_requesturl(entry[2])
        batch.set_getrequests(entry[3])
        batch.set_dnsrequests(entry[4])
        batch.set_downstreamvolume(entry[5])
        batch.set_upstreamvolume(entry[6])
        batch.set_nr_of_host_contacts(entry[7])
        batch.set_connection_count(entry[8])
        batch.set_nr_of_web_bugs(entry[9])

        batches.append(batch)
        conn.close()
def process_batches():
    global processed_mobile_batches
    global processed_desktop_batches

    global mobile_http_gets 
    global mobile_dns_reqs 
    global mobile_downstream_vols 
    global mobile_xaxis 
    global mobile_nr_of_host_contacts
    global mobile_upstream_vols
    global mobile_nr_of_connections
    global mobile_nr_of_webbugs

    global desktop_http_gets 
    global desktop_dns_reqs 
    global desktop_downstream_vols 
    global desktop_xaxis 
    global desktop_nr_of_host_contacts
    global desktop_upstream_vols
    global desktop_nr_of_connections
    global desktop_nr_of_webbugs

    for batch in processed_desktop_batches:

        desktop_http_gets.append(batch.get_getrequests())
        desktop_dns_reqs.append(batch.get_dnsrequests())
        desktop_downstream_vols.append(batch.get_downstreamvolume())
        desktop_xaxis.append(len(desktop_http_gets))
        desktop_nr_of_connections.append(batch.get_connection_count())
        desktop_nr_of_host_contacts.append(batch.get_nr_of_host_contacts())
        desktop_nr_of_webbugs.append(batch.get_nr_of_web_bugs())

    for batch in processed_mobile_batches:

        mobile_http_gets.append(batch.get_getrequests())
        mobile_dns_reqs.append(batch.get_dnsrequests())
        mobile_downstream_vols.append(batch.get_downstreamvolume())
        mobile_xaxis.append(len(mobile_http_gets))
        mobile_nr_of_connections.append(batch.get_connection_count())
        mobile_nr_of_host_contacts.append(batch.get_nr_of_host_contacts())
        mobile_nr_of_webbugs.append(batch.get_nr_of_web_bugs())

def plot_values_and_hist_deprecated():
    processed_mobile_batches
    processed_desktop_batches

    global mobile_http_gets 
    global mobile_dns_reqs 
    global mobile_downstream_vols 
    global mobile_xaxis 

    global desktop_http_gets 
    global desktop_dns_reqs 
    global desktop_downstream_vols 
    global desktop_xaxis 


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
    plt.plot(mobile_xaxis, mobile_http_gets, 'rx')
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
    plt.yscale('log')

    plt.subplot(326)
    plt.bar(vols_vals, vols_freqs)
    plt.xlabel('downstream size of request')
    plt.ylabel('frequency')

    plt.show()

def list_to_ccdf(arr, CdfName):
    array_hist = Pmf.MakeHistFromList(arr)
    array_cdf =  Cdf.MakeCdfFromHist(array_hist, CdfName)
    array_x_axis, array_y_axis = array_cdf.Render()
    return [array_x_axis, cdf_to_ccdf(array_y_axis)]

def cdf_to_ccdf(p):
    ccdf = []
    for x in p:
        ccdf.append(1-x)
    return ccdf

def extract_all_connections():
    global mobile_per_connection_volume
    global desktop_per_connection_volume
    
    sql = "select * from mobileConnections"
    conn = sqlite3.connect(opts.file)
    cursor = conn.cursor()
    cursor.execute(sql)

    for entry in cursor.fetchall():
        mobile_per_connection_volume.append(entry[4])

        sql = "select * from desktopConnections"
    conn = sqlite3.connect(opts.file)
    cursor = conn.cursor()
    cursor.execute(sql)

    for entry in cursor.fetchall():
        desktop_per_connection_volume.append(entry[4])

    conn.close()
def perform_reverse_dns_lookup(target):
    sql = "select * from %sConnections" % (target)
    conn = sqlite3.connect(opts.file)
    cursor = conn.cursor()
    cursor.execute(sql)

    for entry in cursor.fetchall():
        sys.stdout.write('looking up host for ' + str(entry[1]) + ' ... :')
        #print('looking up host for: %s :'), % (entry[1])
        try:
            reverse_dns = socket.gethostbyaddr(entry[1])
        except socket.herror:
             reverse_dns = None, None, None
             print "socket error"
        print('%s') % reverse_dns[0]
        write_back_sql = "update %sConnections SET RDNS='%s' WHERE ID=%s" % (target, reverse_dns[0], str(entry[0]))
        cursor.execute(write_back_sql)
    conn.commit()
    conn.close()

if __name__=="__main__":
    main()



#!/usr/bin/python2.7

from RequestBatch import RequestBatch
import optparse
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import Pmf
import Cdf
import pdb

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

desktop_http_gets = []
desktop_dns_reqs = []
desktop_downstream_vols = []
desktop_xaxis = []
desktop_nr_of_host_contacts = []
desktop_upstream_vols = []
desktop_nr_of_connections = []




def main():
    global opts
    global args


    parser = optparse.OptionParser()
    #commandline options
    parser.add_option('-f', '--file', help='specifies the sqlite database which contains the experiment resulsts')
    (opts, args) = parser.parse_args()
    if opts.file is None:
        print "You haven't specified any sqlite file.\n"
        parser.print_help()
        exit(-1)





 
    sql = "select * from desktopMeasurement"
    read_from_sql(sql, processed_desktop_batches)
    sql = "select * from mobileMeasurement"
    read_from_sql(sql, processed_mobile_batches)

    
    process_batches()
    plot_ccdf()
    plot_ratio()

def read_from_sql(sql_statement, batches):
    conn = sqlite3.connect(opts.file)
    cursor = conn.cursor()
    cursor.execute(sql_statement)

    for entry in cursor.fetchall():
        batch = RequestBatch()
        batch.set_filename(entry[0])
        batch.set_requesturl(entry[1])
        batch.set_getrequests(entry[2])
        batch.set_dnsrequests(entry[3])
        batch.set_downstreamvolume(entry[4])
        batch.set_upstreamvolume(entry[5])
        batch.set_nr_of_host_contacts(entry[6])
        batch.set_connection_count(entry[7 ])

        batches.append(batch)

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

    global desktop_http_gets 
    global desktop_dns_reqs 
    global desktop_downstream_vols 
    global desktop_xaxis 
    global desktop_nr_of_host_contacts
    global desktop_upstream_vols
    global desktop_nr_of_connections

    for batch in processed_desktop_batches:

        desktop_http_gets.append(batch.get_getrequests())
        desktop_dns_reqs.append(batch.get_dnsrequests())
        desktop_downstream_vols.append(batch.get_downstreamvolume())
        desktop_xaxis.append(len(desktop_http_gets))
        desktop_nr_of_connections.append(batch.get_connection_count())
        desktop_nr_of_host_contacts.append(batch.get_nr_of_host_contacts())

    for batch in processed_mobile_batches:

        mobile_http_gets.append(batch.get_getrequests())
        mobile_dns_reqs.append(batch.get_dnsrequests())
        mobile_downstream_vols.append(batch.get_downstreamvolume())
        mobile_xaxis.append(len(mobile_http_gets))
        mobile_nr_of_connections.append(batch.get_connection_count())
        mobile_nr_of_host_contacts.append(batch.get_nr_of_host_contacts())

def plot_values_and_hist():
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

def plot_ccdf():
    global processed_mobile_batches
    global processed_desktop_batches

    global mobile_http_gets 
    global mobile_dns_reqs 
    global mobile_downstream_vols 
    global mobile_xaxis 
    global mobile_nr_of_host_contacts
    global mobile_upstream_vols
    global mobile_nr_of_connections

    global desktop_http_gets 
    global desktop_dns_reqs 
    global desktop_downstream_vols 
    global desktop_xaxis 
    global desktop_nr_of_host_contacts
    global desktop_upstream_vols
    global desktop_nr_of_connections


    plt.figure(1)
    ax = plt.subplot(321)
    x_axis, y_axis = list_to_ccdf(mobile_downstream_vols, 'mobile_downstream_vols')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_downstream_vols, 'desktop_downstream_vols')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Downstream Volume (Bytes)')
    plt.xscale('log')
    plt.legend()
   

    ax = plt.subplot(322)
    x_axis, y_axis = list_to_ccdf(mobile_http_gets, 'mobile_gets')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_http_gets, 'desktop_gets')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of http GET requests')
    #plt.xscale('log')
    plt.legend()


    ax=plt.subplot(323)
    x_axis, y_axis = list_to_ccdf(mobile_dns_reqs, 'mobile_dns')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_dns_reqs, 'desktop_dns')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of DNS requests')
    #plt.xscale('log')
    plt.legend()

    ax=plt.subplot(324)
    x_axis, y_axis = list_to_ccdf(mobile_nr_of_connections, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_nr_of_connections, 'desktop_dns')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of Connections')
    #plt.xscale('log')
    plt.legend()

    ax=plt.subplot(325)
    x_axis, y_axis = list_to_ccdf(mobile_nr_of_host_contacts, 'mobile_connections')
    ax.plot(x_axis, y_axis, '-r', label='mobile')
    x_axis, y_axis = list_to_ccdf(desktop_nr_of_host_contacts, 'desktop_dns')
    ax.plot(x_axis, y_axis, '-g', label='desktop')
    plt.ylabel('ccdf')
    plt.xlabel('Number of hosts contacted')
    plt.xscale('log')
    plt.legend()
    plt.show()

def cdf_to_ccdf(p):
    ccdf = []
    for x in p:
        ccdf.append(1-x)
    return ccdf

def plot_ratio():
    global processed_mobile_batches
    global processed_desktop_batches

    get_requests_x = []
    get_requests_y = []

    dns_requests_x = []
    dns_requests_y = []

    downstream_requests_x = []
    downstream_requests_y = []

    for batch in processed_desktop_batches:
        get_requests_x.append(batch.get_getrequests())
    for batch in processed_mobile_batches:
        get_requests_y.append(batch.get_getrequests())

    for batch in processed_desktop_batches:
        dns_requests_x.append(batch.get_dnsrequests())
    for batch in processed_mobile_batches:
        dns_requests_y.append(batch.get_dnsrequests())

    for batch in processed_desktop_batches:
        downstream_requests_x.append(batch.get_downstreamvolume())
    for batch in processed_mobile_batches:
        downstream_requests_y.append(batch.get_downstreamvolume())

    plt.figure(1)
    ax = plt.subplot(321)
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
    

    ax = plt.subplot(322)
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
   
    ax = plt.subplot(323)
    maximum = max(max(downstream_requests_y), max(downstream_requests_x) ) #super dirty hack!
    helper_x = np.linspace(0,maximum, 1000000)
    helper_y = helper_x
    helper_y2 = helper_x / 10
    #plt.ylim([0,maximum])
    plt.xlim([1,maximum])
    plt.ylim([1,maximum])
    ax.plot(downstream_requests_x, downstream_requests_y, 'xr')
    ax.plot(helper_x, helper_y, '-g')
    ax.plot(helper_x, helper_y2, '-g')
    plt.ylabel('Downstream volume on mobile')
    plt.xlabel('Downstream volume on desktop')
    #plt.xscale('log')
    plt.grid()
    plt.xscale('log')
    plt.yscale('log')

    plt.show()

if __name__=="__main__":
    main()



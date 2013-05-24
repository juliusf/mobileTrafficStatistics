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
processed_batches = []
def main():
    global opts
    global args


    parser = optparse.OptionParser()
    #commandline options
    parser.add_option('-f', '--file', help='specifies the sqlite database which contains the experiment resulsts')
    parser.add_option('-e', '--experiment', help='specifies an experiment from the database')
    parser.add_option('-t', '--type', help='specifies wheter mobile or desktop experiments should be plotted')

    (opts, args) = parser.parse_args()
    if opts.file is None:
        print "You haven't specified any sqlite file.\n"
        parser.print_help()
        exit(-1)



    if not opts.experiment is None:
        sql = "select * from desktopMeasurement where filename='%s'" % (opts.experiment)
        read_from_sql(sql)
        sql = "select * from mobileMeasurement where filename='%s'" % (opts.experiment)
        read_from_sql(sql)

    if opts.type == "desktop":
         sql = "select * from desktopMeasurement"
         read_from_sql(sql)

    if opts.type == "mobile":
        sql = "select * from mobileMeasurement"
        read_from_sql(sql)

    plot_preview()
def read_from_sql(sql_statement):
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

        processed_batches.append(batch)

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
    plt.yscale('log')

    plt.subplot(326)
    plt.bar(vols_vals, vols_freqs)
    plt.xlabel('downstream size of request')
    plt.ylabel('frequency')

    plt.show()
    
    plt.figure(1)
    plt.subplot(321)
    downstream_cdf = Cdf.MakeCdfFromHist(hist_vols, 'downstreamCdf')
    xaxis, yaxis = downstream_cdf.Render()
    plt.plot(xaxis, cdf_to_ccdf(yaxis), '-r')
    plt.ylabel('ccdf')
    plt.xlabel('Downstream Volume (Bytes)')
    plt.yscale('log')
    
    plt.subplot(322)
    gets_cdf = Cdf.MakeCdfFromHist(hist_gets, 'http_gets_Cdf')
    xaxis, yaxis = gets_cdf.Render()
    plt.plot(xaxis, cdf_to_ccdf(yaxis), '-g')
    plt.ylabel('ccdf')
    plt.xlabel('Number of http GET requests')
    plt.yscale('log')

    plt.subplot(323)
    dns_cdf = Cdf.MakeCdfFromHist(hist_dns, 'dns_Cdf')
    xaxis, yaxis = dns_cdf.Render()
    plt.plot(xaxis, cdf_to_ccdf(yaxis), '-b')
    plt.ylabel('ccdf')
    plt.xlabel('Number of DNS requests')
    plt.yscale('log')
    plt.show()



def cdf_to_ccdf(p):
    ccdf = []
    for x in p:
        ccdf.append(1-x)
    return ccdf



if __name__=="__main__":
    main()



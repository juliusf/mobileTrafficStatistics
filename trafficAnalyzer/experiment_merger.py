#!/usr/bin/python2
from RequestBatch import RequestBatch
from Connection import Connection
from Experiment import Experiment
import socket
import sys
import sqlite3
import re
import json
import os

experiments = []
cdn_regex = []
current_experiment = None
processed_batches = []

def main(argv):
    result_mobile_http_gets = []
    result_mobile_dns_reqs = []
    result_mobile_downstream_vols = []
    result_mobile_xaxis = []
    result_mobile_nr_of_host_contacts = []
    result_mobile_upstream_vols = []
    result_mobile_nr_of_connections = []
    result_mobile_nr_of_webbugs = []

    result_desktop_http_gets = []
    result_desktop_dns_reqs = []
    result_desktop_downstream_vols = []
    result_desktop_xaxis = []
    result_desktop_nr_of_host_contacts = []
    result_desktop_upstream_vols = []
    result_desktop_nr_of_connections = []
    result_desktop_nr_of_webbugs = []
    global experiments
    global current_experiment
    global processed_batches

    json_data=open('cdn_regex.json').read()
    data = json.loads(json_data)
    for entry in data["cdns"]:
        cdn_regex.append(re.compile(entry["pattern"], re.I))

    for file in sys.argv:
        if not file == sys.argv[0]: # if I got a penny for every dirty hack I ever used...
            exp = Experiment()
            current_experiment = exp
            print file
            sql = "select * from desktopMeasurement"
            read_batch_from_sql(file, sql, exp._processed_desktop_batches)
            sql = "select * from mobileMeasurement"
            read_batch_from_sql(file, sql, exp._processed_mobile_batches)

            sql = "select * from desktopConnections"
            read_connection_from_sql(file,sql, exp._mobile_connections)
            sql = "select * from mobileConnections"
            read_connection_from_sql(file,sql, exp._mobile_connections)
            experiments.append(exp)
            #assign the connections to the corresponding batches
            for conn in exp._mobile_connections:
                exp._processed_mobile_batches[conn._parentBatchID - 1]._active_connections.append(conn)
            for conn in exp._desktop_connections:
                exp._processed_desktop_batches[conn._parentBatchID - 1]._active_connections.append(conn)

        create_table("gold")
    ######################HARDCODED STUFF
    exp1 = experiments[0]
    exp2 = experiments[1]
    exp3 = experiments[2]

    for x,y,z in zip(exp1._processed_mobile_batches, exp2._processed_mobile_batches, exp3._processed_mobile_batches):
        batch = RequestBatch()
        batch._getCount = (x._getCount + y._getCount + z._getCount ) / 3.0
        batch._dnsCount = (x._dnsCount + y._dnsCount + z._dnsCount ) / 3.0
        batch._downstreamVolumeBytes = (x._downstreamVolumeBytes + y._downstreamVolumeBytes + z._downstreamVolumeBytes ) / 3.0
        batch._nr_of_host_contacts = (x._nr_of_host_contacts + y._nr_of_host_contacts + z._nr_of_host_contacts ) / 3.0
        batch._upstreamVolumeBytes = (x._upstreamVolumeBytes + y._upstreamVolumeBytes + z._upstreamVolumeBytes ) / 3.0
        batch._connectionCount = (x._connectionCount + y._connectionCount + z._connectionCount ) / 3.0
        batch._nr_of_webbgus = (x._nr_of_webbgus + y._nr_of_webbgus + z._nr_of_webbgus ) / 3.0
        batch._requestURL = x._requestURL
        processed_batches.append(batch)
    print len(processed_batches)
    for x,y,z in zip(exp1._processed_desktop_batches, exp2._processed_desktop_batches, exp3._processed_desktop_batches):
        batch = RequestBatch()
        batch._getCount = (x._getCount + y._getCount + z._getCount ) / 3.0
        batch._dnsCount = (x._dnsCount + y._dnsCount + z._dnsCount ) / 3.0
        batch._downstreamVolumeBytes = (x._downstreamVolumeBytes + y._downstreamVolumeBytes + z._downstreamVolumeBytes ) / 3.0
        batch._nr_of_host_contacts = (x._nr_of_host_contacts + y._nr_of_host_contacts + z._nr_of_host_contacts ) / 3.0
        batch._upstreamVolumeBytes = (x._upstreamVolumeBytes + y._upstreamVolumeBytes + z._upstreamVolumeBytes ) / 3.0
        batch._connectionCount = (x._connectionCount + y._connectionCount + z._connectionCount ) / 3.0
        batch._nr_of_webbgus = (x._nr_of_webbgus + y._nr_of_webbgus + z._nr_of_webbgus ) / 3.0
        batch._requestURL = x._requestURL
        processed_batches.append(batch)
    print len(processed_batches)

   # for x,y,z in zip(exp1._processed_mobile_batches, exp2._processed_mobile_batches, exp3._processed_mobile_batches)
     #   result_mobile_http_gets.append((x+y+z)/3.0)
    add_to_database("gold")
def read_batch_from_sql(sql_file, sql_statement, batches):
    conn = sqlite3.connect(str(sql_file))
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

def read_connection_from_sql(sql_file, sql_statement, connections):
    conn = sqlite3.connect(sql_file)
    cursor = conn.cursor()
    cursor.execute(sql_statement)

    for entry in cursor.fetchall():
        conn = Connection()
        conn._dst_IP = entry[1]
        conn._DNS = entry[2]
        conn._rDNS = entry[3]
        conn._current_volume = entry[4]
        conn._parentBatchID = entry[6]
        
        for pattern in cdn_regex:
            if pattern.search(entry[2]) or pattern.search(entry[3]):
                conn._is_CDN_connection = True
                break
        connections.append(conn)


def create_table(original_filename):
    if os.path.exists(original_filename + '.sqlite'):
        os.remove(original_filename + '.sqlite')

    conn = sqlite3.connect(original_filename + '.sqlite')
    c = conn.cursor()
    c.execute('''create table mobileMeasurement( ID INTEGER PRIMARY KEY, fileName text,  batchID text, getRequests INTEGER, dnsRequests INTEGER, downstreamVolume INTEGER, upstreamVolume INTEGER, numberOfHostsContacted INTEGER, numberOfConnections INTEGER, nrOfWebBugs INTEGER)''' )
    conn.commit()

    c = conn.cursor()
    c.execute('''create table desktopMeasurement( ID INTEGER PRIMARY KEY, fileName text,  batchID text, getRequests INTEGER, dnsRequests INTEGER, downstreamVolume INTEGER, upstreamVolume INTEGER, numberOfHostsContacted INTEGER, numberOfConnections INTEGER, nrOfWebBugs INTEGER)''' )
    conn.commit()

    c = conn.cursor()
    c.execute('''create table mobileConnections( ID INTEGER PRIMARY KEY, ipAddr TEXT, DNS TEXT, RDNS TEXT, volume INTEGER, batchID text, parentBatchID INTEGER)''')
    c.close()

    c = conn.cursor()
    c.execute('''create table desktopConnections( ID INTEGER PRIMARY KEY, ipAddr TEXT, DNS TEXT, RDNS TEXT, volume INTEGER, batchID text, parentBatchID INTEGER)''')
    c.close()

def add_to_database(original_filename):
    global processed_batches
    global dut_type
    global filename
    sqlconn = sqlite3.connect(original_filename + '.sqlite')
    c = sqlconn.cursor()
    mobile_data = []
    desktop_data = []

    mobile_connection = []
    desktop_connection = []
    desktop_id_counter = 1
    mobile_id_counter = 1
    for batch in processed_batches:
        if '| MOBILE |' in batch.get_requesturl():
            mobile_data.append( ("gold", batch._requestURL, batch.get_getrequests(), batch.get_dnsrequests(),  batch.get_downstreamvolume(), 0,  batch.get_nr_of_host_contacts(), batch.get_connection_count(), batch.get_nr_of_web_bugs() ) )
           # for connection in batch.get_connections():
            #    mobile_connection.append( (connection.get_dst_ip(), connection.get_dns(), connection.get_volume(), batch.get_requesturl(), mobile_id_counter))
            mobile_id_counter += 1
        if '| DESKTOP |' in batch.get_requesturl():
            desktop_data.append( ("gold", batch._requestURL, batch.get_getrequests(), batch.get_dnsrequests(), batch.get_downstreamvolume(), 0, batch.get_nr_of_host_contacts(), batch.get_connection_count(), batch.get_nr_of_web_bugs() ) )
          #  for connection in batch.get_connections():
          #      desktop_connection.append( (connection.get_dst_ip(), connection.get_dns(), connection.get_volume(), batch.get_requesturl(), desktop_id_counter))
            desktop_id_counter += 1
    if mobile_data:
        c.executemany('insert into mobileMeasurement values (null,?,?,?,?,?,?,?,?,?)', mobile_data)
    if desktop_data:
        c.executemany('insert into desktopMeasurement values (null,?,?,?,?,?,?,?,?,?)', desktop_data)

    if mobile_connection:
        c.executemany('insert into mobileConnections values (null,?,?,null,?,?,?)', mobile_connection)
    if desktop_connection:
        c.executemany('insert into desktopConnections values (null,?,?,null,?,?,?)', desktop_connection)
    sqlconn.commit()

if __name__ == "__main__":
   main(sys.argv[1:])
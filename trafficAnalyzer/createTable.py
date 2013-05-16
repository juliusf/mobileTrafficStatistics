import sqlite3

conn = sqlite3.connect('measurements.sqlite')
c = conn.cursor()
c.execute('''create table mobileMeasurement( fileName text,  batchID text, getRequests INTEGER, dnsRequests INTEGER, downstreamVolume INTEGER, upstreamVolume INTEGER)''' )
conn.commit()

c = conn.cursor()
c.execute('''create table desktopMeasurement( fileName text,  batchID text, getRequests INTEGER, dnsRequests INTEGER, downstreamVolume INTEGER, upstreamVolume INTEGER)''' )
conn.commit()

c.close()

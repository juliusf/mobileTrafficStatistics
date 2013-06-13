from Connection import Connection
from scapy.packet import *
from scapy.layers.inet import *
class RequestBatch(object):
	"""docstring for RequestBock"""

	def __init__(self):
		self._getCount = 0
		self._dnsCount = 0
		self._downstreamVolumeBytes = 0
		self._upstreamVolumeBytes = 0
		self._requestURL = ""
		self._fileName = ""
		self._connectionCount = 0
		self._nr_of_host_contacts = 0
		self._nr_of_webbgus = 0  #Without DNS contact!
		self._active_connections = []
		



	def increment_nr_of_web_bugs(self):
		if self._requestURL != "":
			self._nr_of_webbgus += 1
		else:
			print "WARNING: unable to assign packet to RequestBatch"
	def get_nr_of_web_bugs(self):
		return self._nr_of_webbgus
		
	def set_nr_of_web_bugs(self, number):
		self._nr_of_webbgus = number
		
	def increment_nr_of_host_contacts(self):
		if self._requestURL != "":
			self._nr_of_host_contacts += 1
		else:
			print "WARNING: unable to assign packet to RequestBatch"
	def get_nr_of_host_contacts(self):
		return self._nr_of_host_contacts
		
	def set_nr_of_host_contacts(self, number):
		self._nr_of_host_contacts = number

	def increment_connection_count(self):
		if self._requestURL != "":
			self._connectionCount += 1
		else:
			print "WARNING: unable to assign packet to RequestBatch"
	def set_connection_count(self, count):
		self._connectionCount = count

	def get_connection_count(self):
		return self._connectionCount

	def increment_getrequests(self):
		if self._requestURL != "":
			self._getCount += 1
		else:
			print "WARNING: unable to assign packet to RequestBatch"
	def set_getrequests(self, nr_of_requests):
		self._getCount = nr_of_requests

	def get_getrequests(self):
		return self._getCount
	
	def increment_dnsrequests(self):
		if self._requestURL != "":
			self._dnsCount += 1
		else:
			print "WARNING: unable to assign packet to RequestBatch"

	def get_dnsrequests(self):
		return self._dnsCount

	def set_dnsrequests(self, number_of_dnsrequests):
		self._dnsCount = number_of_dnsrequests

	def increase_downstreamvolume(self, bytes):
		if self._requestURL != "":
			self._downstreamVolumeBytes += bytes
		else:
			print "WARNING: unable to assign packet to RequestBatch"
	def set_downstreamvolume(self, downstream_size):
		self._downstreamVolumeBytes = downstream_size

	def get_downstreamvolume(self):
		return self._downstreamVolumeBytes	

	def set_requesturl(self, requestURL):
		self._requestURL = requestURL
		#print "url updated to: %s" % (self._requestURL)

	def get_requesturl(self):
		return self._requestURL

	def increase_upstreamvolume(self, bytes):
		if self._requestURL != "":
			self._upstreamVolumeBytes += bytes
		else:
			print "WARNING: unable to assign packet to RequestBatch"
	def get_upstreamvolume(self):
		return self._upstreamVolumeBytes

	def set_upstreamvolume(self, bytes):
		self._upstreamVolumeBytes = bytes

	def set_filename(self, filename):
		self._fileName = filename

	def get_filename(self):
		return self._fileName

	def add_new_connection(self, packet):
		conn = Connection()
		tcp = packet.getlayer(TCP)
		conn.set_dst_ip(packet.getlayer(IP).dst)
		conn._curr_dst_IP = packet.getlayer(IP).dst
		conn._curr_src_IP = packet.getlayer(IP).src
		conn._curr_dst_port = tcp.dport
		conn._curr_src_port = tcp.sport
		conn.increase_volume(len(packet.getlayer(IP)))
		self._active_connections.append(conn)
		conn._current_packet_number += 1


	def check_connection(self, other):
		other_tcp = other.getlayer(TCP) 
		other_ip = other.getlayer(IP)
		for conn in self._active_connections:
			if other_ip.src == conn._curr_dst_IP and other_ip.dst == conn._curr_src_IP:
				if other_tcp.dport == conn._curr_src_port and other_tcp.dport == conn._curr_src_port:
					conn.increase_volume(len(other.getlayer(IP)))
					conn._curr_dst_IP = other_ip.dst
					conn._curr_src_IP = other_ip.src
					conn._curr_dst_port = other_tcp.dport
					conn._curr_src_port = other_tcp.sport
					conn._current_packet_number += 1
			else:
				if other_ip.src == conn._curr_src_IP and other_ip.dst == conn._curr_dst_IP:
					if other_tcp.dport == conn._curr_dst_port and other_tcp.dport == conn._curr_dst_port:
						conn.increase_volume(len(other.getlayer(IP)))
						conn._current_packet_number += 1
	def get_connections(self):
		return self._active_connections


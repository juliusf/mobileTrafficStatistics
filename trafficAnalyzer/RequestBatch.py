class RequestBatch(object):
	"""docstring for RequestBock"""

	def __init__(self):
		self._getCount = 0
		self._dnsCount = 0
		self._downstreamVolumeBytes = 0
		self._upstreamVolumeBytes = 0
		self._requestURL = ""
		self._fileName = ""


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
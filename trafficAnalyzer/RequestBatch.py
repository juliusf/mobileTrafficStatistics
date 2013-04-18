class RequestBatch(object):
	"""docstring for RequestBock"""

	def __init__(self):
		self._getCount = 0
		self._dnsCount = 0
		self._downstreamVolumeBytes = 0
		self._requestURL = ""

	def increment_getrequests(self):
		if self._requestURL != "":
			self._getCount += 1
		else:
			print "WARNING: unable to assign packet to RequestBatch"
			
	def get_getrequests(self):
		return self._getCount
	
	def increment_dnsrequests(self):
		if self._requestURL != "":
			self._dnsCount += 1
		else:
			print "WARNING: unable to assign packet to RequestBatch"

	def get_dnsrequests(self):
		return self._dnsCount

	def increase_downstreamvolume(self, bytes):
		if self._requestURL != "":
			self._downstreamVolumeBytes += bytes
		else:
			print "WARNING: unable to assign packet to RequestBatch"
	
	def get_downstreamvolume(self):
		return self._downstreamVolumeBytes	

	def set_requesturl(self, requestURL):
		self._requestURL = requestURL
		#print "url updated to: %s" % (self._requestURL)

	def get_requesturl(self):
		return self._requestURL

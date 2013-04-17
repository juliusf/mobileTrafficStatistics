class RequestBatch(object):
	"""docstring for RequestBock"""
	
	#_getCount = 0
	#_dnsCount = 0
	#_downstreamVolumeBytes = 0
	#_requestURL = ""
	def __init__(self):
		self._getCount = 0
		self._dnsCount = 0
		self._downstreamVolumeBytes = 0
		self._requestURL = ""

	def incrementNumberOfGetRequests(self):
		print self._requestURL
		if self._requestURL != "":
			self._getCount += 1
		else:
			print "WARNING: undefined packet captured!: %s" % (self)
			

	def incrementNumberOfDNSRequests(self):
		global _dnsCount
		if _ != "":
			_dnsCount += 1
		else:
			print "WARNING: undefined packet captured!"


	def increaseDownstreamVolume(self, bytes):
		global _downstreamVolumeBytes
		if _requestURL != "":
			_downstreamVolumeBytes += bytes
		else:
			print "WARNING: unable to assign packet to RequestBatch"
		

	def setRequestURL(self, requestURL):
		self._requestURL = requestURL
		print "url updated to: %s" % (self._requestURL)


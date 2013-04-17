class RequestBatch(object):
	"""docstring for RequestBock"""
	
	_getCount = 0
	_dnsCount = 0
	_downstreamVolumeBytes = 0
	_requestURL = ""
	def __init__(self):
		pass

	def increasNumberOfGetRequests():
		if _requestURL != "":
			_getCount += 1
		else:
			print "WARNING: undefined packet captured!"

	def increaseNumberOfDNSRequests():
		if _requestURL != "":
			_dnsCount += 1
		else:
			print "WARNING: undefined packet captured!"


	def increaseDownstreamVolume(self, bytes):
		if _requestURL != "":
			_downstreamVolumeBytes += bytes
		else:
			print "WARNING: undefined packet captured!"
		

	def setRequestURL(self, requestURL):
		_requestURL = requestURL
		print "url updated to: %s" % (_requestURL)


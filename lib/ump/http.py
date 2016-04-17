import urllib2
from webtunnel import noredirs
noredirects=[]
noredirects.extend(noredirs)
from cloudfare import noredirs
noredirects.extend(noredirs)


class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"

class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):

	def http_error_302(self, req, fp, code, msg, headers):
		for no302 in noredirects:
			if no302.endswith("/") and no302 == req.get_full_url(): 
				if no302==req.get_full_url():
					#return self.parent._open(req)
					return (req, fp, 200, msg, headers)
			elif no302 in req.get_full_url():
				#return self.parent._open(req)
				return (req, fp, 200, msg, headers)
		else:
			result=urllib2.HTTPRedirectHandler.http_error_302(self,req, fp, code, msg, headers)
			result.status=code
			return result
		
class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
	"""Process HTTP error responses."""
	handler_order = 1000  # after all other processing

	def http_response(self, request, response):
		if response.code==302:
			for no302 in noredirects:
				if no302.endswith("/") and no302 == request.get_full_url(): 
					if no302==request.get_full_url():
						return response
				elif no302 in request.get_full_url():
					return response
		return urllib2.HTTPErrorProcessor.http_response(self, request, response)
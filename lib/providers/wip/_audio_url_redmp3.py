def run(hash,ump,referer=None):
	print hash
	print "http://redmp3.su"+hash
	return {"url":{"url":"http://redmp3.su"+hash,"referer":referer}}
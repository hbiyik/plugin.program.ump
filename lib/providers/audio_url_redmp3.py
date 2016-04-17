def run(hash,ump,referer=None):
	u=ump.absuri("http://redmp3.su",hash)
	while True:
		u=u.replace("&amp;","&")
		if not "&amp;" in u: break
	return {"url":{"url":u,"referer":referer}}
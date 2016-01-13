import re
import urlparse

def run(hash,ump,referer=None):
	url = "http://yourupload.com/embed/%s" % hash
	src = ump.get_page(url, "utf-8")
	js=re.findall("setup\(({.*?logo\:)",src,re.DOTALL)
	link=re.findall("file: '(.*?)'",js[0])
	return {"url": link[0]}

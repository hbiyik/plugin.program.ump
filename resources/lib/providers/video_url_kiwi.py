import urlparse
import re
import urllib2

def run(hash,ump,referer=None):
	src = ump.get_page("http://v.kiwi.kz/v2/"+hash,"utf8")
	fv=re.findall('flashvars="(.*?)"',src)[0]
	keys=urlparse.parse_qs(urllib2.unquote(fv))
	return {keys["title"][0]:keys["url"][0]}
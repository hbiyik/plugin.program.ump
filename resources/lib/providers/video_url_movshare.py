import urllib
import re
import urlparse
import time

def run(hash,ump,referer=None):
	src=ump.get_page("http://www.movshare.net/video/"+hash,"utf8")
	key=re.findall('<input type="hidden" name="stepkey" value="(.*?)">',src)
	src=ump.get_page("http://www.wholecloud.net//video/"+hash,"utf8",data={"stepkey":key[0],"submit":"submit"})
	[key]=re.findall("flashvars\.filekey=\"(.*?)\"",src)
	key=urllib.quote_plus(key).replace(".","%2E")
	url="http://www.movshare.net/api/player.api.php?file="+hash+"&key="+key
	html = ump.get_page(url,"utf8")
	dic=urlparse.parse_qs(html)
	for key in dic.keys():
		if not key=="url":
			dic.pop(key)
		else:
			dic[key]=dic[key][0]
	return dic
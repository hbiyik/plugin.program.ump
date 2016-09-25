import re
import urllib
import urlparse


def run(hash,ump,referer=None):
	url="http://www.wholecloud.net/video/"+hash
	src=ump.get_page(url,"utf8")
	key=re.findall('<input type="hidden" name="stepkey" value="(.*?)">',src)
	src=ump.get_page(url,"utf8",data={"stepkey":key[0],"submit":"submit"})
	vid=re.findall('<source src="(.*?)"',src)[0]
	return {"video":{"url":vid,"referer":url}}
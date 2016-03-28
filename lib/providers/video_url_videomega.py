import re
from third import unpack

def run(hash,ump,referer=None):
	link="http://videomega.tv/iframe.php?ref="+hash
	src = ump.get_page(link,"utf-8",referer=referer)
	packed=re.findall("(eval\(function\(p.*?)\n",src)
	code=unpack.unpack(packed[0]).replace("\\","")
	url=re.findall('"src","(.*?)"',code)[0]
	return {"video":{"url":url,"referer":link}}
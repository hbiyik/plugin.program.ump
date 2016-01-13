import re
from third import unpack

def run(hash,ump,referer=None):
	src = ump.get_page("http://videomega.tv/view.php?ref="+hash["key"],"utf-8",referer=hash["referer"])
	packed=re.findall("(eval\(function\(p.*?)\n",src)
	code=unpack.unpack(packed[0]).replace("\\","")
	url=re.findall('"src","(.*?)"',code)[0]
	return {"video":url}
import urlparse
import re
import time
from third import unpack
domain="http://www.promptfile.com/"
def run(hash,ump,referer=None):
	src = ump.get_page(domain+"l/"+hash,"utf8",referer=referer)
	data={"chash":re.findall('name="chash" value="(.*?)"',src)[0]}
	src = ump.get_page(domain+"l/"+hash,"utf8",data=data,referer=domain+"l/"+hash)
	files=re.findall("url: '(.*?)'.*?canvas\: \{",src,re.DOTALL)
	return {"video":{"url":files[0],"referer":domain+"l/"+hash}}
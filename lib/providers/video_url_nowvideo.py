import re
import urlparse


dmn="http://www.nowvideo.sx"
def run(hash,ump,referer=None):
	link=dmn+"/video/"+hash
	src=ump.get_page(link,"utf-8",referer=referer)
	stepkey=re.findall('name="stepkey" value="(.*?)"',src)
	if len(stepkey)>0:
		src=ump.get_page(link,"utf-8",data={"stepkey":stepkey[0],"submit":"submit"},referer=link)
		sources=re.findall('<source src="(.*?)"',src)
		return {"video":sources[0]}
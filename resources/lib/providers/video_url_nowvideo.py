import re
import urlparse

dmn="http://www.nowvideo.sx"
def run(hash,ump,referer=None):
	link=dmn+"/video/"+hash
	src=ump.get_page(link,"utf-8",referer=referer)
	stepkey=re.findall('name="stepkey" value="(.*?)"',src)
	if len(stepkey)>0:
		src=ump.get_page(link,"utf-8",data={"stepkey":stepkey[0],"submit":"submit"},referer=link)
		domain=re.findall('flashvars.domain="(.*?)"',src)
		file=re.findall('flashvars.file="(.*?)"',src)
		key=re.findall('fkzd="(.*?)"',src)
		url=domain[0]+"/api/player.api.php"
		data={"file":file[0],"key":key,"cid":1,"cid2":"undefined","cid3":"nowvideo.sx","pass":"undefined","numOfErrors":0,"user":"undefined","pass":"undefined"}
		src=ump.get_page(url,"utf-8",query=data)
		dic=urlparse.parse_qs(src)
		for key in dic.keys():
			if not key=="url":
				dic.pop(key)
			else:
				dic[key]=dic[key][0]
		return dic
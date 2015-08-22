import re
import json
from urllib2 import HTTPError

encoding="utf-8"
domain = 'http://sezonlukdizi.com'


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()
	found=False
	if not i["code"][:2]=="tt" or not is_serie:
		return None

	page=ump.get_page(domain+"/hakkimizda.html",encoding)
	series=re.findall('<li><a href="'+domain+'/diziler(/.*?/).*?" title="(.*?) Sezon ([0-9]*?)"',page)
	for name in names:
		ump.add_log("sezonlukdizi is searching %s"%name)	
		for serie in series:
			l,t,s=serie
			if ump.is_same(t,i["tvshowtitle"]) and int(i["season"])==int(s):
				url=domain+l+str(i["season"])+"-sezon-"+str(i["episode"])+"-bolum"
				try:
					epage=ump.get_page(url+".html",encoding)
				except HTTPError, err:
					if err.code == 404:
						epage=ump.get_page(url+"-sezon-finali.html",encoding)
				ump.add_log("sezonlukdizi matched %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				video_id = re.findall('video_id  \= "([0-9]*?)"',epage)[0]
				part_name = re.findall('var part_name \= "(.*?)"',epage)[0]
				vurl=domain+"/service/get_video_part"
				vpage=ump.get_page(vurl,encoding,data={"video_id":video_id,"part_name":part_name,"page":0},header={"X-Requested-With":"XMLHttpRequest"})
				js=json.loads(vpage)
				vlink={"url":re.findall('<script src="(.*?)"',js["part"]["code"])[0],"referer":domain}
				parts=[{"url_provider_name":"google", "url_provider_hash":vlink}]
				ump.add_mirror(parts,"%s %dx%d %s" % (i["tvshowtitle"],i["season"],i["episode"],i["title"]))				
				return None
				break
	ump.add_log("sezonlukdizi can't match %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
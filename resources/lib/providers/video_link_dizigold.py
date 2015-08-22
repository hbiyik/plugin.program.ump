import re
import json
from urllib2 import HTTPError

encoding="utf-8"
domain = 'http://www.dizigold.net'


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()
	found=False
	if not i["code"][:2]=="tt" or not is_serie:
		return None

	for name in names:
		ump.add_log("dizigold is searching %s"%name)
		data={"aranan":name,"tip":"aranans"}
		page=ump.get_page(domain+"/sistem/ajax.php",encoding,data=data,referer=domain,header={"X-Requested-With":"XMLHttpRequest"})
		series=re.findall('href\="(.*?)".*?h3\>(.*?)\<',page.decode("string-escape"),re.DOTALL)
		for serie in series:
			l,t=serie
			l=l.replace("\\","")
			t=t.replace("\\","")
			print t
			if ump.is_same(t,i["tvshowtitle"]):
				url=l+"/"+str(i["season"])+"-sezon/"+str(i["episode"])+"-bolum"
				try:
					epage=ump.get_page(url,encoding)
				except HTTPError, err:
					if err.code == 404:
						ump.add_log("dizigold can't match %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
						return None
				ump.add_log("dizigold matched %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				video_id = re.findall('view_id="([0-9]*?)"',epage)[0]
				data={"id":video_id,"tip":"view"}
				page=ump.get_page(domain+"/sistem/ajax.php",encoding,data=data,referer=domain,header={"X-Requested-With":"XMLHttpRequest"})
				links=re.findall('"file":"(.*?)", "label":"(.*?)"',page.decode("string-escape"))
				if len(links)>0:
					mirrors={"html5":True}
					for link in links:
						mirrors[link[1].replace("\\","")]=link[0].replace("\\","")
					parts=[{"url_provider_name":"google", "url_provider_hash":mirrors}]
					ump.add_mirror(parts,"%s %dx%d %s" % (i["tvshowtitle"],i["season"],i["episode"],i["title"]))				
					return None
				break
	ump.add_log("dizigold can't match %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
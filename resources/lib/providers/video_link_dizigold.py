# -*- coding: utf-8 -*-
import re
import json
from urllib2 import HTTPError

encoding="utf-8"
domain = 'http://www.dizigold.net'

#note: i dont really care about the mirros on this site only care about gvideos, mirros are vk which are marked private now and mail.ru most of them rarely works randomly
def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()
	found=False
	if not i["code"][:2]=="tt" or not is_serie:
		return None

	for name in names:
		query={"page":"/dizi/aranan_%s"%name}
		page=ump.get_page(domain+"/sistem/arsiv.php",encoding,query=query,referer=domain+"/arsiv",header={"X-Requested-With":"XMLHttpRequest"})
		names=re.findall('<span class="realcuf">(.*?)</span></a>',page)
		links=re.findall('<div class="detay "><a href="(.*?)"></a>',page)
		series=zip(links,names)
		for serie in series:
			found=False
			l,t=serie
			if ump.is_same(t,name):
				url=l+"/"+str(i["season"])+"-sezon/"+str(i["episode"])+"-bolum"
				try:
					epage=ump.get_page(url,encoding)
				except HTTPError, err:
					if err.code == 404:
						ump.add_log("dizigold can't match %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
						return None
				ump.add_log("dizigold matched %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				vid = re.findall('view_id="([0-9]*?)"',epage)
				lselects=re.findall('<small class="realcuf">(.*?)<',epage)
				langs=[]
				for lselect in lselects:
					if ump.is_same(lselect,"Türkçe"):
						langs.append("tr")
					elif ump.is_same(lselect,"Altyazısız"):
						langs.append("or")
					else:
						langs.append("en")
				if len(vid)>0:
					for lang in langs:
						data={"tip":"view","id":vid[0],"dil":lang}
						jsdata1=json.loads(ump.get_page(domain+"/sistem/ajax.php",encoding,referer=url,header={"X-Requested-With":"XMLHttpRequest"},data=data))
						alts=re.findall('trigger\="(.*?)"',jsdata1["alternative"])
						for alt in alts:
							if lang=="tr":
								prefix="[HS:TR]"
							else:
								prefix=""
							data={"id":vid[0],"tip":"view","s":alt,"dil":lang}
							jsdata2=json.loads(ump.get_page(domain+"/sistem/ajax.php",encoding,referer=url,header={"X-Requested-With":"XMLHttpRequest"},data=data))
							player=re.findall('iframe src="(.*?)"',jsdata2["data"])
							if len(player)>0:
								mname="%s%s %dx%d %s" % (prefix,i["tvshowtitle"],i["season"],i["episode"],i["title"])
								pdata=ump.get_page(player[0],encoding,referer=url)
								vkext=re.findall('"(.*?video\_ext\.php.*?)"',pdata)
								if len(vkext)>0:
									parts=[{"url_provider_name":"vkext", "url_provider_hash":vkext[0].replace("\\","")}]
									ump.add_mirror(parts,mname)
									found=True
									continue
								veterok=re.findall('veterok\.tv\/v\/(.*?)"',pdata)
								if len(veterok)>0:
									ump.add_mirror([{"url_provider_name":"veterok","url_provider_hash":veterok[0]}],mname)
									continue
								cloudy=re.findall('cloudy.*?embed\.php\?id\=(.*?)"',pdata)
								if len(cloudy)>0:
									ump.add_mirror([{"url_provider_name":"cloudy","url_provider_hash":cloudy[0]}],mname)
									continue
								googles=re.findall('"file":"(.*?)", "label":"(.*?)"',pdata)
								if len(googles)>0:
									softsub=re.findall("file: '.*?\.vtt'",pdata)
									if len(softsub)>0 and prefix=="[HS:TR]":
										prefix=""
									mname="%s%s %dx%d %s" % (prefix,i["tvshowtitle"],i["season"],i["episode"],i["title"])
									parts={}
									for google in googles:
										parts[google[1]]=google[0]
									ump.add_mirror([{"url_provider_name":"google","url_provider_hash":parts}],mname)
									continue	
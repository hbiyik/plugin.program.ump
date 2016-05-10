import re

encoding="utf-8"
domain = 'http://sezonlukdizi.com'


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()

	if not is_serie:
		return None

	for name in names:
		ump.add_log("sezonlukdizi is searching %s"%name)
		page=ump.get_page(domain+"/diziler.asp",encoding,query={"adi":name})
		series=re.findall('href="(.*?)" class="header">(.*?) \(([0-9]{4})\)</a>',page)
		for serie in series:
			l,t,y=serie
			l,t,s=serie
			tag=l.split("/")[-1][:-5]
			if ump.is_same(t,name):
				url=domain+"/"+tag+"/"+str(i["season"])+"-sezon-"+str(i["episode"])+"-bolum.html"
				epage=ump.get_page(url,encoding)
				if "Haydaaa..." in epage:
					continue
				ump.add_log("sezonlukdizi matched %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
				video_ids = re.findall('<div data-id="([0-9]*?)" class="item',epage)
				for video_id in video_ids:
					vurl=domain+"/ajax/dataEmbed.asp"
					vpage=ump.get_page(vurl,encoding,referer=url,data={"id":video_id},header={"X-Requested-With":"XMLHttpRequest"})
					glink=re.findall('src="(http://sdp.sezonlukdizi.com/.*?)"',vpage)
					uprv=""
					if len(glink)>0:
						videos=re.findall('file:"(.*?)", label:"(.*?)"',ump.get_page(glink[0],encoding,referer=url))
						vlink={}
						for video in videos:
							vlink[video[1]]=video[0]
						uprv="google"
					#oklink=re.findall('<iframe src="(.*?)"',js["part"]["code"])
					#if len(oklink)>0:
					#	oksrc=ump.get_page(oklink[0],encoding,referer=domain)
						#vlink=re.findall("id='\+([0-9]*?)\+'",oksrc)[0]
					#	vlink={}
					#	links=re.findall('file:"(.*?)", label:"(.*?)"',oksrc)
					#	for link in links:
					#		vlink[link[1]]=link[0]
					#	uprv="okru"
					if not uprv=="":
						parts=[{"url_provider_name":uprv, "url_provider_hash":vlink,"referer":domain}]
						ump.add_mirror(parts,"%s %dx%d %s" % (i["tvshowtitle"],i["season"],i["episode"],i["title"]))				
				break

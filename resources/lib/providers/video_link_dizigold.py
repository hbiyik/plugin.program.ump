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
				video_id = re.findall('view_id="([0-9]*?)"',epage)[0]
				data={"id":video_id,"tip":"view"}
				page=ump.get_page(domain+"/sistem/ajax.php",encoding,data=data,referer=domain,header={"X-Requested-With":"XMLHttpRequest"})
				links=re.findall('"file":"(.*?)", "label":"(.*?)"',page.decode("string-escape"))
				##new player 
				vid=re.findall('var view_id="([0-9]*?)"',epage)
				if len(links)>0:
					mirrors={"html5":True}
					for link in links:
						mirrors[link[1].replace("\\","")]=link[0].replace("\\","")
					parts=[{"url_provider_name":"google", "url_provider_hash":mirrors}]
					ump.add_mirror(parts,"%s %dx%d %s" % (i["tvshowtitle"],i["season"],i["episode"],i["title"]))				
					found=True
				elif len(vid)>0:
					data={"tip":"view","id":vid[0]}
					iframe=ump.get_page(domain+"/sistem/ajax.php",encoding,referer=url,header={"X-Requested-With":"XMLHttpRequest"},data=data)
					vkext=re.findall('\?oid=(.*?)"',iframe)
					if len(vkext)>0:
						parts=[{"url_provider_name":"vkext", "url_provider_hash":"https://vk.com/video_ext.php?oid=%s"%vkext[0].replace("\\","")}]
						ump.add_mirror(parts,"%s %dx%d %s" % (i["tvshowtitle"],i["season"],i["episode"],i["title"]))
						found=True
				if not found:
					ump.add_log("dizigold : link is down %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
					return None
				break
	ump.add_log("dizigold can't match %s %dx%d %s"%(i["tvshowtitle"],i["season"],i["episode"],i["title"]))
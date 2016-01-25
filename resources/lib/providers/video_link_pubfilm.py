import re
import time
from third import unidecode
import json
import socket
			
domain="http://movie.pubfilmno1.com"
encoding="utf-8"

def match_results(link,inf):
	prefix=""
	submatch=False
	subpage=ump.get_page(link,encoding,referer=domain)
	imdbid=re.findall('"(http://www.imdb.com/title/tt.*?)"',subpage)
	if len(imdbid)>0:
		imdbid=imdbid[0]
		if imdbid.endswith("/"):
			imdbid=imdbid[:-1]
		imdbid=imdbid.split("/")[-1]
		if imdbid==inf["code"]:
			submatch=True
	else:
		casting=re.findall('<a class="fl ellip _Wqb".*?>(.*?)</a>',subpage)
		infocasting=ump.info["cast"]
		cast_found=0
		for cast in casting:
			for icast in infocasting:
				if ump.is_same(cast,icast):
					cast_found+=1
					continue
		if len(casting)==cast_found or (len(infocasting)==cast_found and len(casting)>len(infocasting)) or (len(casting)==cast_found and len(casting)<len(infocasting)):
			submatch=True
	prefix0=re.findall("itemprop='title'>.*?\((.*?)\)</span>",subpage)
	if len(prefix0)>0:
		prefix=prefix0[0].upper()
		if "HD" == prefix:
			prefix=""
		else:
			prefix="[%s]"%prefix
	return prefix,submatch,subpage
	

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	if not i["code"][:2]=="tt":
		return None
	
	is_serie,names=ump.get_vidnames()
	match=False
	mlink=""
	prefix=""
	if is_serie:
		return None
	kk=0
	try:
		for name in names:
			if match: break
			ump.add_log("pubfilm is searching %s" % name)
			data={"alt":"json-in-script","max-results":9999,"callback":"showResult","q":name}
			page=ump.get_page(domain+"/feeds/posts/summary",encoding,data=data,referer=domain)
			js=re.findall("showResult\((.*?)\);",page)
			if len(js)>0:
				js=json.loads(js[0])
				if "entry" in js["feed"].keys():
					for feed in js["feed"]["entry"]:
						if match: break
						for link in feed["link"]:
							if match: break
							if link["rel"]=="alternate":
								prefix,match,page=match_results(link["href"],i)
								mlink=link["href"]
				else:
					time.sleep(1)
					continue
	except socket.timeout:
		ump.add_log("pubfilm sitesearch is down, trying google")
		for u in ump.web_search("site:movie.pubfilmno1.com \"%s\""%names[0]):
			if match: break
			prefix,match,page=match_results(link["href"],i)

	if not match:
		ump.add_log("pubfilm can't match %s"%names[0])
		return None
	else:
		ump.add_log("pubfilm matched %s with imdbid: %s"%(names[0],i["code"]))

	link1=re.findall('src="(http://player.pubfilm.com/.*?)"',page)
	if len(link1)>0:
		page=ump.get_page(link1[0],encoding,referer=mlink)
		link2=re.findall('link:"(.*?)"',page)
		if len(link2)>0:
			page=ump.get_page("http://player.pubfilm.com/smplayer/plugins/gkphp/plugins/gkpluginsphp.php",encoding,data={"link":link2[0]},referer=link1)
			links=json.loads(page)
			mparts={"html5":True}
			if not isinstance(links["link"],list):
				mparts["video"]=links["link"]
			else:
				for link in links["link"]:
					mparts[link["label"]]=link["link"]
			parts=[{"url_provider_name":"google", "url_provider_hash":mparts,"referer":link1}]
			ump.add_mirror(parts,"%s %s"%(prefix,i["title"]))
			ump.add_log("pubfilm decoded google : %s"%names[0])
			

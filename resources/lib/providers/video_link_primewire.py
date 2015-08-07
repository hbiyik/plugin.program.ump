import urllib2
import urllib
import json
import re
import urlparse
from unidecode import unidecode
			
domain="http://www.primewire.ag"
encoding="utf-8"
matches=[]
max_match=3
max_pages=10


def codify(prv,path):
	path=path.replace(" ","")
	if prv in ["movshare","vodlocker","sharesix","novamov","nowvideo","divxstage","sharerepo","videoweed"]:
		return path.split("/")[-1]
	elif prv in ["zalaa"]:
		return path.split("/")[-2]
	else:
		return None

def search_matches(page):
	global matches
#	<div class="index_item index_item_ie"><a href="/watch-188-The-Matrix-online-free" title="Watch The Matrix (1999)"
	results=re.findall('\<div class="index_item index_item_ie"\>\<a href="(.*?)" title="(.*?) \(',page)
	for result in results:
		if ump.is_same(result[1][6:],ump.info["title"]) :
			ump.add_log("Primewire matched %s" % result[1][6:])
			matches.append(result[0])
	return matches


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	exact=False
	if "tvshowtitle" in i.keys() and not i["tvshowtitle"]=="":
		return None
	#section=[1,2]["episode" in i.keys() and not str(i["episode"])=="-1"]
	section=1
	if section == 1:
		title=i["title"]
	else:
		return None
		#dont use primewire for series their search page is messed up
		title=i["tvshowtitle"]
	ump.add_log("Primewire is searching %s" % title)
	query={"search_section":section,"search_keywords":title}
	page=ump.get_page(domain+"/index.php",encoding,query=query)
	matches=search_matches(page)
	if len(matches)<1:	
		ump.add_log("Primewire is searching %s again without accents" % i["title"])
		query={"search_section":section,"search_keywords":unidecode(title)}
		page=ump.get_page(domain+"/index.php",encoding,query=query)
		matches=search_matches(page)

	pages=[]	
	pagination=re.findall("class=current(.*?)\<div",page,re.DOTALL)
	if len(pagination)>0:
		lastpage=re.findall('href="(.*?)"',pagination[0])
		if len(lastpage)>0:
			lastpage=urlparse.parse_qs(lastpage[-1])["page"]
			for k in range(2,int(lastpage[0])+1):
				if len(pages)>max_pages-1:
					break
				else:
					pages.append({"search_section":section,"search_keywords":title,"page":k})

	for npage in pages:
		if len(matches)<=max_match:
			matches=search_matches(ump.get_page(domain+"/index.php",encoding,query=npage))

	if len(matches)==0: 
		ump.add_log("Primewire can't find any links for %s"%i["title"])
		return None
	
	for match in matches:
		src=ump.get_page(domain+match,encoding)
		imdb=re.findall('imdb\.com/title/(.*?)"',src)
		year=re.findall('\<title\>.*?\((.*?)\).*?</title>',src)
		#either match imid or year for name
		if len(imdb)>0  and "code" in i.keys() and i["code"]==imdb[0]:
			exact=True
			ump.add_log("Primewire found exact match with imdbid %s for %s" %(i["code"],i["title"]))
		elif len(year)>0 and "year" in i.keys() and str(i["year"])==year[0]:
			exact=True
			ump.add_log("Primewire found exact match with in %s for %s" %(str(i["year"]),i["title"]))
		externals=re.findall('class=quality_(.*?)\>.*?href="(/external.php.*?)"',src,re.DOTALL)
		for external in externals:
			page=ump.get_page(domain+"/external.php?"+external[1],encoding)
			#<frame src="http://www.promptfile.com/l/1857EA2CD0-46AE6395D4"/>
			link=re.findall('frame src="(http.*?)"',page)
			if len(link)>0:
				uri = urlparse.urlparse(link[0])
				mname="%s [%s] [%s]" % (["?",""][exact],external[0].upper(),i["title"])
				prv=uri.hostname.split(".")[-2]
				hash=codify(prv,uri.path)
				if hash is None: 
					continue
				ump.add_log("Primewire decoded %s %s" % (mname,prv))
				parts=[{"url_provider_name":prv, "url_provider_hash":hash}]
				ump.add_mirror(parts,mname)
		if exact:
			break
	
	if len(matches)<1:ump.add_log("Primewire cant find any match from %d results"%len(results))
	return None
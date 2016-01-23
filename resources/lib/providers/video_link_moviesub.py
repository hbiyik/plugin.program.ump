import re
import string
import time
from third import unidecode
import json
			
domain="http://www.moviesub.net"
encoding="utf-8"

def decode_link(prv,link):
	page=ump.get_page(link,encoding,referer=domain)
	if prv=="google":
		hash=re.findall('Htplugins_Make_Player\("(.*?)"',page)
		if len(hash)>0:
			links=json.loads(ump.get_page("%s/Htplugins/Loader.php"%domain,encoding,data={"data":hash[0]}))
			if len(links["l"])>0:
				vlinks={"html5":True}
				for i in range(len(links["l"])):
					vlinks[links["q"][i]]=links["l"][i]
				parts=[{"url_provider_name":"google", "url_provider_hash":vlinks,"referer":link}]
				return parts
	elif prv=="videomega":
		hash=re.findall('iframe\.php\?ref\=(.*?)"',page)
		if len(hash)>0:
			return [{"url_provider_name":prv,"url_provider_hash":hash[0],"referer":link}]
	elif prv=="vid":
		hash=re.findall('vid\.ag/(.*?)"',page)
		if len(hash)>0:
			return [{"url_provider_name":prv,"url_provider_hash":hash[0],"referer":link}]
	elif prv=="vodlocker":
		hash=re.findall('vodlocker\.com/embed\-(.*?)\-',page)
		if len(hash)>0:
			return [{"url_provider_name":prv,"url_provider_hash":hash[0],"referer":link}]

def filtertext(text,space=True,rep=""):
	str=string.punctuation
	if space:
		str+=" "
	for c in str:
		text=text.replace(c,rep)
	return text.lower()

def match_results(page,names):
	match_name,match_cast,subpage=False,False,""
	results=re.findall('data-rel=".*?" href="(http://www.moviesub.net/watch/.*?)" title="(.*?)">(.*?)</div',page,re.DOTALL)
	for result in results:
		if match_cast:
			break
		link,title,rest=result
		if "mark-8" in rest:
			camrip="[CAM]"
		else:
			camrip=""
		for name in names:
			if ump.is_same(title,name):
				match_name=True
				break
		if match_name:
			subpage=ump.get_page(link,encoding)
			casting=re.findall('href="actor/.*?">(.*?)</a>',subpage)
			infocasting=ump.info["cast"]
			cast_found=0
			for cast in casting:
				for icast in infocasting:
					if ump.is_same(cast,icast):
						cast_found+=1
						continue
			if len(casting)==cast_found or (len(infocasting)==cast_found and len(casting)>len(infocasting)):
				match_cast=True
	return camrip,match_name,match_cast,subpage

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	if not i["code"][:2]=="tt":
		return None
	
	is_serie,names=ump.get_vidnames()

	if is_serie:
		return None


	ump.add_log("moviesub is searching %s" % filtertext(names[0],False," "))
	page=ump.get_page(domain+"/search/%s.html"%unidecode.unidecode(names[0]),encoding)
	camrip,match_name,match_cast,page=match_results(page,names)
#	if not match_cast:
#		paginations=re.findall('<a href="(.*?unutulmazfilmler.co/arama\.php.*?)">[0-9]*?</a>',page)
#		for pagination in paginations:
#			match_name,match_cast,link=match_results(ump.get_page(pagination,encoding),names)
#			if match_cast:
#				break

	if not match_cast:
		ump.add_log("moviesub can't match %s"%names[0])
		return None
	links={}
	trs=re.findall('<tr>(.*?)</tr>',page)
	for tr in trs:
		lname=re.findall('size="2">Server\s(.*?)\:',tr)[0].lower()
		if lname=="vid.ag":
			lname="vid"
		slinks=re.findall('href="(http://www.moviesub.net/watch/.*?)"',tr)
		links[lname]=slinks
	if not len(links)>0:
		ump.add_log("moviesub can't find any links for %s"%names[0])
		return None

	for prv,links in links.iteritems():
		for link in links:
			parts=decode_link(prv,link)
			if not parts is None:
				ump.add_log("moviesub decoded: %s"%prv)
				ump.add_mirror(parts,"%s%s" % (camrip,names[0]))
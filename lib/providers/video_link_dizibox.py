# -*- coding: utf-8 -*-
import time
import re
import json
from urllib2 import HTTPError
from xml.dom import minidom
import urlparse

encoding="utf-8"
domain = 'http://www.dizibox.com'

def scrape_page(page,etype):
	parts=[]
	enc=re.findall('iframe src="(https?\://play\.dizibox\.net/.*?)"',page)
	if len(enc):
		try:
			url=urlparse.parse_qs(urlparse.urlparse(enc[0]).query)["v"][0].decode("base-64")
		except:
			url=enc[0]
		
	else:
		url=re.findall("<span class=\"object-wrapper\"><iframe.*?src=(?:'|\")(.*?)(?:'|\")",page)[0]

	mparts=url.split("|")
	prefix="[HS:TR]"
	if "alty" in etype.lower():
		prefix=""
	if "ingilizce" in etype.lower():
		prefix="[HS:EN]"
	for mpart in mparts:
		u=urlparse.urlparse(mpart)
		if "ok.ru" in mpart:
			parts.append({"url_provider_name":"okru","url_provider_hash":mpart.split("/")[-1],"referer":url})
		elif "vid.me" in mpart:
			parts.append({"url_provider_name":"vidme","url_provider_hash":mpart.split("/")[-1],"referer":url})
		elif "picasaweb.google.com" in mpart:
			parts.append({"url_provider_name":"picasa","url_provider_hash":mpart,"referer":url})
		elif "vimeo.com" in mpart:
			parts.append({"url_provider_name":"vimeo","url_provider_hash":mpart.split("/")[-1],"referer":url})
		elif "dizibox.net/vk/" in mpart:
			args=urlparse.parse_qs(u.query)
			hash="http://vk.com/video_ext.php?oid=%s&id=%s&hash=%s"%(args.get("oid",[""])[0],args.get("id",[""])[0],args.get("hash",[""])[0])
			parts.append({"url_provider_name":"vkext","url_provider_hash":hash,"referer":url})
		elif "openload.co" in mpart:
			parts.append({"url_provider_name":"openload","url_provider_hash":u.path.split("/")[2],"referer":url})
		elif "mail.ru" in mpart:
			#continue
			parts.append({"url_provider_name":"mailru","url_provider_hash":u.path[1:],"referer":url})
		elif "alphavid" in u.netloc:
			hash=urlparse.parse_qs(u.query)["id"][0]			
			parts=[{"url_provider_name":"alphavid","url_provider_hash":hash}]
		elif "veterok" in u.netloc:
			parts=[{"url_provider_name":"veterok","url_provider_hash":u.path.split("/")[2]}]
		elif "cloudy.ec" in u.netloc:
			hash=urlparse.parse_qs(u.query)["id"][0]			
			parts=[{"url_provider_name":"cloudy","url_provider_hash":hash}]
		else:
			ump.add_log("dizibox can't scrape %s"%mpart)

	return prefix,parts

def scrape_epi(page,elink):
	etitle=re.findall("<mark class='original-title'>(.*?)</mark>",page)
	if not len(etitle):
		return True
	etype=re.findall("selected='selected'>(.*?)</option>",page)[0]
	ops=re.findall("value='(.*?)'>(.*?)</option>",page)
	try:
		prefix,parts=scrape_page(page,etype.lower())
	except:
		ump.add_log("dizibox can't scrape %s"%elink)
	if len(parts):	ump.add_mirror(parts,"%s %s %dx%d %s" % (prefix,i["tvshowtitle"],i["season"],i["episode"],etitle[0]))				

	for op in ops:
		elink,etype=op
		prefix,parts=scrape_page(ump.get_page(elink,encoding,referer=elink),etype.lower())
		try:
			pass
			#prefix,parts=scrape_page(ump.get_page(elink,encoding,referer=elink),etype.lower())
		except:
			ump.add_log("dizibox can't scrape %s"%elink)
			continue
		if len(parts): ump.add_mirror(parts,"%s %s %dx%d %s" % (prefix,i["tvshowtitle"],i["season"],i["episode"],etitle[0]))				


def run(ump):
	globals()['ump'] = ump
	i=ump.info
	globals()['i'] = i
	is_serie,names=ump.get_vidnames()
	found=False
	if not is_serie:
		return None
	for name in names:
		if found: break
		ump.add_log("dizibox is searching %s"%name)
		page=ump.get_page(domain,encoding,query={"s":name})
		series=re.findall('<h3 class="title"><a href="(.*?)"(.*?)\<\/a\>\<\/h3\>',page)
		#check if it is auto redirected first
		if not len(series):
			snames=re.findall('<h1 class="title"><a href="(.*?)">(.*?)</a></h1>',page)
			for snamet in snames:
				sname,slink=snamet
				if ump.is_same(sname,name):
					found=True
					scrape_epi(page,slink)
		#then check if it is a results page
		for serie in series:
			if found:break
			slink,sname=serie
			if ump.is_same(sname,name): 
				found=True
			else:
				continue
			salias=slink.split("/")[-2]
			page=ump.get_page(slink,encoding,referer=domain)
			if not int(i["season"]==1):
				sseasons=re.findall("<a href='(.*?)' class='season\-button.*?>([0-9]*?)\.",page)
				for sseason in sseasons:
					slink,snum=sseason
					if int(i["season"])==int(snum):
						page=ump.get_page(slink,encoding,referer=domain)
						break
			seps=re.findall('class="season-episode">([0-9]*?)\.Sezon.?([0-9]*?)\..*?<a href="(.*?)"',page)
			for sep in seps:
				sseason,sepisode,elink=sep
				if int(i["episode"])==int(sepisode):
					ump.add_log("dizibox matched %s %dx%d %s"%(name,i["season"],i["episode"],i["title"]))
					page=ump.get_page(elink,encoding,referer=slink)
					scrape_epi(page,elink)
					break
			if not int(i["episode"])==int(sepisode):
				slink="%s/%s-%d-sezon-%d-bolum-izle/"%(domain,salias,int(i["season"]),int(i["episode"]))
				page=ump.get_page(slink,encoding,referer=slink)
				if scrape_epi(page,slink):
					slink="%s/%s-%d-sezon-%d-bolum-sezon-finali-izle/"%(domain,salias,int(i["season"]),int(i["episode"]))
					page=ump.get_page(slink,encoding,referer=slink)
					scrape_epi(page,slink)
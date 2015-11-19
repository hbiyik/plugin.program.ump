from urllib2 import HTTPError
import json
import re
import time
import urlparse
			
domain="http://www.animeram.me"
encoding=None

slower=0
def codify(name, prv, url):
	if prv in ["videoweed", "novamov"]:
		return re.findall("embed\.php\?v\=(.+?)&", url)[0],None
	elif prv in ["auengine"]:
		purl=urlparse.urlparse(url)
		return urlparse.parse_qs(purl.query).get("file",[""])[0],None
	elif prv in ["mp4upload", "videonest"]:
		return re.findall("embed-(.+?)\.html", url)[0],None
	elif prv in ["acercloud"]:
		return url,"http://animebam.com"
	elif prv in ["yourupload"]:
		return re.findall("yourupload.com/embed/(.+)", url)[0].split("&")[0],url
	return url,None

def add_mirror(i, name, url):
	URL_TO_PROVIDER = {
			"auengine." : 'auengine',
			"mp4upload.com": 'mp4upload',
			"videonest.net": 'videonest',
			"animebam.com": 'acercloud',
			"yourupload.": 'yourupload',
			"videoweed.": 'videoweed',
			"novamov.com": 'novamov',
	}

	provider = None

	for provider_url, provider_name in URL_TO_PROVIDER.iteritems():
		if provider_url in url:
			provider = provider_name
			break
	
	if not provider:
		ump.add_log("animeram found unrecognized source : %s" % url)
		return
	
	uphash,upref=codify(name, provider, url)
	parts=[{"url_provider_name":provider, "url_provider_hash":uphash,"referer":upref}]
	# TODO: Mirror nameing
	ump.add_mirror(parts, name)

def match_uri(results,refnames):
	for result in results:
		
		page=ump.get_page(result,encoding)
		info_table = re.findall('<table\sclass=\"sheet\">(.+?)</table>', page, re.DOTALL)[0]
		info = re.findall("<td\sclass=\"header\"><label>(.+?)</label></td>\s<td\sclass=\"content1\">(.+?)</td>", page, re.DOTALL)
		for info_title, info_value in info:
			if "Title:" in info_title:
				orgname=info_value
				break

		for info_title, info_value in info:
			if "Alternative Title:" in info_title:
				names = [orgname]
				if info_value is not "-":
					#TODO: implement after such found.
					raise

		for name in refnames:
			for name1 in names:
				if ump.is_same(name1,name,strict=True):
					ump.add_log("animeram found %s"%name)
					return result
	return False

def searchsite(names):
	for name in names:
		ump.add_log("animeram is searching %s on %s"%(name,"sitesearch"))
		try:
			
			data={"cmd_wpa_wgt_anm_sch_sbm": "Search", "txt_wpa_wgt_anm_sch_nme": name}
			sres=ump.get_page(domain+"/anime-list/search/",encoding,data=data)
			sres=re.findall("<div\sclass=\"popular\sfull\">\s<table.+?>(.+?)</table>", sres, re.DOTALL)

			results = []
			for res in sres:
				results.append(re.findall("<h3><a\shref=\"(%s/.+?)/\">(.+?)</a></h3>" % domain, res, re.DOTALL)[0][0])
		except ValueError,timeout:
			continue

		found=match_uri(results,names)
		if found:
			return found
	return False

def sitelist(names):
	ump.add_log("animeram is searching %s on %s"%(names[0],"sitelist"))
	
	sitenames=ump.get_page(domain+"/anime-list-all",encoding)
	sitenames = re.findall("<a\shref=\"%s/([-\w\s\d]+?)/\".+?rel=\"(\d+)\".+?>(.+?)</a>" % domain, sitenames, re.DOTALL)
	for name in names:
		for sitename in sitenames:
			if ump.is_same(sitename[2],name,strict=True):
				ump.add_log("animeram found %s"%name)
				return domain+"/"+sitename[0]
	return False

def google(names):
	ump.add_log("animeram is searching %s on %s"%(names[0],"google"))
	urls=ump.web_search('site:%s %s "Alternative Title:"'%(domain, names[0]))
	if not urls is None:
		return match_uri(urls,names)

def run(ump):
	globals()['ump'] = ump
	i=ump.info

	#lock this provider with ann for the time being. This fucntion will be handled on api later on
	if not i["code"][:5]=="!ann!":
		return None

	is_serie,names=ump.get_vidnames()

	urls=[]	
	found = (searchsite(names) or sitelist(names) or google(names))
	if not found:
		ump.add_log("animeram can't find %s"%names[0])
		return None

	if is_serie:
		epinum=i["absolute_number"]
	else:
		epinum=1
	

	base_url = "%s/%d" % (found, epinum)
	epipage=ump.get_page(base_url, encoding)
	if "Sorry, the page your are trying to view cannot be found or it may have been removed" in epipage:
		if is_serie:
			epipage=ump.get_page(found+"/%d"%i["episode"],encoding)
			if "Sorry, the page your are trying to view cannot be found or it may have been removed" in epipage:
				ump.add_log("animeram can't find episode %d of %s"%(epinum,name))
				return None

	source_list = re.findall("<ul class=\"video.+?\".+?>(.+?)</ul>", epipage, re.DOTALL)[1]
	source_list = re.findall("<a href=\"%s/(\d+)/\">(.+?)</a>" % base_url, source_list, re.DOTALL)
	source_list = [(res[1], "%s/%s" % (base_url, res[0])) for res in source_list]

	links = 0
	for name, url in source_list:
		if "[dubbed]" in name.lower():
			prfx="[D:EN]"
		else:
			prfx="[HS:JP]"
		try:
			watch_page = ump.get_page(url, encoding)
			link=re.findall("<iframe.+?src=\"(.+?)\"", watch_page, re.DOTALL)[0]
			add_mirror(i, prfx+i["title"], link)
			links += 1
		except HTTPError, e:
			continue

	if not links:
			ump.add_log("animeram can't find any links for %s"%i["title"])
	return None

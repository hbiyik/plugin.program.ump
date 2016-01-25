import re
import string
			
domain="http://www.unutulmazfilmler.co"
encoding="utf-8"

def filtertext(text,space=True,rep=""):
	str=string.punctuation
	if space:
		str+=" "
	for c in str:
		text=text.replace(c,rep)
	return text.lower()

def match_results(page,names):
	match_name,match_cast,link=False,False,""
	results=re.findall('<div class="leftflmbg_right_name"><a href="(.*?)">(.*?)</a></div>.*?<div class="leftflmbg_right_content_l">Oyuncular</div>.*?<div class="leftflmbg_right_content_r">(.*?)</div>',page,re.DOTALL)
	for result in results:
		if match_cast:
			break
		link,alt,casting=result
		alt=filtertext(alt).encode("ascii","ignore")
		for name in names:
			if filtertext(name).encode("ascii","ignore") in alt:
				match_name=True
				break
		if match_name:
			casting=re.split(",",casting)
			infocasting=ump.info["cast"]
			cast_found=0
			for cast in casting:
				for icast in infocasting:
					if ump.is_same(cast,icast):
						cast_found+=1
						continue
			if len(casting)==cast_found or (len(infocasting)==cast_found and len(casting)>len(infocasting)):
				match_cast=True
	return match_name,match_cast,link

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	if not i["code"][:2]=="tt":
		return None
	
	is_serie,names=ump.get_vidnames()

	if is_serie:
		return None
	pages=[]

	ump.add_log("UnutulmazFilmler is searching %s" % names[0])
	query={"arama":filtertext(names[0],False," ")}
	page=ump.get_page(domain+"/arama.php",encoding,query=query)
	match_name,match_cast,link=match_results(page,names)
	if not match_cast:
		paginations=re.findall('<a href="(.*?unutulmazfilmler.co/arama\.php.*?)">[0-9]*?</a>',page)
		for pagination in paginations:
			match_name,match_cast,link=match_results(ump.get_page(pagination,encoding),names)
			if match_cast:
				break

	if not match_cast:
		ump.add_log("UntulmazFilmler can't match %s"%names[0])
		return None
	page=ump.get_page(link,encoding)
	params=re.findall('webscripti\("(.*?)", "(.*?)", "(.*?)"\)\;',page)
	if not len(params)>0:
		ump.add_log("UntulmazFilmler can't find any links for %s"%names[0])
		return None
	vid,kaynak,kisim=params[0]
	boot=ump.get_page(domain+"/playerayar.php",encoding,data={"vid":vid,"kisim":kisim,"kaynak":kaynak},referer=domain)
	googles=re.findall('href=".*?sgplus\.html"',boot)
	if not len(googles) > 0 :
		#mailru and ok.ru videos are down only for gvideos
		ump.add_log("UntulmazFilmler can't find any links for %s"%names[0])
		return None
	mails=re.findall('href=".*?smailru\.html"',boot)
	parts={"gplus":googles,"mailru":mails}
	for ptype,parts in parts.iteritems():
		k=0
		plinks=[]
		for part in parts:
			k+=1
			src=ump.get_page(domain+"/playerayar.php",encoding,data={"vid":vid,"kisim":k,"kaynak":ptype},referer=domain)
			if ptype=="gplus":
				plinks.extend(re.findall('src="(http://unutulmazfilmler.co/player/.*?)"',src))
		umpparts=[]
		if ptype=="gplus":
			for plink in plinks:
				umpparts.append({"url_provider_name":"google", "url_provider_hash":plink,"referer":domain})
			if len(umpparts)>0:
				ump.add_mirror(umpparts,"[HS:TR]%s" % names[0])	
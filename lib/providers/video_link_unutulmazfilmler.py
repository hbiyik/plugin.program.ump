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

def match_results(page,names,info):
	match_name,match_year,link=False,False,""
	results=re.findall('<div class="leftflmbg_right_name"><a href="(.*?)">(.*?)</a></div>.*?<div class="leftflmbg_right_content_r">([0-9]{4})',page,re.DOTALL)
	for result in results:
		if match_year:
			break
		link,alt,year=result
		alt=filtertext(alt).encode("ascii","ignore")
		for name in names:
			if filtertext(name).encode("ascii","ignore") in alt:
				match_name=True
				break
		if match_name:
			match_year=info["year"]==int(year)
	return match_name,match_year,link

def run(ump):
	globals()['ump'] = ump
	i=ump.info

	is_serie,names=ump.get_vidnames()

	if is_serie:
		return None
	pages=[]
	
	for name in names:
		ump.add_log("UnutulmazFilmler is searching %s" % name)
		query={"arama":filtertext(name,False," ")}
		page=ump.get_page(domain+"/arama.php",encoding,query=query)
		match_name,match_year,link=match_results(page,names,i)
		if match_year:
			break
		else:
			paginations=re.findall('<a href="(.*?unutulmazfilmler.co/arama\.php.*?)">[0-9]*?</a>',page)
			for pagination in paginations:
				match_name,match_year,link=match_results(ump.get_page(pagination,encoding),names,i)
				if match_name:
					break

	if not match_year:
		ump.add_log("UntulmazFilmler can't match %s"%name)
		return None
	page=ump.get_page(link,encoding)
	params=re.findall('webscripti\("(.*?)", "(.*?)", "(.*?)"\)\;',page)
	if not len(params)>0:
		ump.add_log("UntulmazFilmler can't find any links for %s"%name)
		return None
	vid,kaynak,kisim=params[0]
	boot=ump.get_page(domain+"/playerayar.php",encoding,data={"vid":vid,"kisim":kisim,"kaynak":kaynak},referer=domain)
	googles=re.findall('href=".*?sgplus\.html"',boot)
	if not len(googles) > 0 :
		#mailru and ok.ru videos are down only for gvideos
		ump.add_log("UntulmazFilmler can't find any links for %s"%name)
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
				ump.add_mirror(umpparts,"[HS:TR]%s" % name)	
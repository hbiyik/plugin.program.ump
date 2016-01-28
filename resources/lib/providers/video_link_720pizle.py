import json
import re
import time
			
domain="http://720pizle.com"
encoding="iso-8859-9"


def crawl_movie_page(src,url,name):
	movie_function=re.findall("script>(.*)\(\'(.*)\',",src)
	res=re.findall('class="a oval">(.*?)<',src)
	name=re.findall('<h1>(.*?)<',src)
	if len(name)>0: name= name[0]
	if len(res)>0:
		res=res[0]
	else:
		res="HD"
	if len(movie_function) > 0:
		(prv,hash)=movie_function[0]
		if prv == "vidag":
			prv="vid"
		return prv,hash,res,name
	else:
		#try plusplayer
		hash=re.findall("class=\"plusplayer\".*?>(.*)</div",src)
		if len(hash) > 0:
			return "plusplayer",hash[0],res,name
		else:
			hash=re.findall("(http\://webteizle.org/player/vk\.asp.*?)\"",src)
			if len(hash) > 0:
				return "vkplayer",hash[0],res,name
			else:
				ump.add_log("720pizle Movie page has different encryption: %s" % str(url))
				return None,None,None,None

def return_links(name,type,upname,uphash,res,referer):
	if not upname is None:
		dub=["","[D:TR]"][type=="dub"]
		sub=["","[HS:TR]"][type=="sub"]
		mname="%s%s%s" % (dub,sub,name)
		#ump.add_log("720pizle decoded %s %s" % (mname,movie_link[0][0]))
		parts=[{"url_provider_name":upname, "url_provider_hash":uphash,"referer":referer}]
		ump.add_mirror(parts,mname)

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	is_serie,names=ump.get_vidnames()
	match=False
	for name in names:
		if match:break
		ump.add_log("720pizle is searching %s" % name)
		results=json.loads(ump.get_page(domain+"/api/autocompletesearch.asp",encoding,query={"limit":"10","q":name}))
		if len(results)==0 or len(results)==1 and "orgfilmadi" in results[0].keys() and "Bulunamad" in results[0]["orgfilmadi"] : 
			ump.add_log("720pizle can't find any links for %s"%name)
			continue
		imdbmatch=False

		for result in results:
			if ump.is_same(result["imdbid"],i["code"]):
				ump.add_log("720pizle matched %s with imdb:%s" % (i["title"],result["imdbid"]))
				match=result["url"]
				break
			elif ump.is_same(result["orgfilmadi"],name) and ump.is_same(result["yil"],i["year"]):
				ump.add_log("720pizle matched %s in %s" % (name,result["yil"]))
				match=result["url"]
				break
		time.sleep(1)

	if not match:
		ump.add_log("720pizle cant find any match from %d results"%len(results))
		return None

	src=ump.get_page(domain+match,encoding)
	movie_pages=re.findall('href="(/izle/.*?)" title=""',src)
	count=len(movie_pages)
	for movie_page in movie_pages:
		movie_page_type=["dub","sub"][movie_page.split("/")[2]=="altyazi"]
		src=ump.get_page(domain+movie_page,encoding)
		prv,hash,res,name2=crawl_movie_page(src,movie_page,name)
		return_links(name2,movie_page_type,prv,hash,res,domain+movie_page)
		alts=[]
		urls = re.findall('href="(/izle/.*?)" rel="nofollow"(.*?)</a>',src)
		alts=[x[0] for x in urls if not "tlb_isik" in x[1] ]
		count+=len(alts)
		ump.add_log("720pizle found %d mirrors for Turkish %s %s" % (len(alts),movie_page_type,name2))
		for alt in alts:
			src=ump.get_page(domain+alt,encoding)
			#ump.add_log("720pizle is crawling %s" % alt)
			prv,hash,res,name2=crawl_movie_page(src,alt,name)
			return_links(name2,movie_page_type,prv,hash,res,domain+alt)
	ump.add_log("720pizle finished crawling %d mirrors"%count)
	return None
	
	
	return None
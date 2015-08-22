import json
import re
			
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
		return movie_function,res,name
	else:
		#try plusplayer
		hash=re.findall("class=\"plusplayer\".*>(.*)<",src)
		if len(hash) > 0:
			return [("plusplayer",hash[0])],res,name
		else:
			hash=re.findall("(http\://webteizle.org/player/vk\.asp.*?)\"",src)
			if len(hash) > 0:
				return [("vkplayer",hash[0])],res,name
			else:
				ump.add_log("720pizle Movie page has different encryption: %s" % str(url))
				return [],None,None

def return_links(name,type,movie_link,res):
	if len(movie_link)> 0:
		dub=["","[D:TR]"][type=="dub"]
		sub=["","[HS:TR]"][type=="sub"]
		mname="%s%s%s" % (dub,sub,name)
		#ump.add_log("720pizle decoded %s %s" % (mname,movie_link[0][0]))
		parts=[{"url_provider_name":movie_link[0][0], "url_provider_hash":movie_link[0][1]}]
		ump.add_mirror(parts,mname)

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	if "tvshowtitle" in i.keys() and not i["tvshowtitle"]=="":
		return None
	ump.add_log("720pizle is searching %s" % i["title"])
	results=json.loads(ump.get_page(domain+"/api/autocompletesearch.asp",encoding,query={"limit":"10","q":i["title"]}))
	if len(results)==0 or len(results)==1 and "orgfilmadi" in results[0].keys() and "Bulunamad" in results[0]["orgfilmadi"] : 
		ump.add_log("720pizle can't find any links for %s"%i["title"])
		return None
	matches=[]
	max_match=3
	imdbmatch=False

	for result in results:
		if i["code"].startswith("tt") and result["imdbid"]==i["code"]:
			ump.add_log("720pizle matched %s with %s" % (i["title"],i["code"]))
			matches=[result["url"]]
			imdbmatch=True
			break

	for result in results:
		if not imdbmatch and len(matches)<=max_match and ump.is_same(result["orgfilmadi"],i["title"]):
			ump.add_log("720pizle matched %s" % i["title"])
			matches.append(result["url"])

	for match in matches:
		src=ump.get_page(domain+match,encoding)
		movie_pages=re.findall('href="(/izle/.*?)" title=""',src)
		count=len(movie_pages)
		for movie_page in movie_pages:
			movie_page_type=["dub","sub"][movie_page.split("/")[2]=="altyazi"]
			src=ump.get_page(domain+movie_page,encoding)
			movie_link,res,name2=crawl_movie_page(src,movie_page,i["title"])
			return_links(name2,movie_page_type,movie_link,res)
			alts=[]
			urls = re.findall('href="(/izle/.*?)" rel="nofollow"(.*?)</a>',src)
			alts=[x[0] for x in urls if not "tlb_isik" in x[1] ]
			count+=len(alts)
			ump.add_log("720pizle found %d mirrors for Turkish %s %s" % (len(alts),movie_page_type,name2))
			for alt in alts:
				src=ump.get_page(domain+alt,encoding)
				#ump.add_log("720pizle is crawling %s" % alt)
				movie_link,res,name2=crawl_movie_page(src,alt,i["title"])
				return_links(name2,movie_page_type,movie_link,res)
		ump.add_log("720pizle finished crawling %d mirrors"%count)
		return None
	
	if len(matches)<1:ump.add_log("720pizle cant find any match from %d results"%len(results))
	return None
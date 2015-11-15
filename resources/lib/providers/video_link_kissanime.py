from urllib2 import HTTPError
import json
import re
import time
			
domain="http://kissanime.to"
encoding="utf-8"

def match_uri(results,refnames):
	matched=False
	pages={}
	for result in results:
		if matched: break
		depth=result.replace("%s/Anime/"%domain,"").split("/")
		if len(depth)>1:
			continue
		page=ump.get_page(result,encoding)
		orgname=re.findall('<a Class="bigChar".*?>(.*?)</a>',page)
		orgname=orgname[0].split("(")[0]
		names=[orgname]
		namesdiv=re.findall('class="info">Other name\:</span>(.*?)\n',page)
		
		for div in namesdiv:
			names.extend(re.findall('">(.*?)</a>',div))

		for name in refnames:
			if matched: break
			for name1 in names:
				if ump.is_same(name1,name,strict=False):
					related=re.findall('subdub.png.*<a href="(.*?)"><b>(.*?)</b></a>',page)
					if len(related)>0:
						if "(Sub)" in related[0][1]:
							pages["[HS:EN]"]=ump.get_page("%s%s"%(domain,related[0][0]),encoding)
							pages["[D:EN]"]=page
						elif "(Dub)" in related[0][1]:
							pages["[D:EN]"]=ump.get_page("%s%s"%(domain,related[0][0]),encoding)
							pages["[HS:EN]"]=page
					else:
						pages["[HS:EN]"]=page
					ump.add_log("kissanime found %s %s"%(name,"".join(pages.keys())))
					matched=True
					break
	return matched,pages

def run(ump):
	globals()['ump'] = ump
	i=ump.info

	#lock this provider with ann for the time being. This fucntion will be handled on api later on
	if not i["code"][:5]=="!ann!":
		return None

	is_serie="tvshowtitle" in i.keys() and not i["tvshowtitle"].replace(" ","") == ""
	if is_serie:
		orgname=i["tvshowtitle"]
		altnames=i["tvshowalias"].split("|")
	else:
		orgname=i["title"]
		altnames=i["originaltitle"].split("|")
	
	for k in range(len(altnames)):
		if altnames[k]=="":
			altnames.pop(k)

	urls=[]	
	names=[orgname]
	names.extend(altnames)
	jq_limit=False
	found=False
	ump.get_page(domain,encoding)
	for name in names:
		ump.add_log("kissanime is searching %s on %s"%(name,"sitesearch"))
		u="%s/AdvanceSearch"%domain
		f={"animeName":name,"genres":0,"status":""}
		page=ump.get_page(u,encoding,data=f)
		urls=re.findall('class="bigChar" href="(.*?)"',page)
		found,res=match_uri([domain+url for url in urls],names)	
		if found:break
	
	if not found:
		ump.add_log("kissanime is searching %s on %s"%(names[0],"google"))
		urls=ump.web_search('site:%s/Anime/* %s "Genres:"'%(domain,names[0]))
		if not urls is None:
			found,res=match_uri(urls,names)

	if not found and not jq_limit:
		ump.add_log("kissanime is searching %s on %s"%(names[0],"swift"))
		urls=[]
		ekey="orVAutnpwh1yygQ3eGzz"
		q={"engine_key":ekey,"q":names[0]}
		res=ump.get_page("http://api.swiftype.com/api/v1/public/engines/search",encoding,query=q)
		res=json.loads(res)
		pages=res["records"]["page"]
		if "/Message/" in pages[0]["url"]:
			ump.add_log("Kissanime exceeded swift search limit")
			jq_limit=True
		else:
			for page in pages:
				urls.append(page["url"])
			found,res=match_uri(urls,names)
		
	if not found:
		ump.add_log("Kissanime can't find %s"%names[0])
		return None
	else:
		found=False
		for dub,page in sorted(res.iteritems(),reverse=True):
			table=re.findall('<table class="listing">(.*?)</table>',page,re.DOTALL)
			if len(table)<1:
				continue
			epis=re.findall('href="(/Anime/.*?)"',table[0])
			epinames=re.findall('title="Watch anime (.*?)">',table[0])
			for epi,epiname in zip(epis,epinames):
				if is_serie:
					epinum=re.findall("([0-9]*?) online",epiname)
					if not len(epinum)==1 or epinum[0]=="" or not int(epinum[0])==int(i["absolute_number"]):
						continue
				ump.add_log("kissanime is  loading %s"%i["title"])
				epipage=ump.get_page(domain+epi,encoding)
				fansub=re.findall("\[(.*?)\]",epiname)
				if len(fansub)==1:
					prefix="%s[FS:%s]"%(dub,fansub[0])
				else:
					prefix=dub
				links=re.findall('<select id="selectQuality">(.*?)\n',epipage)
				for link in links:
					qualities=re.findall('value="(.*?)"',link)
					for quality in qualities:
						url=quality.decode("base-64")
						if "googlevideo.com" in url or "blogspot.com" in url:
							found=True
							parts=[{"url_provider_name":"google", "url_provider_hash":{"html5":True,"url":url}}]
							ump.add_mirror(parts,"%s %s"%(prefix,i["title"]))
		if not found:
			ump.add_log("kissanime can't find any links for %s"%i["title"])

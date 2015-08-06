import urllib2
import urllib
import json
import re
import time
import urlparse
from unidecode import unidecode
			
domain="http://kissanime.com"
encoding="utf-8"

def dec(s):
	try:
		offset=1 if s[0]=='+' else 0
		return int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
	except:
		return

def get_page(*args,**kwargs):
	try:
		page=ump.get_page(*args,**kwargs)
	except urllib2.HTTPError, err:
		if err.code == 503:
			body=err.read()
			try:
				challenge = re.search(r'name="jschl_vc" value="(\w+)"', body).group(1)
				challenge_pass = re.search(r'name="pass" value="(.+?)"', body).group(1)
				builder = re.search(r"setTimeout\(function\(\){\s+(var t,r,a,f.+?\r?\n[\s\S]+?a\.value =.+?)\r?\n", body).group(1)
				builder = re.sub(r"a\.value =(.+?) \+ .+?;", r"\1", builder)
				builder = re.sub(r"\s{3,}[a-z](?: = |\.).+", "", builder)
			except Exception as e:
				raise
			js = re.sub(r"[\n\\']", "", builder)
			d,k,m=re.findall(',\s(.*?)={"(.*?)":(.*?)}',builder)[0]
			ops=re.findall(d+"\."+k+"(.)\=(.*?)\;",builder)
			res=dec(m)
			for op in ops:
				res=eval("res"+op[0]+"dec('"+op[1]+"')")
			answer = str(res + len("kissanime.com"))
			waittime=4
			ump.add_log("Kissanime has been stalled for %d seconds due to cloudfare protection"%waittime)
			time.sleep(waittime)
			kwargs["referer"]=args[0]
			args=list(args)
			args[0]="%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&pass=%s&jschl_answer=%s"%(domain,challenge,challenge_pass,answer)
			page=ump.get_page(*args,**kwargs)
		else:
			page=err.read()
	return page

def match_uri(results,refnames):
	matched=False
	pages={}
	for result in results:
		if matched: break
		depth=result.replace("http://kissanime.com/Anime/","").split("/")
		if len(depth)>1:
			continue
		page=get_page(result,encoding)
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
					related=re.findall('subdub.png"/>.*<a href="(.*?)"><b>(.*?)</b></a>',page)
					if len(related)>0:
						if "(Sub)" in related[0][1]:
							pages["[HS:EN]"]=get_page("%s%s"%(domain,related[0][0]),encoding)
							pages["[D:EN]"]=page
						elif "(Dub)" in related[0][1]:
							pages["[D:EN]"]=get_page("%s%s"%(domain,related[0][0]),encoding)
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
	gg_limit=False
	found=False
	get_page(domain,encoding)
	for name in names:
		ump.add_log("kissanime is searching %s on %s"%(name,"sitesearch"))
		u="%s/AdvanceSearch"%domain
		f={"animeName":name,"genres":0,"status":""}
		page=get_page(u,encoding,data=f)
		urls=re.findall('class="bigChar" href="(.*?)"',page)
		found,res=match_uri([domain+url for url in urls],names)	
		if found:break
	
	if not found and not gg_limit:
		ump.add_log("kissanime is searching %s on %s"%(names[0],"google"))
		urls=[]
		query={"v":"1.0","q":'site:https://kissanime.com/Anime/* %s "Genres:"'%names[0]}
		j=json.loads(ump.get_page("http://ajax.googleapis.com/ajax/services/search/web",encoding,query=query))
		status=j.get("responseStatus",0)
		if not status==200:
			ump.add_log("Kissanime exceeded google search limit")
			gg_limit=True
		elif not found:
			results=j["responseData"]["results"]
			for result in results:
				urls.append(result["unescapedUrl"])
			found,res=match_uri(urls,names)

	if not found and not jq_limit:
		ump.add_log("kissanime is searching %s on %s"%(names[0],"swift"))
		urls=[]
		ekey="orVAutnpwh1yygQ3eGzz"
		q={"engine_key":ekey,"q":names[0]}
		res=get_page("http://api.swiftype.com/api/v1/public/engines/search",encoding,query=q)
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
			epis=re.findall('<a href="(/Anime/.*?)" title="Watch anime (.*?)">',page)
			for epi in epis:
				if is_serie:
					epinum=re.findall("([0-9]*?) online",epi[1])
					if not len(epinum)==1 or epinum[0]=="" or not int(epinum[0])==int(i["absolute_number"]):
						continue
				ump.add_log("kissanime is  loading %s"%i["title"])
				epipage=get_page(domain+epi[0],encoding)
				fansub=re.findall("\[(.*?)\]",epi[1])
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
							parts=[{"url_provider_name":"google", "url_provider_hash":json.dumps({"html5":True,"url":url})}]
							ump.add_mirror(parts,"%s %s"%(prefix,i["title"]))
		if not found:
			ump.add_log("kissanime can't find any links for %s"%i["title"])

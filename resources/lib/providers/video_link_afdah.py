import re
import urlparse
import string
			
domain="http://afdah.tv"
encoding="utf-8"
matches=[]
max_match=3
max_pages=10

def codify(prv,path,query=""):
	path=path.replace(" ","")
	if prv in ["movshare","vodlocker","sharesix","novamov","nowvideo","divxstage","sharerepo","videoweed","thefile","stagevu","vidxden","filenuke","vidbull","ishared"]:
		hash=path.split("/")[-1]
		if hash not in ["embed.php"]:
			return hash
	if prv in ["zalaa","uploadc","mightyupload"]:
		return path.split("/")[-2]

	if prv in ["movshare"]:
		return query.split("=")[1].replace("&","")
	
	return None

def match_results(results,names):
	exact,page,result=False,None,None
	for result in results:
		page=ump.get_page(domain+result,encoding)
		imdb=re.findall('"http://www.imdb.com/title/(tt.*?)/?"',page)
		title=re.findall('Title: </font>(.*?)<br>',page)
		year=re.findall('<title>.*?\(([0-9]*?)\)',page)
		director=re.findall('Director: (.*?)<br>',page,re.DOTALL)
		if len(director)>0:
			director[0]=re.sub(r'<.*?>','', director[0])
		if len(imdb)>0  and "code" in ump.info.keys() and ump.info["code"]==imdb[0]:
			exact=True
			ump.add_log("afdah found exact matched imdbid %s" %(ump.info["code"]))
		elif len(imdb)==0 and len(title)>0 and len(year)>0 and len(director)>0 and year[0]==ump.info["year"] and ump.is_same(director[0],ump.info["director"]):
			for name in names:
				if ump.is_same(name,title[0]):
					exact=True
					ump.add_log("afdah found exact match with %s/%s/%s" %(name,ump.info["director"],ump.info["year"]))
					break
		if exact:
			break

	return exact,page,result

#func borrowed from salts
def caesar(plaintext, shift):
	lower = string.ascii_lowercase
	lower_trans = lower[shift:] + lower[:shift]
	alphabet = lower + lower.upper()
	shifted = lower_trans + lower_trans.upper()
	return str(plaintext).translate(string.maketrans(alphabet, shifted)).encode(encoding)

def run(ump):
	globals()['ump'] = ump
	i=ump.info
	exact=False
	is_serie,names=ump.get_vidnames()
	if not i["code"][:2]=="tt" or is_serie:
		return None

	for name in names:
		if exact:
			break
		ump.add_log("afdah is searching %s" % name)
		query={"search":name,"type":"title"}
		page1=ump.get_page(domain+"/wp-content/themes/afdah/ajax-search.php",encoding,data=query,referer=domain)
		results=re.findall('href="(.*?)"',page1)
		exact,page,result=match_results(results,names)

	if not exact:
		ump.add_log("afdah can't match %s"%names[0])
		return None
	mirrors=re.findall('href="(.*?)" target="_blank">',page,re.DOTALL)
	embeds=re.findall('href="(http://afdah.tv/embed.*?)" target\="new">',page,re.DOTALL)


	if "This movie is of poor quality" in page:
		mname="[TS]%s" % i["title"]
	else:
		mname=i["title"]

	for embed in embeds:
		src=ump.get_page(embed,encoding)
		encoded=re.findall('write\("(.*?)"\)\;',src)
		if len(encoded)<1:
			continue
		plaintext = caesar(encoded[0], 13).decode('base-64')
		if 'http' not in plaintext:
			plaintext = caesar(encoded[0].decode('base-64'), 13).decode('base-64')
		iframe=re.findall("\<iframe.*?src='(.*?)'",plaintext)
		glinks=re.findall('file: "(.*?)", label: "(.*?)" }',plaintext)
		videomega=re.findall("http://videomega.tv/validatehash.php\?hashkey\=([0-9]*?)'",plaintext)

		if len(videomega)>0:
			urls={"referer":domain,"key":videomega[0]}
			prv="videomega"
			ump.add_log("afdah decoded %s %s" % (mname,prv))
			parts=[{"url_provider_name":prv, "url_provider_hash":urls}]
			ump.add_mirror(parts,mname)


		elif len(glinks)>0:
			urls={"html5":True}
			for glink in glinks:
				if not glink[0][-6:] == "sd.mp4":
					urls[glink[1]]=glink[0]
			if len(urls.keys())>1:
				prv="google"
				ump.add_log("afdah decoded %s %s" % (mname,prv))
				parts=[{"url_provider_name":prv, "url_provider_hash":urls}]
				ump.add_mirror(parts,mname)

			
		elif len(iframe)>0:
			uri = urlparse.urlparse(iframe[0])
			prv=uri.hostname.split(".")[-2]
			hash=codify(prv,uri.path,uri.query)
			if hash is None: 
				continue
			ump.add_log("afdah decoded %s %s" % (mname,prv))
			parts=[{"url_provider_name":prv, "url_provider_hash":hash}]
			ump.add_mirror(parts,mname)

	for mirror in mirrors:
		uri = urlparse.urlparse(mirror)
		prv=uri.hostname.split(".")[-2]
		hash=codify(prv,uri.path)
		if hash is None: 
			continue
		ump.add_log("afdah decoded %s %s" % (mname,prv))
		parts=[{"url_provider_name":prv, "url_provider_hash":hash}]
		ump.add_mirror(parts,mname)
	ump.add_log("afdah finished crawling %d mirrors"%(len(mirrors)+len(embeds)))
	return None
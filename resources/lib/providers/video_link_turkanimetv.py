import re
from unidecode import unidecode
			
domain="http://www.turkanime.tv/"
encoding="utf-8"


def return_links(name,mp,h,fs):
	parts=[{"url_provider_name":mp, "url_provider_hash":h}]
	prefix=""
	if not fs == "Varsayilan":
		prefix="[FS:%s]"%fs
	name="%s[HS:TR]%s" % (prefix,name)
	ump.add_mirror(parts,name)

def scrape_moviepage(url,fansub,name):
	pg=ump.get_page(domain+url,encoding)
	videos=re.findall("'#video','(.*?)','#video'.*?icon-play\"></i>(.*?)</a>",pg)
	for video in videos:
		up=unidecode(video[1].replace(" ","").lower())
		u=video[0]
		try:
			if up=="mail": 
				up="mailru"
				continue
				#skip mailru this provider is messed up
			elif up=="myvi":
				uphash=re.findall("embed/html/(.*?)\"",ump.get_page(domain+u,encoding))[0]
			elif up=="odnoklassniki": 
				up="okru"
				uphash=re.findall("/videoembed/(.*?)\"",ump.get_page(domain+u,encoding))[0]
			elif up=="sibnet":
				continue
				#skip this provider it uses m3u8.
				uphash=re.findall("videoid\=([0-9]*?)\"",ump.get_page(domain+u,encoding))[0]
			elif up in ["cloudy","videohut","videoraj"]:
				uphash=re.findall("\?id\=(.*?)\"",ump.get_page(domain+u,encoding))[0]
			elif up == "vk":
				up="vkext"
				hash=re.findall("\?vid\=(.*?)\"",ump.get_page(domain+u,encoding))[0]
				oid,video_id,embed_hash=hash.split("_")
				uphash="http://vk.com/video_ext.php?oid="+oid+"&id="+video_id+"&hash="+embed_hash
			elif up == "turkanime":
				hash=re.findall("(http\://www.schneizel.net/video/index.php\?vid\=.*?)\"",ump.get_page(domain+u,encoding))[0]
				uphash={"url":hash,"referer":"http://www.turkanime.tv/bolum/shingeki-no-kyojin-25-bolum-final&fansub=PeaceFansub&giris=OK&video=690863"}
				up="google"
			elif up == "dailymotion":
				#todo prepare a decoder
				uphash=re.findall("/video/(.*?)\"",ump.get_page(domain+u,encoding))[0]
			elif up == "kiwi":
				uphash=re.findall("v2/(.*?)\"",ump.get_page(domain+u,encoding))[0]
			elif up == "meta":
				#todo this provider is messed up
				continue
				#todo prepare a decoder
				uphash=re.findall("iframe/(.*?)/",ump.get_page(domain+u,encoding))[0]
			else:
				print "Unknown URL Provider: %s"%up
				continue
		except IndexError:
			print "Turkanimetv changed regex for : %s, skipping"%up
			continue
		return_links(name,up,uphash,fansub)	
		
def run(ump):
	globals()['ump'] = ump
	i=ump.info
	names=[i["tvshowtitle"]]
	if "tvshowalias" in i.keys():
		names.extend(i["tvshowalias"].split("|"))
	if "title" in i.keys() and not i["title"]=="":
		names.append(i["title"])
	is_movie=False
	url=None
	animes=re.findall('<a href="(.*?)" class="btn".*?title="(.*?)">',ump.get_page(domain+"/icerik/tamliste",encoding))
	for name in names:
		ump.add_log("turkanimetv is searching %s" % name)
		for anime in animes:
			if ump.is_same(anime[1],name):
				url=anime[0]
				break
		if not url is None:
			break

	if url is None:	
		ump.add_log("turkanimetv can't find any links for %s"%name)
		return None
	
	url=re.findall('"(icerik/bolumler.*?)"',ump.get_page(domain+url,encoding))[0]

	if not is_movie:
		bolumler=re.findall('<a href="(.*?)" class="btn".*?title=".*?([0-9]*?)\..*?">',ump.get_page(domain+url,encoding))
		url=None
		for bolum in bolumler:
			try:
				bid=int(bolum[1])
			except:
				continue
			if bid == i["absolute_number"]:
				ump.add_log("turkanimetv matched episode %dx%d:%s" % (i["season"],i["episode"],bid))
				url=bolum[0]
				break
	else:
		url=re.findall('<a href="(.*?)" class="btn"',ump.get_page(domain+url,encoding))
		if len(url)==1:
			url=url[0]
			ump.add_log("turkanimetv matched %s" % unidecode(anime[1]))
		else:
			url=None

	if url is None:	
		ump.add_log("turkanimetv can't find any links for %s"%name)
		return None

	fansubs=re.findall("'#video','(.*?)fansub=(.*?)&giris=OK','#video'",ump.get_page(domain+url,encoding))
	for fansub in fansubs:
		f=fansub[1]
		u=fansub[0]+"fansub="+fansub[1]+"&giris=OK"
		scrape_moviepage(u,f,name)
	if len(fansubs)==0:
		scrape_moviepage(url,"Varsayilan",name)
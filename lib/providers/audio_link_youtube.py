# -*- coding: utf-8 -*-
import json
import re
import urlparse


domain="http://www.youtube.com/"
encoding="utf-8"
tunnel=["cookie"]

def run(ump):
	globals()['ump'] = ump
	parts=[]
	ids=[]
	tracks=[]
	old_artist=""
	old_artalbum=""
	old_tralbum=""
	if "playlist" in ump.args:
		playlist=ump.args["playlist"]
		mname=ump.args.get("mname","Grooveshark Playlist")
	else:
		playlist=[{"info":ump.info,"art":ump.art}]
		mname="%s - %s" %(ump.info["artist"],ump.info["title"])
	for item in playlist:
		match=False
		i=item["info"]
		page=ump.get_page(domain+"results",encoding,query={"search_query":"%s - %s"%(i["artist"],i["title"])})
		ump.add_log("youtube is searching track: %s - %s"%(i["artist"],i["title"]))
		for res in re.findall('<h3 class="yt-lockup-title "><a href="(.*?)".*?title="(.*?)"',page):
			link,title=res
			title=title.split("-")
			if not len(title)==2:continue
			artist,title=title
			hash=urlparse.parse_qs(urlparse.urlparse(link).query).get("v",[None])[0]
			if not hash or hash in ids: continue
			ids.append(hash)
			if ump.is_same(artist,i["artist"]) and ump.is_same(title,i["title"]):
				ump.add_log("youtube found track: %s - %s"%(i["artist"],i["title"]))
				part={"url_provider_name":"youtube", "url_provider_hash":hash,"referer":domain,"partname":"%s - %s" %(artist,title),"info":i}
				if "playlist" in ump.args:
					parts.append(part)
					break
				else:
					ump.add_mirror([part],mname,wait=0.2,missing="ignore")
	if len(parts):
		if len(parts)==1:
			ump.add_mirror(parts,mname)
		elif len(parts)>1:
			ump.add_mirror(parts,"%s [TRACKS:%d]"%(mname,len(parts)),wait=0.2,missing="ignore")
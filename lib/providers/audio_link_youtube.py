# -*- coding: utf-8 -*-
import json
import re
import urlparse


domain="http://www.youtube.com/"
encoding="utf-8"
tunnel=["cookie"]
timetol=3

def run(ump):
	globals()['ump'] = ump
	parts=[]
	ids=[]
	tracks=[]
	old_artist=""
	old_artalbum=""
	old_tralbum=""
	if ump.defs.MT_ALBUM==ump.info["mediatype"]:
		playlist=ump.args["playlist"]
		mname=ump.args.get("mname","Grooveshark Playlist")
	else:
		playlist=[{"info":ump.info,"art":ump.art}]
		mname="%s - %s" %(ump.info["artist"],ump.info["title"])
	for item in playlist:
		i=item["info"]
		page=ump.get_page(domain+"results",encoding,query={"search_query":"%s - %s"%(i["artist"],i["title"])})
		ump.add_log("youtube is searching track: %s - %s"%(i["artist"],i["title"]))
		for res in re.findall('<h3 class="yt-lockup-title "><a href="(.*?)".*?title="(.*?)".*?</a><span class="accessible-description".*?>(.*?)</span></h3>',page):
			link,title,times=res
			times=re.findall("([0-9]*?)\:([0-9]*?)\.",times)
			try:
				idur=int(i.get("duration",0))
				dur=int(times[0][0])*60+int(times[0][1])
			except:
				idur=0
				dur=0
			title=title.split("-")
			if not len(title)==2:continue
			artist,title=title
			hash=urlparse.parse_qs(urlparse.urlparse(link).query).get("v",[None])[0]
			if not hash or hash in ids: continue
			ids.append(hash)
			if dur>0 and idur>0:
				match=artist.strip() in i["artist"].strip() or i["artist"].strip() in artist.strip()
				match=match and (title.strip() in i["title"].strip() or i["title"].strip() in title.strip())
				match=match and abs(dur-idur)<=timetol
			else:
				match=ump.is_same(artist,i["artist"]) and ump.is_same(title,i["title"]) 
			if match:
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
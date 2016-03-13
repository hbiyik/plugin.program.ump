# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import re
import urlparse
			
domain="http://musicmp3.ru"
encoding="utf-8"
		
def run(ump):
	globals()['ump'] = ump
	i=ump.info
	ump.add_log("musicmp3 is searching %s"%i["artist"])
	page=ump.get_page(domain+"/search.html",encoding,query={"text":i["artist"]})
	parts=[]
	ump.add_log("redmp3 is searching track: %s - %s"%(i["artist"],i["title"]))
	artists=re.findall('<a class="artist_preview__title" href="(.*?)">(.*?)</a>',page)
	for artist in artists:
		if ump.is_same(artist[1],i["artist"]):
			ump.add_log("musicmp3 matched Artist: %s"%artist[1])
			page=ump.get_page(domain+artist[0],encoding)
			albums=re.findall('<a class="album_report__link" href="(.*?)".*?class="album_report__name">(.*?)</span>',page)
			for album in albums:
				if ump.is_same(album[1],i["album"]) or i["album"]=="":			
					ump.add_log("musicmp3 matched Artist: %s, Album : %s"%(artist[1],album[1]))
					page=ump.get_page(domain+album[0],encoding)
					tracks=re.findall('<tr class="song" id="(.*?)".*?rel="(.*?)".*?<span itemprop="name">(.*?)</span>',page)
					for track in tracks:
						trackid,rel,tn=track
						if i["title"]=="":
							if not i["album"]=="":
								mname="%s : %d Tracks"%(i["album"],len(parts)+1)
							else:
								mname="%s : %d Tracks"%(i["artist"],len(parts)+1)
							parts.append({"url_provider_name":"musicmp3", "url_provider_hash":rel,"partname":artist[1]+" - "+tn,"referer":trackid})
						elif ump.is_same(i["title"],tn):
							mname=("%s - %s"%(i["artist"],i["title"]))
							parts.append({"url_provider_name":"musicmp3", "url_provider_hash":rel,"partname":artist[1]+" - "+tn,"referer":trackid})
							ump.add_log("musicmp3 matched Artist: %s, Track : %s"%(artist[1],tn))
							print track
	if len(parts):
		ump.add_mirror(parts,mname)
	else:
		ump.add_log("musicmp3 can't find any tracks")
import json
import xbmc
import re
import uuid,md5

anime_providers=["ann"]
#mtypes:0 movie,1 series, 2 anime movies, 3 anime series
def sync(ump,upname,uphash,url,q,w,h,hs="",fs="",d="",f=0):
	indexer=ump.module
	if indexer in anime_providers:
		is_serie,names=ump.get_vidnames(org_first=False)
		is_serie=int(is_serie)+2
	else:
		is_serie,names=ump.get_vidnames(org_first=True)
		is_serie=int(is_serie)

	if is_serie in [1,3]:
		epiname=ump.info["title"]
		referer="%s %sx%s %s"%(names[0],str(ump.info["season"]),str(ump.info["episode"]),epiname)
	else:
		epiname=""
		referer="%s (%s)"%(names[0],str(ump.info["year"]))

	data={
		"ctype":ump.content_type,
		"mtype":is_serie,
		"season":ump.info["season"],
		"episode":ump.info["episode"],
		"name":names[0],
		"epiname":epiname,
		"director":ump.info["director"],
		"casting":json.dumps(ump.info["cast"]),
		"plot":ump.info["plot"],
		"votes":ump.info["votes"],
		"rating":ump.info["rating"],
		"year":ump.info["year"],
		"aired":ump.info["aired"],
		"fanart":ump.art["fanart"],
		"poster":ump.art["poster"],
		"eposter":ump.art["thumb"],
		"indexer":indexer,
		"quality":q,
		"width":w,
		"height":h,
		"urlprovider":upname,
		"urlhash":uphash,
		"url":url,
		"hs":hs,
		"fs":fs,
		"d":d,
		"f":f
		}
	
	ua="%s%s"%(re.sub("\(.*?\)","",xbmc.getInfoLabel( "System.FriendlyName	" )),xbmc.getInfoLabel( "System.BuildVersion" ))
	ua=ua.replace("  "," ")
	print ua
	m=md5.new()
	m.update(str(uuid.getnode()))
	print m.hexdigest()
#	ump.tm.add_queue(target=ump.get_page, args=("http://ump.6te.net/ump/sync.php",None,None,data,None,None,False,None,{"User-Agent":"UMP"}))
	print ump.get_page("http://ump.6te.net/ump/sync.php","utf-8",None,data,None,None,False,referer,{"User-Agent":ua})
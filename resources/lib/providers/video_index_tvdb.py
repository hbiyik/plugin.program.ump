import xbmc
import xbmcgui
import xbmcplugin
from datetime import date
from urllib import quote_plus
from urllib import urlencode
import time
import re
import json
from xml.dom import minidom
import random
import urlparse

mirror="http://thetvdb.com"
try:
	language=xbmc.getLanguage(xbmc.ISO_639_1).lower()
except AttributeError:
	#backwards compatability
	language="en"
if not language in ["en","sv","no","da","fi","nl","de","it","es","fr","pl","hu","el","tr","ru","he","ja","pt","zh","cs","sl","hr","ko"]:
	language="en"
encoding="utf-8"
apikey="C738A0A57D46E2CC"
recnum=50

def str_int(x):
	return int(float(x))

def str_trim(x):
	return x.split(" (")[0]

def get_child_data(p,c,defval,func=None):
	i=p.getElementsByTagName(c)
	if len(i)==1 and not i[0] is None and not i[0].lastChild is None:
		if func is None:
			return i[0].lastChild.data
		else:
			return func(i[0].lastChild.data)
	else:
		return defval

def get_tvdb_art(ids):
	def get_id(id):
		p=ump.get_page("%s/api/%s/series/%s/banners.xml"%(mirror,apikey,str(id)),None)
		x=minidom.parseString(p)
		banners=x.getElementsByTagName("Banner")
		result[id]={
		"banner_series_text":{"local":[],"global":[],"rest":[]},
		"banner_series_graphical":{"local":[],"global":[],"rest":[]},
		"banner_series_blank":{"local":[],"global":[],"rest":[]},
		"poster_season":{"local":{},"global":{},"rest":{}},
		"banner_season":{"local":{},"global":{},"rest":{}},
		"poster":{"local":[],"global":[],"rest":[]},
		"fanart":{"local":[],"global":[],"rest":[]},
		}
		for banner in banners:
			bpath=banner.getElementsByTagName("BannerPath")
			btype1=banner.getElementsByTagName("BannerType")
			btype2=banner.getElementsByTagName("BannerType2")
			lng=banner.getElementsByTagName("Language")

			key="rest"
			if len(lng)>0 and not lng[0].lastChild is None:
				if lng[0].lastChild.data == language:
					key="local"
				elif lng[0].lastChild.data == "en":
					key="global"

			if len(bpath)==1 and len(btype1)==1 and btype1[0].lastChild.data=="poster":
				result[id]["poster"][key].append(bpath[0].lastChild.data)
			if len(bpath)==1 and len(btype1)==1 and btype1[0].lastChild.data=="fanart":
				result[id]["fanart"][key].append(bpath[0].lastChild.data)
			if len(bpath)==1 and len(btype1)==1 and btype1[0].lastChild.data=="season":
				for ref,db in [("season","poster_season"),("seasonwide","banner_season")]:
					if len(btype2[0].lastChild.data) and btype2[0].lastChild.data==ref:
						s=int(banner.getElementsByTagName("Season")[0].lastChild.data)
						if s:
							if s in result[id][db][key].keys() and isinstance(result[id][db][key][s],list):
								result[id][db][key][s].append(bpath[0].lastChild.data)
							else:
								result[id][db][key][s]=[bpath[0].lastChild.data]
			
			if len(bpath)==1 and len(btype1)==1 and btype1[0].lastChild.data=="series":
				for ref,db in [("text","banner_series_text"),("graphical","banner_series_graphical"),("blank","banner_series_blank")]:
					if len(btype2[0].lastChild.data) and btype2[0].lastChild.data==ref:
						result[id][db][key].append(bpath[0].lastChild.data)

	result={}

	gid=ump.tm.create_gid()
	for id in ids:
		ump.tm.add_queue(get_id,(id,),gid=gid)
	
	ump.tm.join(gid=gid)
	return result

def get_tvdb_info(ids,force_lang=False):
	if not force_lang:
		force_lang=language

	def get_id(id,lng):
		p=ump.get_page("%s/api/%s/series/%s/%s.xml"%(mirror,apikey,str(id),lng),None)
		x=minidom.parseString(p)
		serie=x.getElementsByTagName("Series")[0]
		info={}
		art={}
		infolabels={
			"ContentRating":("mpaa","",None),
			"FirstAired":("aired","",None),
			"IMDB_ID":("code","",None),
			"id":("code2","",None),
			"zap2it_id":("code10","",None),
			"Network":("studio","",None),
			"Overview":("plotoutline","",None),
			"Overview":("plot","",None),
			"Rating":("rating","",float),
			"RatingCount":("votes","",str_int),
			"SeriesName":("localtitle",None,str_trim),
			"added":("dateadded","",None),
			}

		artlabels={
			"banner":("banner","",None),
			"fanart":("fanart","",None),
			"poster":("poster","",None),
			"thumb":("poster","",None),
			}

		for i in infolabels.keys():
			info[infolabels[i][0]]=get_child_data(serie,i,infolabels[i][1],infolabels[i][2])
		
		if info["localtitle"] is None:info.pop("localtitle")
		if len(info["aired"])>4: info["year"]=int(info["aired"][:4])
		for a in artlabels.keys():
			art[a]="%s/banners/%s"%(mirror,get_child_data(serie,artlabels[a][0],artlabels[a][1],artlabels[a][2]))
		
		actors=get_child_data(serie,"Actors","")
		actors=[x for x in actors.split("|") if not x==""]
		info["cast"]=actors

		genre=get_child_data(serie,"Genre","")
		genre=genre.replace("|"," ")
		info["genre"]=genre
		info["code2"]=id
		
		result[id]={"info":info,"art":art}

	result={}

	gid=ump.tm.create_gid()
	for id in ids:
		ump.tm.add_queue(get_id,(id,force_lang),gid=gid)
	
	ump.tm.join(gid=gid)
	return result

def get_tvdb_episodes(ids,arts):
	def get_id(id):
		p=ump.get_page("%s/api/%s/series/%s/all/%s.xml"%(mirror,apikey,str(id),language),None)
		x=minidom.parseString(p)
		seasons=x.getElementsByTagName("Combined_season")
		seasons=set([x1.lastChild.data for x1 in seasons])
		epis={}
		for s in seasons:
			epis[int(s)]={"info":{"title":"Season %s"%(str(s),)},"art":make_art(arts,int(s)),"episode":{}}
		episodes=x.getElementsByTagName("Episode")
		infolabels={
			"Combined_episodenumber":("episode",-1,str_int),
			"Combined_season":("season",-1,str_int),
			"Director":("director","",None),
			"EpImgFlag":("EpImgFlag",-1,str_int),
			"EpisodeName":("title","",None),
			"EpisodeNumber":("EpisodeNumber",-1,str_int),
			"FirstAired":("aired","",None),
			"GuestStars":("GuestStars","",None),
			"Language":("Language","",None),
			"Overview":("plot","",None),
			"Rating":("rating","",float),
			"RatingCount":("votes","",str_int),
			"SeasonNumber":("SeasonNumber","",str_int),
			"Writer":("writer","",None),
			"lastupdated":("dateadded","",None),
			"absolute_number":("absolute_number",-1,str_int),
			}
		artlabels={
			"filename":("thumb","",None),
			}
		for e in episodes:
			epiinfo=ump.info.copy()
			for i in infolabels.keys():
				epiinfo[infolabels[i][0]]=get_child_data(e,i,infolabels[i][1],infolabels[i][2])
			epiart=make_art(arts,-1)
			for a in artlabels.keys():
				epiart[artlabels[a][0]]="%s/banners/%s"%(mirror,get_child_data(e,a,artlabels[a][1],artlabels[a][2]))
			epiart["poster"]=epiart["thumb"]
			season=epiinfo["season"]
			episode=epiinfo["episode"]
			epis[season]["episode"][episode]={"info":epiinfo,"art":epiart}
		result[id]=epis
	result={}
	gid=ump.tm.create_gid()
	for k in range(len(ids)):
		ump.tm.add_queue(get_id,(ids[k],),gid=gid)
	
	ump.tm.join(gid=gid)
	return result	


def make_art(art,season=-1,banner_tables=["text","graphical","blank"]):
	def selectrandom(typ):
		selected="DefaultFolder.png"
		for lng in ["local","global","rest"]:
			if season==-1 or typ=="fanart":
				if not typ == "banner":
					if len(art[typ][lng]):
						selected=random.choice(art[typ][lng])
						break
				else:
					if selected=="DefaultFolder.png":
						for banner_table in banner_tables:
							if len(art["banner_series_"+banner_table][lng]):
								selected=random.choice(art["banner_series_"+banner_table][lng])
								break
			else:
				if typ=="poster":typ="poster_season"
				if typ=="banner":typ="banner_season"
				if season in art[typ][lng].keys() and len(art[typ][lng][season]):
					selected=random.choice(art[typ][lng][season])
					break
		return selected

	xart={
		"thumb":"%s/banners/%s"%(mirror,selectrandom("poster")),
		"poster":"%s/banners/%s"%(mirror,selectrandom("poster")),
		"banner":"%s/banners/%s"%(mirror,selectrandom("banner")),
		"fanart":"%s/banners/%s"%(mirror,selectrandom("fanart")),
		"clearart":"",
		"clearlogo":"",
		"landscape":""
		}
	return xart

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("Search", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search",{"search":True}),li,True)


	elif ump.page == "search":
		kb = xbmc.Keyboard('default', 'heading', True)
		kb.setDefault("")
		kb.setHiddenInput(False)
		kb.doModal()
		what=kb.getText()
		q={"seriesname":what,"language":"all"}
		p=ump.get_page("%s/api/GetSeries.php"%mirror,None,query=q)
		x=minidom.parseString(p)
		series=x.getElementsByTagName("Series")
		ump.set_content(ump.defs.CC_TVSHOWS)
		names={}
		suggest=""
		otherids=[]
		for s in series:
			sid=s.getElementsByTagName("seriesid")[0].lastChild.data
			lang=s.getElementsByTagName("language")[0].lastChild.data
			if not lang == "":
				otherids.append(sid)
			if not sid in names.keys():
				names[sid]={}
			sname=s.getElementsByTagName("SeriesName")[0].lastChild.data
			names[sid]["title"]=names[sid]["tvshowtitle"]=names[sid]["localtitle"]=names[sid]["originaltitle"]=sname.split(" (")[0]
			alternates=list(set([x.split(" (")[0] for x in get_child_data(s,"AliasNames","").split("|")]))
			for k in range(len(alternates)):
				if alternates[k]=="": alternates.pop(k)
			if "alternates" in names[sid].keys():
				names[sid]["alternates"].extend(alternates)
			else:
				names[sid]["alternates"]=alternates

		#get english names locally returned values
		if len(otherids):
			other_data=get_tvdb_info(otherids,"en")
			for otherid in otherids:
				if "localtitle" in other_data[otherid]["info"].keys():
					names[otherid]["originaltitle"]=other_data[otherid]["info"]["localtitle"]

		#if there is no result do a google search
		if len(names)==0:
			suggest="[SUGGESTED] "
			sug_ids=[]
			urls=ump.web_search("inurl:thetvdb.com/?tab=series %s"%what)
			if not urls:
				return None
			for u in urls:
				idx=urlparse.parse_qs(urlparse.urlparse(u).query).get("id",None)
				if not idx:
					continue
				sug_ids.append(idx[0])
			sug_data=get_tvdb_info(sug_ids,"en")
			for sug_id in sug_ids:
				names[sug_id]={}
				names[sug_id]["title"]=names[sug_id]["tvshowtitle"]=names[sug_id]["localtitle"]=names[sug_id]["originaltitle"]=sug_data[sug_id]["info"]["localtitle"]
				names[sug_id]["alternates"]=[]


		data=get_tvdb_info(names.keys())

		for id in data.keys():
			names[id].update(data[id]["info"])
			li=xbmcgui.ListItem(suggest+names[id]["localtitle"], iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			ump.info=names[id]
			ump.art=data[id]["art"]
			try:
				li.setArt(ump.art)
			except AttributeError:
				#backwards compatability
				pass
			li.setInfo(ump.content_type,ump.info)
			u=ump.link_to("seasons",{"tvdbid":id})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "seasons":
		ump.set_content(ump.defs.CC_ALBUMS)
		id=ump.args.get("tvdbid",None)
		if not id:
			return None
		arts=get_tvdb_art([id])[id]
		epis=get_tvdb_episodes([id],arts)[id]
		#todo get names in all langs

		for sno in sorted(epis.keys(),reverse=True):
			li=xbmcgui.ListItem("Season %d"%sno, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			ump.art=epis[sno]["art"]
			#ump.info=epis[sno]["info"]
			try:
				li.setArt(ump.art)
			except AttributeError:
				#backwards compatability
				pass
			#li.setInfo(ump.content_type,ump.info)
			u=ump.link_to("episodes",{"tvdbid":id,"season":sno})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
			
	elif ump.page == "episodes":
		#xbmc.executebuiltin("XBMC.Container.Update(plugin://plugin.program.ump/?test=123)")
		ump.set_content(ump.defs.CC_EPISODES)
		id=ump.args.get("tvdbid",None)
		season=ump.args.get("season",None)
		if not id or not season:
			return None
		arts=get_tvdb_art([id])[id]
		epis=get_tvdb_episodes([id],arts)[id][season]
		for epno in sorted([int(x) for  x in epis["episode"].keys()],reverse=True):
			#json keys are strings :(
			li=xbmcgui.ListItem("%dx%d %s"%(season,epno,epis["episode"][epno]["info"]["title"]), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			ump.info=epis["episode"][epno]["info"]
			ump.art=epis["episode"][epno]["art"]
			try:
				li.setArt(ump.art)
			except AttributeError:
				#backwards compatability
				pass
			li.setInfo(ump.content_type,ump.info)
			u=ump.link_to("urlselect")
			xbmcplugin.addDirectoryItem(ump.handle,u,li,False)

	xbmcplugin.endOfDirectory(ump.handle,cacheToDisc=cacheToDisc,updateListing=False,succeeded=True)
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
import dateutil.parser as dparser

mirror="http://thetvdb.com"
language="en"
encoding="utf-8"
apikey="C738A0A57D46E2CC"
recnum=50

def str_int(x):
	return int(float(x))

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
		season={}
		poster=[]
		fanart=[]
		for banner in banners:
			bpath=banner.getElementsByTagName("BannerPath")
			btype1=banner.getElementsByTagName("BannerType")
			btype2=banner.getElementsByTagName("BannerType2")
			if len(bpath)==1 and len(btype1)==1 and btype1[0].lastChild.data=="poster":
				poster.append(bpath[0].lastChild.data)
			if len(bpath)==1 and len(btype1)==1 and btype1[0].lastChild.data=="fanart":
				fanart.append(bpath[0].lastChild.data)
			if len(bpath)==1 and len(btype1)==1 and len(btype2)==1 and btype1[0].lastChild.data=="season" and btype2[0].lastChild.data=="season":
				s=int(banner.getElementsByTagName("Season")[0].lastChild.data)
				if s in season.keys() and isinstance(season[s],list):
					season[s].append(bpath[0].lastChild.data)
				else:
					season[s]=[bpath[0].lastChild.data]
		if len(poster)==0:
			poster=[""]
		if len(fanart)==0:
			fanart=[""]
		result[id]={"poster":poster,"fanart":fanart,"season":season}
		
	result={}

	gid=ump.tm.create_gid()
	for id in ids:
		ump.tm.add_queue(get_id,(id,),gid=gid)
	
	ump.tm.join(gid=gid)
	return result

def get_tvdb_info(ids):
	def get_id(id):
		p=ump.get_page("%s/api/%s/series/%s/%s.xml"%(mirror,apikey,str(id),language),None)
		x=minidom.parseString(p)
		serie=x.getElementsByTagName("Series")[0]
		info={}
		art={}
		infolabels={
			"ContentRating":("mpaa","",None),
			"FirstAired":("aired","",None),
			"IMDB_ID":("code","",None),
			"zap2it_id":("code2","",None),
			"Network":("studio","",None),
			"Overview":("plotoutline","",None),
			"Overview":("plot","",None),
			"Rating":("rating","",float),
			"RatingCount":("votes","",str_int),
			"SeriesName":("tvshowtitle","",None),
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

		for a in artlabels.keys():
			art[a]="%s/banners/%s"%(mirror,get_child_data(serie,artlabels[a][0],artlabels[a][1],artlabels[a][2]))
		
		actors=get_child_data(serie,"Actors","")
		actors=[x for x in actors.split("|") if not x==""]
		info["cast"]=actors

		genre=get_child_data(serie,"Genre","")
		genre=genre.replace("|"," ")
		info["genre"]=genre
		
		result[id]={"info":info,"art":art}

	result={}

	gid=ump.tm.create_gid()
	for id in ids:
		ump.tm.add_queue(get_id,(id,),gid=gid)
	
	ump.tm.join(gid=gid)
	return result

def get_tvdb_episodes(ids,info,arts):
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
			epiinfo=info
			for i in infolabels.keys():
				epiinfo[infolabels[i][0]]=get_child_data(e,i,infolabels[i][1],infolabels[i][2])
			epiart=make_art(arts,epiinfo["season"])
			for a in artlabels.keys():
				epiart[artlabels[a][0]]="%s/banners/%s"%(mirror,get_child_data(e,a,artlabels[a][1],artlabels[a][2]))
			season=epiinfo["season"]
			episode=epiinfo["episode"]
			epis[season]["episode"][episode]={"info":dict(epiinfo),"art":dict(epiart)}
		result[id]=epis

	result={}
	gid=ump.tm.create_gid()
	for id in ids:
		ump.tm.add_queue(get_id,(id,),gid=gid)
	
	ump.tm.join(gid=gid)
	return result	


def make_art(art,season=-1):
	if season==-1:
		poster=random.choice(art["poster"])
	elif season in art["season"].keys():
		poster=random.choice(art["season"][season])
	else:
		poster=""
	xart={
		"thumb":"%s/banners/%s"%(mirror,poster),
		"poster":"",
		"banner":"%s/banners/%s"%(mirror,poster),
		"fanart":"%s/banners/%s"%(mirror,random.choice(art["fanart"])),
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
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search",{"serach":True}),li,True)


	elif ump.page == "search":
		kb = xbmc.Keyboard('default', 'heading', True)
		kb.setDefault("")
		kb.setHiddenInput(False)
		kb.doModal()
		q={"seriesname":kb.getText()}
		p=ump.get_page("%s/api/GetSeries.php"%mirror,None,query=q)
		x=minidom.parseString(p)
		series=x.getElementsByTagName("Series")
		ump.set_content(ump.defs.CC_TVSHOWS)
		names={}

		for s in series:
			sname=s.getElementsByTagName("SeriesName")[0].lastChild.data
			salias=get_child_data(s,"AliasNames","")
			sid=s.getElementsByTagName("seriesid")[0].lastChild.data
			names[sid]=(sname,salias)

		data=get_tvdb_info(names.keys())

		for id in names.keys():
			data[id]["info"]["tvshowalias"]=names[id][1]
			li=xbmcgui.ListItem(names[id][0], iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			li.setArt(data[id]["art"])
			li.setInfo(ump.content_type,data[id]["info"])
			u=ump.link_to("seasons",{"id":id,"info":data[id]["info"],"art":data[id]["art"]})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "seasons":
		ump.set_content(ump.defs.CC_ALBUMS)
		id=ump.args["id"]
		info=ump.args["info"]
		arts=get_tvdb_art([id])[id]
		epis=get_tvdb_episodes([id],info,arts)[id]

		for sno in sorted(epis.keys(),reverse=True):
			li=xbmcgui.ListItem(epis[sno]["info"]["title"], iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			li.setArt(epis[sno]["art"])
			li.setInfo(ump.content_type,epis[sno]["info"])
			u=ump.link_to("episodes",{"id":id,"episodes":epis[sno]["episode"],"season":sno})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
			
	elif ump.page == "episodes":
		ump.set_content(ump.defs.CC_EPISODES)
		epis=ump.args["episodes"]
		season=ump.args["season"]
		for epno in sorted([int(x) for  x in epis.keys()],reverse=True):
			#json keys are strings :(
			epno=str(epno)
			li=xbmcgui.ListItem("%dx%d %s"%(season,epis[epno]["info"]["episode"],epis[epno]["info"]["title"]), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			info=epis[epno]["info"]
			art=epis[epno]["art"]
			li.setArt(art)
			li.setInfo(ump.content_type,info)
			ump.art=art
			ump.info=info
			u=ump.link_to("urlselect",{"info":info,"art":art})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	xbmcplugin.endOfDirectory(ump.handle,cacheToDisc=cacheToDisc)
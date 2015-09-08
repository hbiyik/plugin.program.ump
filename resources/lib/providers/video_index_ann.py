# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcplugin
import datetime
from urllib import quote_plus
from urllib import urlencode
import time
import re
import json
import urlparse
from xml.dom import minidom
import dateutil.parser as dparser
import dateutil
import httplib
from xml.parsers import expat
from unidecode import unidecode

domain="http://www.animenewsnetwork.com"
encoding="utf-8"

def latinise(text):
	# some roman chars are rare on daily usage, and everybody uses latin representatives. Dont know how romaji works in details.
	chars={
		333:"ou", #ō
		215:"x", #instead of × 
		}

	for char in chars.keys():
		text=text.replace(unichr(char),chars[char])
	return text

def scrape_ann_search(animes):
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('ANN', 'Retrieving Information')
	pDialog.update(5, 'Retrieving Information')
	res=ump.get_page(domain+"/encyclopedia/api.xml?anime="+"/".join(animes),None)
	pDialog.update(40, 'Retrieving Information')
	m1=[]
	#no idea why chr 08 causes xml sructure error :/
	res=minidom.parseString(res.replace(chr(8),""))
	medias=res.getElementsByTagName("anime")
	pDialog.update(50, 'Retrieving Information')
	count=0
	for media in medias:
		count+=1
		relnum=0
		img=""
		title=""
		maintitle=""
		alttitle=[]
		originaltitle=""
		tvshowtitle=""
		tvshowalias=""
		outline=""
		gen=""
		year=""
		dates=[]
		votes="0"
		episodes={}
		dir=""
		cast=[]
		mpaa=""
		runtime=""
		rating=float(0)
		id="!ann!"+str(media.getAttribute("id"))
		type=str(media.getAttribute("precision"))
		epinum=0
		num_of_epis=0
		for info in media.getElementsByTagName("info"):
			t=info.getAttribute("type")
			#image
			if t=="Picture":
				img=info.lastChild.getAttribute("src")
			if t=="Main title":
				maintitle=latinise(info.lastChild.data)
			if t=="Alternative title":
				alttitle.append(latinise(info.lastChild.data))
			if t=="Plot Summary":
				outline+=info.lastChild.data
			if t=="Genres" or t=="Themes":
				gen+=info.lastChild.data+"/"
			if t=="Vintage":
				try:
					pdate=dparser.parse(info.lastChild.data,fuzzy=True,default=datetime.datetime(1970, 1, 1, 0, 0))
					dates.append(pdate)
				except:
					pass
			if t=="Premiere date" and type=="movie series":
				epinum+=1
				episodes[epinum]={"title":info.lastChild.data,"relativenumber":epinum}
			
			if t=="Number of episodes":
				num_of_epis=int(info.lastChild.data)

		for episode in media.getElementsByTagName("episode"):
			if not float(episode.getAttribute("num")) == 0:
				relnum+=1
							
			episodes[episode.getAttribute("num")]={"title":episode.lastChild.lastChild.data,"relativenumber":relnum}
		
		##special for ovas, i hate the random stuff with ann
		cur_epis=len(episodes)
		if num_of_epis>cur_epis and num_of_epis>1:
			for k in range(num_of_epis-cur_epis):
				episodes[cur_epis+k+1]={"title":"Episode %d"%(cur_epis+k+1),"relativenumber":cur_epis+k+1}
		
		if len(episodes)>0:
			tvshowtitle=maintitle
			tvshowalias="|".join(alttitle)
		else:
			title=maintitle
			originaltitle="|".join(alttitle)
		
		for rate in media.getElementsByTagName("ratings"):
			rating=float(rate.getAttribute("weighted_score"))
			votes=rate.getAttribute("nb_votes")

		if not gen=="":
			gen=gen[0:-1]
		if len(dates)>0:
			dates.sort
			m= datetime.datetime.now().month
			y= datetime.datetime.now().year
			if dates[0].year > y or dates[0].year == y and dates[0].month > m:
				#print "TOO SOON FOR : " + tvshowtitle.encode("ascii","ignore")
				continue
			year=str(dates[0].year)

	
		data={}
		data["info"]={
			"count":len(episodes.keys()),
			"size":0, 
			#"date":"01-01-1970",
			"genre":gen,
			"year":year,
			"episode":-1,
			"season":-1,
			"top250":-1,
			"tracknumber":-1,
			"rating":rating,
			"playcount":-1,
			"overlay":0,
			"cast":[],
			"castandrole":[],
			"director":"",
			"mpaa":mpaa,
			"plot":outline,
			"plotoutline":outline,
			"title":title,
			"originaltitle":originaltitle,
			"tvshowtitle":tvshowtitle,
			"tvshowalias":tvshowalias,
			"sorttitle":"",
			"duration":runtime,
			"studio":"",
			"tagline":"",
			"write":"",
			"premiered":"",
			"status":"",
			"code":id,
			"aired":"",
			"credits":"",
			"lastplayed":"",
			"album":"",
			"artist":([]),
			"votes":votes,
			"trailer":"",
			"dateadded":"",
			"type":type
			}
		data["art"]={
			"thumb":img,
			"poster":img,
			"banner":"",
			"fanart":"",
			"clearart":"",
			"clearlogo":"",
			"landscape":""
			}
		data["episodes"]=episodes #special only for this indexer
		m1.append(data)
		pDialog.update(50+count, 'Retrieving Information')

	pDialog.close()
	return m1

def grab_searches(link,maxpage=2):
	pages=[]
	pages.append(ump.get_page(link,encoding))
	num=re.findall("pg\=([0-9]*?)\"",pages[0])
	if len(num)<2: 
		return pages
	for i in range(1,int(num[-1])+1):
		link2="%s&pg=%d"%(link,i)
		pages.append(ump.get_page(link2,encoding))
		if i >= maxpage:
			break
	return pages

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("Search", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search"),li,True)

		li=xbmcgui.ListItem("Top Rated Animes", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("select_year"),li,True)

		li=xbmcgui.ListItem("Newest Animes", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("newest"),li,True)

		li=xbmcgui.ListItem("Animes by Genre", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("bygenre"),li,True)

	elif ump.page == "bygenre":
		genres={
			"Adventure":"adventure/A",
			"Comedy":"comedy",
			"Drama":"drama/D",
			"Slice Of Life":"slice%20of%20life/D",
			"Fantasy":"fantasy/F",
			"Magic":"magic/F",
			"Supernatural":"supernatural/F",
			"Horror":"horror",
			"Mystery":"mystery",
			"Psychological":"psychological",
			"Romance":"romance",
			"Science Fiction":"science%20fiction",
			"Thriller":"thriller",
			"Tournament":"tournament",
			"Erotic":"erotica",
			}
			
		for genre in sorted(genres.keys()):
			li=xbmcgui.ListItem(genre, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("selectgenre",{"genre":genres[genre]}),li,True)
	
	elif ump.page == "selectgenre":
		ids=[]
		pages=grab_searches("%s/encyclopedia/search/genreresults?w=series&w=movies&from=&to=&lic=&a=AA&a=OC&a=TA&a=MA&a=AO&g=%s&o=rating"%(domain,ump.args["genre"]))
				
		for page in pages:
			ids.extend(re.findall("anime.php\?id=([0-9]*?)\"(.*?)</a>",page))

		li=xbmcgui.ListItem("Show Both", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":[x[0] for x in ids],"filters":["numvotes"]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("Show only series", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":[x[0] for x in ids if not "(movie)" in x[1]],"filters":["numvotes"]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Show only movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":[x[0] for x in ids if "(movie)" in x[1]],"filters":["numvotes"]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "newest":
		ids=[]
		dates=[]
		months=[]
		pages=grab_searches("%s/encyclopedia/search/genreresults?w=series&w=movies&from=%d&to=%d&lic=&a=AA&a=OC&a=TA&a=MA&a=AO&o=date"%(domain, datetime.datetime.now().year, datetime.datetime.now().year))
		for page in pages:
			ids.extend(re.findall("anime.php\?id=([0-9]*?)\"",page))
			dates.extend(re.findall("class=\"de\-emphasized\">(.*?)<",page))

		for i in range(len(dates)):
			if datetime.datetime.now().month == dparser.parse(dates[i],fuzzy=True,default=datetime.datetime(1970, 1, 1, 0, 0)).month:
				months.append(ids[i])

		li=xbmcgui.ListItem("This Month", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":months,"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("This Year", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":ids,"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
				

	elif ump.page == "select_year":
		ump.args["year"]=""
		li=xbmcgui.ListItem("All Time", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("toprated",ump.args)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		for year in reversed(range(datetime.date.today().year-50,datetime.date.today().year+1)):
			ump.args["year"]=str(year)
			li=xbmcgui.ListItem(str(year), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			u=ump.link_to("toprated",ump.args)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "toprated":
		ids=[]
		pages=grab_searches("%s/encyclopedia/search/genreresults?w=series&w=movies&from=%s&to=%s&lic=&a=AA&a=OC&a=TA&a=MA&o=rating"%(domain,ump.args["year"],ump.args["year"]))
		for page in pages:
			ids.extend(re.findall("anime.php\?id=([0-9]*?)\"(.*?)</a>",page))

		li=xbmcgui.ListItem("Show Both", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":[x[0] for x in ids],"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("Show only series", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":[x[0] for x in ids if not "(movie)" in x[1]],"filters":[],"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Show only movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":[x[0] for x in ids if "(movie)" in x[1]],"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "search":
		kb = xbmc.Keyboard('default', 'Search Anime', True)
		kb.setDefault("")
		kb.setHiddenInput(False)
		kb.doModal()
		what=kb.getText()
		q={"id":155,"type":"anime","search":what}
		res=ump.get_page(domain+"/encyclopedia/reports.xml",None,query=q)
		res=minidom.parseString(res)
		items=res.getElementsByTagName("item")
		ids=[]
		for item in items:
			ids.append(item.getElementsByTagName("id")[0].firstChild.data)

		li=xbmcgui.ListItem("Found %d %s(s) for %s" % (len(items),"anime",what), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":ids,"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
	
	elif ump.page == "results_search":
		filters=ump.args["filters"]
		animes=ump.args["anime"]
		index=ump.args.get("index",0)
		anime=animes[index*50:(index+1)*50]
		medias=scrape_ann_search(anime)

		if len(medias) > 0: 
			if not index==0:
				li=xbmcgui.ListItem("Results %d-%d"%((index-1)*50+1,index*50))
				u=ump.link_to("results_search",{"anime":animes,"filters":filters,"index":index-1})
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
			for media in medias:
				if "numvotes" in filters and int(media["info"]["votes"])<100:
					#print "TOO FEW VOTES FOR : "+ media["info"]["tvshowtitle"].encode("ascii","ignore")
					continue
				if len(media["episodes"].keys())==0:
					li=xbmcgui.ListItem("%s (%s)"%(media["info"]["title"],media["info"]["type"]))
				else:
					li=xbmcgui.ListItem("%s (%s)"%(media["info"]["tvshowtitle"],media["info"]["type"]))
				li.setInfo(ump.defs.CT_VIDEO,media["info"])
				li.setArt(media["art"])
				ump.art=media["art"]
				ump.info=media["info"]
				if len(media["episodes"].keys())==0:
					u=ump.link_to("urlselect")
				else:
					u=ump.link_to("show_episodes",{"annid":media["info"]["code"]})
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
			if not index==len(animes)/50:
				li=xbmcgui.ListItem("Results %d-%d"%((index+1)*50+1,(index+2)*50))
				u=ump.link_to("results_search",{"anime":animes,"filters":filters,"index":index+1})
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		cacheToDisc=True
	
	elif ump.page== "show_episodes":
		annid=ump.args.get("annid",None)
		if not annid or not annid[:5]=="!ann!":
			return None
		medias=scrape_ann_search([annid[5:]])
		if len(medias)<1:
			return None
		episodes=medias[0]["episodes"]
		#keys are parsed as strings
		for k,v in episodes.items():
			episodes.pop(k)
			episodes[int(float(k))]=v
		#below does not work on old versions of python
		#episodes = {float(k):v for k,v in episodes.iteritems()}
		for epi in sorted(episodes.keys(),reverse=True):
			li=xbmcgui.ListItem("%d %s"%(epi,episodes[epi]["title"]))
			li.setArt(ump.art)
			ump.info["title"]=episodes[epi]["title"]
			ump.info["episode"]=episodes[epi]["relativenumber"]
			#even though animes dont have season info force it so trakt will scrobble
			ump.info["season"]=1
			ump.info["absolute_number"]=epi
			u=ump.link_to("urlselect")
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)			

	xbmcplugin.endOfDirectory(ump.handle,	cacheToDisc=cacheToDisc)
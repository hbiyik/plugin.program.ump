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
from third.dateutil import parser
import httplib
from xml.parsers import expat
from third.unidecode import unidecode
import operator

domain="http://www.animenewsnetwork.com"
encoding="utf-8"

try:
	language=xbmc.getLanguage(xbmc.ISO_639_1).lower()
except AttributeError:
	#backwards compatability
	language="en"

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
		titlealias=""
		originaltitle=None
		tvshowtitle=""
		localtitle=None
		alts=[]
		alttitle=[]
		outline=""
		gen=""
		year=1900
		dates=[]
		votes="0"
		episodes={}
		dir=""
		cast=[]
		mpaa=""
		runtime=""
		rating=float(0)
		id=str(media.getAttribute("id"))
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
				alt=latinise(info.lastChild.data)
				alttitle.append((info.getAttribute("lang"),alt))
			if t=="Plot Summary":
				outline+=info.lastChild.data
			if t=="Genres" or t=="Themes":
				gen+=info.lastChild.data+"/"
			if t=="Vintage":
				try:
					pdate=parser.parse(info.lastChild.data.split(" to ")[0],fuzzy=True,default=datetime.datetime(1970, 1, 1, 0, 0))
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
		title=maintitle
		
		palts=[]
		for alt in alttitle:
			l,a=alt
			if not a in palts:
				l=l.lower()
				palts.append(a)
				if a == "" or a==" ":
					continue
				if l=="ja" and originaltitle is None:
					originaltitle=a
				if l==language and localtitle is None:
					localtitle=a
				if not a == localtitle and not a ==originaltitle:
					alts.append(a)
		
		if originaltitle is None:
			orginaltitle=maintitle

		if localtitle is None:
			localtitle=maintitle

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
			year=int(dates[0].year)

	
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
			"localtitle":localtitle,
			"alternates":alts,
			"sorttitle":"",
			"duration":runtime,
			"studio":"",
			"tagline":"",
			"write":"",
			"premiered":"",
			"status":"",
			"code3":id,
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

def getgenres(filter):
	ids=[]
	pages=grab_searches("%s/encyclopedia/search/genreresults?w=series&w=movies&o=rating&%s"%(domain,filter))
	for page in pages:
		ids.extend(re.findall("anime.php\?id=([0-9]*?)\"(.*?)</a>",page))
	return [x[0] for x in ids]

def results_search(animes=None,filters=None):
	if filters is None: filters=ump.args["filters"]
	if animes is None: animes=ump.args["anime"]
	if isinstance(animes,unicode): animes=eval(animes)
	index=ump.args.get("index",0)
	anime=animes[index*50:(index+1)*50]
	medias=scrape_ann_search(anime)
	
	itemcount=0
	if len(medias) > 0: 
		if not index==0:
			li=xbmcgui.ListItem("Results %d-%d"%((index-1)*50+1,index*50))
			u=ump.link_to("results_search",{"anime":animes,"filters":filters,"index":index-1})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		for media in medias:
			if "numvotes" in filters and int(media["info"]["votes"])<100:
				#print "TOO FEW VOTES FOR : "+ media["info"]["tvshowtitle"].encode("ascii","ignore")
				continue
			li=xbmcgui.ListItem("%s (%s)"%(media["info"]["localtitle"],media["info"]["type"]))
			li.setInfo(ump.defs.CT_VIDEO,media["info"])
			ump.set_content(ump.defs.CC_MOVIES)
			try:
				li.setArt(media["art"])
			except AttributeError:
				#backwards compatability
				pass
			itemcount+=1
			ump.art=media["art"]
			ump.info=media["info"]
			if len(media["episodes"].keys())==0:
				u=ump.link_to("urlselect")
				xbmcplugin.addDirectoryItem(ump.handle,u,li,False)
			else:
				u=ump.link_to("show_episodes",{"annid":media["info"]["code3"]})
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		if (index+1)*50 < len(animes) and not itemcount==0:
			li=xbmcgui.ListItem("Results %d-%d"%((index+1)*50+1,(index+2)*50))
			u=ump.link_to("results_search",{"anime":animes,"filters":filters,"index":index+1})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
	cacheToDisc=False

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=False
	if ump.page == "root":
		li=xbmcgui.ListItem("Search", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search"),li,True)

		li=xbmcgui.ListItem("Top Rated Animes", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("select_year"),li,True)

		li=xbmcgui.ListItem("Newest Animes", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("newest"),li,True)

		li=xbmcgui.ListItem("Animes by Genre", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("bygenre"),li,True)

		li=xbmcgui.ListItem("Animes by Themes", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("bytheme"),li,True)

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
			args={"anime":"getgenres('%s')"%urlencode({"g":genres[genre]}),"filters":["numvotes"]}
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("results_search",args),li,True)
	
	elif ump.page == "bytheme":
		themes=re.findall('name="th" type="checkbox" value="(.*?)".*?\(([0-9]*?)\)',ump.get_page("%s/encyclopedia/search/genre"%domain,None))
		addthemes=[]
		for theme,count in sorted([(x[0],int(x[1])) for x in themes], key=operator.itemgetter(1),reverse=True):
			if not theme in addthemes:
				addthemes.append(theme)
				li=xbmcgui.ListItem("%s (%d)"%(theme.title().replace("|"," / "),count), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
				args={"anime":"getgenres('%s')"%urlencode({"th":theme}),"filters":["numvotes"]}
				xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("results_search",args),li,True)
	
	elif ump.page == "newest":
		ids=[]
		dates=[]
		months=[]
		pages=grab_searches("%s/encyclopedia/search/genreresults?w=series&w=movies&from=%d&to=%d&lic=&a=AA&a=OC&a=TA&a=MA&a=AO&o=rating"%(domain, datetime.datetime.now().year, datetime.datetime.now().year))
		for page in pages:
			ids.extend(re.findall("anime.php\?id=([0-9]*?)\"",page))
			dates.extend(re.findall("class=\"de\-emphasized\">(.*?)<",page))
		
		for i in range(len(dates)):
			since=(datetime.datetime.now() - parser.parse(dates[i],fuzzy=True,default=datetime.datetime(1970, 1, 1, 0, 0))).days
			if  since<= 15 and since >=0:
				months.append(ids[i])

		li=xbmcgui.ListItem("Last 15 Days", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":months,"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("This Year", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_search",{"anime":ids,"filters":[]})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
				

	elif ump.page == "select_year":
		li=xbmcgui.ListItem("All Time", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		args={"anime":"getgenres('')","filters":["numvotes"]}
		u=ump.link_to("results_search",args)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		for year in reversed(range(datetime.date.today().year-50,datetime.date.today().year+1)):
			args={"anime":"getgenres('%s')"%urlencode({"from":year,"to":year}),"filters":["numvotes"]}
			li=xbmcgui.ListItem(str(year), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			u=ump.link_to("results_search",args)
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
		
		if len(ids):
			results_search(ids,[])
	
	elif ump.page == "results_search":
		results_search()
	
	elif ump.page== "show_episodes":
		annid=ump.args.get("annid",None)
		if annid is None:
			return None
		medias=scrape_ann_search([annid])
		if len(medias)<1:
			return None
		episodes=medias[0]["episodes"]
		ump.info=medias[0]["info"]
		#keys are parsed as strings
		for k,v in episodes.items():
			episodes.pop(k)
			episodes[int(float(k))]=v
		#below does not work on old versions of python
		#episodes = {float(k):v for k,v in episodes.iteritems()}
		ump.set_content(ump.defs.CC_EPISODES)
		for epi in sorted(episodes.keys(),reverse=True):
			li=xbmcgui.ListItem("%d %s"%(epi,episodes[epi]["title"]))
			try:
				li.setArt(ump.art)
			except AttributeError:
				#backwards compatability
				pass
			ump.info["title"]=episodes[epi]["title"]
			ump.info["episode"]=episodes[epi]["relativenumber"]
			#even though animes dont have season info force it so trakt will scrobble
			ump.info["season"]=1
			ump.info["absolute_number"]=epi
			u=ump.link_to("urlselect")
			li.setInfo(ump.defs.CT_VIDEO,ump.info)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,False)

	xbmcplugin.endOfDirectory(ump.handle,cacheToDisc=cacheToDisc,updateListing=False,succeeded=True)
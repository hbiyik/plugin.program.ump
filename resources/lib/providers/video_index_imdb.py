import xbmc
import xbmcgui
import xbmcplugin
from datetime import date
from urllib import quote_plus
from urllib import urlencode
import time
import re
import json
recnum=50

def scrape_imdb_search(page):
	m1=[]
	t1=time.time()
	trs=re.findall('detailed"\>(.*?)\</tr\>',page,re.DOTALL)
	t2=time.time()
	for tr in trs:
		#image
		poster=re.findall('img src="(.*?)"',tr)
		if len(poster)>0:
			poster=poster[0].split("._")[0]
		else:
			img=""
		
		#name/id
		title=re.findall('href="/title/tt([0-9]*?)/"\>(.*?)\</a\>',tr)
		if len(title)>0:
			id="tt"+str(title[0][0])
			title=title[0][1]
		else:
			title=""
			id=""
		
		#outline
		outline=re.findall('class="outline"\>(.*?)\</span',tr)
		if len(outline)>0 :
			outline=outline[0]
		else:
			outline=""

		#director
		dirs=re.findall('Dir:(.*?)\\n',tr)
		dir=""
		if len(dirs)>0:
			dirs=re.findall("\>(.*?)\<",dirs[0])
			for dr in dirs:
				dir+=dr

		#cast
		cast=re.findall('With:(.*?)\\n',tr)
		if len(cast)>0:
			cast=re.findall('"\>(.*?)\</a',cast[0])
		else:
			cast=[]

		#genre
		gen=""
		genres=re.findall('class="genre"\>(.*?)\</span',tr)
		if len(genres)>0:
			genres=re.findall("\>(.*?)\<",genres[0])
			for genre in genres:
				gen+=genre
				
		#year
		year=re.findall('class="year_type"\>\(([0-9]*?)\)',tr)
		if len(year)>0:
			year=str(year[0])
		else:
			year=""
		
		#duration
		runtime=re.findall('class="runtime"\>([0-9].*?)\s',tr)
		if len(runtime)>0:
			runtime=str(runtime[0])
		else:
			runtime=""

		#mpaa
		mpaa=re.findall('class="certificate"\>\<span title="(.*?)"',tr)
		if len(mpaa)>0:
			mpaa=mpaa[0]
		else:
			mpaa=""
		
		#rating
		rating=re.findall('class="value"\>(.*?)\</span',tr)
		if len(rating)>0:
			if "-" in rating[0][0]:
				rating=float(0)
			else:
				rating=float(rating[0])
		else:
			rating=float(0)

		movie={}
		movie["info"]={
			"count":1,
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
			"cast":cast,
			"castandrole":cast,
			"director":dir,
			"mpaa":mpaa,
			"plot":outline,
			"plotoutline":outline,
			"title":title,
			"originaltitle":title,
			"sorttitle":"",
			"duration":runtime,
			"studio":"",
			"tagline":"",
			"write":"",
			"tvshowtitle":"",
			"premiered":"",
			"status":"",
			"code":id,
			"aired":"",
			"credits":"",
			"lastplayed":"",
			"album":"",
			"artist":([]),
			"votes":"",
			"trailer":"",
			"dateadded":""
			}
		movie["art"]={
			"thumb":poster+"._V1_SX214_AL_.jpg",
			"poster":poster,
			"banner":"",
			"fanart":"",
			"clearart":"",
			"clearlogo":"",
			"landscape":""
			}
		m1.append(movie)
	
	return m1

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("Search", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search"),li,True)

		li=xbmcgui.ListItem("Top User Rated 50 Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","num_votes":"20000,","sort":"user_rating","title_type":"feature,tv_movie,short,tv_special","content_cat":ump.defs.CC_MOVIES})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("Top IMDB Rated 50 Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","num_votes":"20000,","sort":"moviemeter,asc","title_type":"feature,tv_movie,short,tv_special","content_cat":ump.defs.CC_MOVIES})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		ump.content_cat="N/A"
		li=xbmcgui.ListItem("Top Voted 50 Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"num_votes,desc","title_type":"feature,tv_movie,short,tv_special","content_cat":ump.defs.CC_MOVIES})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Top US Box Office 50 Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"boxoffice_gross_us,desc","title_type":"feature,tv_movie,short,tv_special","content_cat":ump.defs.CC_MOVIES})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "select_year":
		ump.args["year"]=""
		li=xbmcgui.ListItem("All Time", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_title",ump.args)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		for year in reversed(range(date.today().year-50,date.today().year+1)):
			ump.args["year"]=str(year)
			li=xbmcgui.ListItem(str(year), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			u=ump.link_to("results_title",ump.args)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "search":
		kb = xbmc.Keyboard('default', 'heading', True)
		kb.setDefault("")
		kb.setHiddenInput(False)
		kb.doModal()
		what=kb.getText()
		li=xbmcgui.ListItem("Search %s Title in Movies" % what, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_title",{"title":what,"title_type":"feature,tv_movie,short,tv_special","count":recnum,"sort":"moviemeter,asc","content_cat":ump.defs.CC_MOVIES})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Search %s Title in Documentaries" % what, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_title",{"title":what,"title_type":"documentary","count":recnum,"sort":"moviemeter,asc","content_cat":ump.defs.CC_MOVIES})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Search %s Title in Series" % what, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_title",{"title":what,"title_type":"tv_series,mini_series","count":recnum,"sort":"moviemeter,asc","content_cat":ump.defs.CC_TVSHOWS})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "results_title":
		ump.set_content(ump.args["content_cat"])
		#ump.args[key]=quote_plus(str(ump.args[key]).decode("windows-1254"))
		page=ump.get_page("http://www.imdb.com/search/title","utf-8",query=ump.args)
		movies=scrape_imdb_search(page)
		if len(movies) > 0: 
			for movie in movies:
				li=xbmcgui.ListItem(movie["info"]["title"])
				li.setInfo("video",movie["info"])
				li.setArt(movie["art"])
				ump.art=movie["art"]
				ump.info=movie["info"]
				u=ump.link_to("urlselect")
				xbmcplugin.addDirectoryItem(ump.handle,u,li,False)
		cacheToDisc=False

	xbmcplugin.endOfDirectory(ump.handle,	cacheToDisc=cacheToDisc)
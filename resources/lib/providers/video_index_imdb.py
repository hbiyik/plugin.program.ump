import xbmc
import xbmcgui
import xbmcplugin
from datetime import date
from urllib import quote_plus
from urllib import urlencode
import time
import re
import json
import operator
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
			"tvshowalias":"",
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
	
	def alternate(key,id):
		cd=scrape_name(id,True)
		m1[key]["info"]["originaltitle"]=cd

	gid=ump.tm.create_gid()
	for m in range(len(m1)):
		ump.tm.add_queue(alternate,(m,m1[m]["info"]["code"]),gid=gid)
	ump.tm.join(gid=gid)

	return m1


def scrape_name(id,lean=False):
	m1={"info":{},"art":{}}
	m1["info"]["originaltitle"]=""
	alts=[]
	res=ump.get_page("http://www.imdb.com/title/%s/releaseinfo"%id,"utf-8")
	akas=re.findall('<table id="akas"(.*?)</table>',res,re.DOTALL)
	if len(akas)==1:
		tds=re.findall("<td>(.*?)</td>",akas[0])
		for td in range(1,len(tds),2):
			alts.append(tds[td])
		if lean:
			return "|".join(alts)
		else:
			m1["info"]["originaltitle"]="|".join(alts)
	elif lean:
		return ""
	poster=re.findall('<img itemprop="image"\nclass="poster".*?alt="(.*?)".*?src="(.*?)"',res,re.DOTALL)
	namediv=re.findall('<h3 itemprop="name">.*?itemprop=\'url\'>(.*?)</a>.*?<span class="nobr">(.*?)</span>',res,re.DOTALL)
	if len(namediv)==1:
		namestr,datestr=namediv[0]
		m1["info"]["title"]=namestr
		m1["info"]["year"]=re.sub("[^0-9]", "", datestr.split("-")[0])
	if len(poster)==1:
		namestr,link=poster[0]
		m1["art"]["poster"]=link.split("._")[0]
		m1["art"]["thumb"]=m1["art"]["poster"]+"._V1_SX214_AL_.jpg"
	m1["info"]["code"]=id
	return m1
		

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("Search", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search",{"title":" "}),li,True)

		li=xbmcgui.ListItem("Top 50 User Rated", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","num_votes":"60000,","sort":"user_rating"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("Top 50 IMDB Rated", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","num_votes":"60000,","sort":"moviemeter,asc"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		ump.content_cat="N/A"
		li=xbmcgui.ListItem("Top 50 Voted", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"num_votes,desc"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Top 50 US Box Office", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"boxoffice_gross_us,desc"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "select_year":
		ump.args["year"]=""
		li=xbmcgui.ListItem("All Time", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("search",ump.args)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		for year in reversed(range(date.today().year-50,date.today().year+1)):
			ump.args["year"]=str(year)
			li=xbmcgui.ListItem(str(year), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			u=ump.link_to("search",ump.args)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "search":
		title=ump.args.get("title",None)
		if title:
			kb = xbmc.Keyboard('default', 'heading', True)
			kb.setDefault("")
			kb.setHiddenInput(False)
			kb.doModal()
			ump.args["title"]=kb.getText()
			ump.args["sort"]="moviemeter,asc"
		
		mquery=ump.args.copy()
		mquery["title_type"]="feature,tv_movie,short,tv_special"
		mquery["content_cat"]=ump.defs.CC_MOVIES
		li=xbmcgui.ListItem("Show Only Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_title",mquery)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		squery=ump.args.copy()
		squery["title_type"]="tv_series,mini_series"
		squery["content_cat"]=ump.defs.CC_TVSHOWS
		li=xbmcgui.ListItem("Show Only Series", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_title",squery)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		dquery=ump.args.copy()
		dquery["title_type"]="documentary"
		dquery["content_cat"]=ump.defs.CC_MOVIES
		li=xbmcgui.ListItem("Show Only Documentaries", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("results_title",dquery)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)


	elif ump.page == "results_title":
		ump.set_content(ump.args["content_cat"])
		#ump.args[key]=quote_plus(str(ump.args[key]).decode("windows-1254"))
		page=ump.get_page("http://www.imdb.com/search/title","utf-8",query=ump.args)
		movies=scrape_imdb_search(page)
		suggest=""
		if len(movies) < 1 and "title" in ump.args:
			suggest="[SUGGESTED] "
			movies=[]
			ids=[]
			if "tv_series" in ump.args["title_type"]:
				suffix='"TV Series"'
			elif "documentary" in ump.args["title_type"]:
				suffix='"Documentary"'
			else:
				suffix='-"TV Series" -Documentary'
			urls=ump.web_search('inurl:http://www.imdb.com/title/ inurl:releaseinfo %s %s'%(ump.args["title"],suffix))
			if len(urls)<1:
				return None
			else:
				for u in urls:
					idx=u.split("/")[4]
					if not idx[:2]=="tt":
						continue
					ids.append(idx)
			for id in set(ids):
				movies.append(scrape_name(id))

		if not len(movies) < 1: 
			for movie in movies:
				name=movie["info"]["title"]
				altnames=movie["info"]["originaltitle"]
				li=xbmcgui.ListItem(suggest+name)
				li.setInfo("video",movie["info"])
				try:
					li.setArt(movie["art"])
				except AttributeError:
					#backwards compatability
					pass
				ump.art=movie["art"]
				ump.info=movie["info"]
				if "tv_series" in ump.args["title_type"]:
					ump.info["tvshowtitle"]=name
					ump.info["title"]=""
					ump.info["tvshowalias"]=altnames
					ump.info["originaltitle"]=""
					u=ump.link_to("show_seasons",{"imdbid":ump.info["code"]})
					xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
				else:
					ump.info["tvshowtitle"]=""
					ump.info["title"]=name
					ump.info["tvshowalias"]=""
					ump.info["originaltitle"]=altnames
					u=ump.link_to("urlselect")
					xbmcplugin.addDirectoryItem(ump.handle,u,li,False)
		cacheToDisc=True

	elif ump.page=="show_seasons":
		imdbid=ump.args.get("imdbid",None)
		if not imdbid :
			return None
		res=ump.get_page("http://www.imdb.com/title/%s/episodes"%imdbid,"utf-8")
		seasons=re.findall('<option.*?value="([0-9]{1,2})">',res)
		if not len(seasons)>0:
			return None
		for season in sorted([int(x) for x in seasons if x.isdecimal()],reverse=True):
			li=xbmcgui.ListItem("Season %d"%season)
			ump.info["season"]=season
			u=ump.link_to("show_episodes",{"imdbid":imdbid,"season":season})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
	
	elif ump.page=="show_episodes":
		ump.set_content(ump.defs.CC_EPISODES)
		imdbid=ump.args.get("imdbid",None)
		season=ump.args.get("season",None)
		if not imdbid or not season:
			return None
		res=ump.get_page("http://www.imdb.com/title/%s/episodes?season=%d"%(imdbid,season),"utf-8")
		#episodes=re.findall('<div class="list_item(.*?)<div class="wtw-option-standalone"',res,re.DOTALL)
		title_img=re.findall('class="zero-z-index" alt="(.*?)" src="(.*?)"',res)
		episodes=re.findall('<meta itemprop="episodeNumber" content="([0-9]*?)"/>',res)
		episodes=[int(x) for x in episodes]
		plots=re.findall('<div class="item_description" itemprop="description">(.*?)</div>',res,re.DOTALL)
		dates=re.findall('<div class="airdate">\n(.*?)\n',res)
		episodes=zip(episodes,dates,plots,*zip(*title_img))
		episodes.sort(key=operator.itemgetter(0), reverse=True)
		for episode in episodes:
			epi,dat,plot,title,img=list(episode)
			li=xbmcgui.ListItem("%d. %s"%(epi,title))
			ump.info["title"]=title
			ump.info["episode"]=epi
			plot=plot.replace("\n","")
			if not 'href="/updates' in plot:
				ump.info["plot"]=plot
				ump.info["plotoutline"]=plot
			ump.art["thumb"]=img
			ump.art["poster"]=img
			li.setInfo("video",ump.info)
			try:
				li.setArt(ump.art)
			except AttributeError:
				#backwards compatability
				pass
			u=ump.link_to("urlselect")
			xbmcplugin.addDirectoryItem(ump.handle,u,li,False)

	xbmcplugin.endOfDirectory(ump.handle,	cacheToDisc=cacheToDisc)
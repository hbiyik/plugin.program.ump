import xbmc
import xbmcgui
import xbmcplugin
from datetime import date
from urllib import quote_plus
import time
import re
import operator
from ump import countries

try:
	language=xbmc.getLanguage(xbmc.ISO_639_1).lower()
except AttributeError:
	#backwards compatability
	language="en"

def get_localtitle(alts,original):
	local=original
	ww=original
	for country in countries.all:
		if language == country[2] and country[0].lower() in alts.keys():
			local=alts[country[0].lower()]
	for key in alts.keys():
		if ump.is_same("USA",key):
			ww=alts[key]		
			break
	if ww == original:
		for key in alts.keys():
			if ump.is_same("World-wide",key):
				ww=alts[key]		
				break
	return local,ww

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
		year=re.findall('class="year_type"\>\(([0-9]{4})',tr)
		if len(year)>0:
			year=int(year[0])
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
			"localtitle":title,
			"alternates":[],
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
		alts=scrape_name(id,True)
		altl=zip(*alts.items())
		if len(altl):
			m1[key]["info"]["alternates"]= altl[1]
		else:
			m1[key]["info"]["alternates"]= []
		m1[key]["info"]["localtitle"],m1[key]["info"]["title"]=get_localtitle(alts,m1[key]["info"]["originaltitle"])

	gid=ump.tm.create_gid()
	for m in range(len(m1)):
		ump.tm.add_queue(alternate,(m,m1[m]["info"]["code"]),gid=gid)
	ump.tm.join(gid=gid)

	return m1


			

def scrape_name(id,lean=False):
	m1={"info":{},"art":{}}
	m1["info"]["originaltitle"]=""
	alts={}
	res=ump.get_page("http://www.imdb.com/title/%s/releaseinfo"%id,"utf-8")
	akas=re.findall('<table id="akas"(.*?)</table>',res,re.DOTALL)
	if len(akas)==1:
		tds=re.findall("<td>(.*?)</td>",akas[0])
		pcountry=[]
		for td in range(1,len(tds),2):
			country=tds[td-1]
			if any(word in country for word in ["fake","informal","version","literal","promotional","short"]):
				continue
			country=re.sub("\s\(.*\)","",tds[td-1]).lower()
			if country in pcountry:
				continue
			pcountry.append(country)
			cname=tds[td]
			alts[country]=cname
		if lean:
			return alts
		else:
			poster=re.findall('<img itemprop="image"\nclass="poster".*?alt="(.*?)".*?src="(.*?)"',res,re.DOTALL)
			namediv=re.findall('<h3 itemprop="name">.*?itemprop=\'url\'>(.*?)</a>.*?<span class="nobr">(.*?)</span>',res,re.DOTALL)
			if len(namediv)==1:
				namestr,datestr=namediv[0]
				m1["info"]["originaltitle"]=namestr
				m1["info"]["year"]=int(re.sub("[^0-9]", "", datestr.split("-")[0]))
				m1["info"]["localtitle"],m1["info"]["title"]=get_localtitle(alts,namestr)
				m1["info"]["alternates"]= zip(*alts.items())[1]
			if len(poster)==1:
				namestr,link=poster[0]
				m1["art"]["poster"]=link.split("._")[0]
				m1["art"]["thumb"]=m1["art"]["poster"]+"._V1_SX214_AL_.jpg"
			m1["info"]["code"]=id
			return m1
	elif lean:
		return alts
	

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
			ump.args["year"]=year
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
		page=ump.get_page("http://www.imdb.com/search/title","utf-8",query=ump.args,header={"Accept-Language":"tr"})#hack imdb to give me original title with my unstandart language header
		movies=scrape_imdb_search(page)
		suggest=""
		if len(movies) < 1 or ump.args.get("google",False) and "title" in ump.args.keys():
			suggest="[SUGGESTED] "
			movies=[]
			ids=[]
			if "tv_series" in ump.args["title_type"]:
				suffix='"TV Series"'
			elif "documentary" in ump.args["title_type"]:
				suffix='"Documentary"'
			else:
				suffix=''
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
				li=xbmcgui.ListItem(suggest+movie["info"]["localtitle"])
				li.setInfo("video",movie["info"])
				try:
					li.setArt(movie["art"])
				except AttributeError:
					#backwards compatability
					pass
				ump.art=movie["art"]
				ump.info=movie["info"]
				if "tv_series" in ump.args["title_type"]:
					ump.info["tvshowtitle"]=movie["info"]["title"]
					u=ump.link_to("show_seasons",{"imdbid":ump.info["code"]})
					xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
				else:
					u=ump.link_to("urlselect")
					xbmcplugin.addDirectoryItem(ump.handle,u,li,False)
			if not ump.args.get("google",False) and "title" in ump.args.keys():
				ump.args["google"]=True
				u=ump.link_to("results_title",ump.args)
				li=xbmcgui.ListItem("Search \"%s\" in Google"%ump.args["title"])
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
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

	xbmcplugin.endOfDirectory(ump.handle,cacheToDisc=cacheToDisc,updateListing=False,succeeded=True)
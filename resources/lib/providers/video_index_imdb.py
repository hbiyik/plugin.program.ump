import xbmc
import xbmcgui
import xbmcplugin
from datetime import date
from urllib import quote_plus
import time
import re
import operator
from ump import countries
import json
import random

tmdbk="3b672de17b90fb71d393cf367b793d89"
tmdbu="http://image.tmdb.org/t/p/"
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
		if ump.is_same("master",key):
			ww=alts[key]		
			break
	if ww == original:
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

def tmdb_art(id):
	try:
		arts=json.loads(ump.get_page("http://api.themoviedb.org/3/movie/%s/images?api_key=%s"%(id,tmdbk),"utf-8"))
		fanarts=[]
		localposters=[]
		posters=[]
		for f in arts.get("backdrops",[]):
			fanarts.append("%soriginal%s"%(tmdbu,f["file_path"]))
		for p in arts.get("posters",[]):
			if p["iso_639_1"]==language:
				localposters.append("%sw342%s"%(tmdbu,p["file_path"]))
			elif p["iso_639_1"] == "en" or p["iso_639_1"] is None:
				posters.append("%sw342%s"%(tmdbu,p["file_path"]))
		if len(fanarts):
			fanart=random.choice(fanarts)
		else:
			fanart=None
		
		if len(localposters):
			poster=random.choice(localposters)
		elif len(posters):
			poster=random.choice(posters)
		else:
			poster=None
	except:
		return None,None

	return fanart,poster

def scrape_imdb_names(page):
	trs=re.findall('detailed"\>(.*?)\</tr\>',page,re.DOTALL)
	people=[]
	for tr in trs:
		#image
		main=re.findall('a href="/name/(nm[0-9]*?)/" title="(.*?)"><img src="(.*?)"',tr)
		person={}
		person["id"]=main[0][0]
		person["name"]=main[0][1]
		person["poster"]=main[0][2].split("._")[0]
		people.append(person)
	return people

def scrape_imdb_search(page):
	m1=[]
	t1=time.time()
	trs=re.findall('detailed"\>(.*?)\</tr\>',page,re.DOTALL)
	t2=time.time()
	for tr in trs:
		#image
		position=re.findall('td class="number">([0-9]*?)\.</td',tr)
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
		fanart,poster=tmdb_art(id)
		if fanart: m1[key]["art"]["fanart"]=fanart
		if poster: m1[key]["art"]["poster"]=poster
	try:
		start,end,total=re.findall('<div id="left">\n(.*?)\-(.*?) of (.*?)\n',page)[0]
		start=int(start.replace(",",""))
		end=int(end.replace(",",""))
		total=int(total.replace(",",""))
	except:
		start=end=total=0

	gid=ump.tm.create_gid()
	for m in range(len(m1)):
		ump.tm.add_queue(alternate,(m,m1[m]["info"]["code"]),gid=gid)
	ump.tm.join(gid=gid)

	return start,end,total,m1


			

def scrape_name(id,lean=False):
	m1={"info":{},"art":{}}
	m1["info"]["originaltitle"]=""
	res=ump.get_page("http://www.imdb.com/title/%s/releaseinfo"%id,"utf-8")
	namediv=re.findall('<h3 itemprop="name">.*?itemprop=\'url\'>(.*?)</a>.*?<span class="nobr">(.*?)</span>',res,re.DOTALL)
	namestr,datestr=namediv[0]
	alts={"master":namestr}
	akas=re.findall('<table id="akas"(.*?)</table>',res,re.DOTALL)
	if len(akas)==1:
		tds=re.findall("<td>(.*?)</td>",akas[0])
		pcountry=[]
		for td in range(1,len(tds),2):
			country=tds[td-1]
			if any(word in country for word in ["fake","informal","version","literal","promotional"]):
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
		ump.content_cat="N/A"
		li=xbmcgui.ListItem("Search Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("results_title",{"title":"?","title_type":"feature,tv_movie,short","sort":"moviemeter,asc"}),li,True)

		li=xbmcgui.ListItem("Search Series", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("results_title",{"title":"?","title_type":"tv_series,mini_series","sort":"moviemeter,asc"}),li,True)

		li=xbmcgui.ListItem("Search Documentaries", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("results_title",{"title":"?","title_type":"documentary","sort":"moviemeter,asc"}),li,True)

		li=xbmcgui.ListItem("Search People", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("results_name",{"name":"?"}),li,True)

		li=xbmcgui.ListItem("Top Rated Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","num_votes":"60000,","sort":"user_rating","title_type":"feature,tv_movie,short","next_page":"results_title"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
#		li=xbmcgui.ListItem("Top 50 IMDB Rated", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
#		u=ump.link_to("select_year",{"at":"0","num_votes":"60000,","sort":"moviemeter,asc"})
#		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)


		li=xbmcgui.ListItem("Top Voted Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"num_votes,desc","title_type":"feature,tv_movie,short","next_page":"results_title"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Top Box Office Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"boxoffice_gross_us,desc","title_type":"feature,tv_movie,short","next_page":"results_title"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Top Rated Series", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","num_votes":"5000,","sort":"user_rating","title_type":"tv_series,mini_series","next_page":"results_title"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("Top Voted Series", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"num_votes,desc","title_type":"tv_series,mini_series","next_page":"results_title"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Top Rated Documentaries", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","num_votes":"5000,","sort":"user_rating","title_type":"documentary","next_page":"results_title"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("Top Voted Documentaries", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("select_year",{"at":"0","sort":"num_votes,desc","title_type":"documentary","next_page":"results_title"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Genres", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("genres")
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Awards", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("awards")
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("World Cinema", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("languages")
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
	
	elif ump.page == "genres":
		genres=("Action","Adventure","Animation","Biography","Comedy","Crime","Drama","Family","Fantasy","Film-Noir","Game-Show","History","Horror","Music","Musical","Mystery","News","Reality-TV","Romance","Sci-Fi","Sport","Talk-Show","Thriller","War","Western")
		for genre in genres:
			li=xbmcgui.ListItem(genre, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			u=ump.link_to("select_year",{"at":"0","sort":"moviemeter,asc","num_votes":"1000,","genres":genre.lower().replace("-","_")})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "awards":
		awards=(("oscar_best_picture_winners","OSCARS: Best Picture Winning Movies",0),
				("oscar_best_director_winners","OSCARS: Best Director Winning Movies",0),
				("oscar_best_director_winners","OSCARS: Best Director Winning People",2),
				("oscar_best_actress_winners","OSCARS: Best Actress Winning People",2),
				("oscar_best_actor_winners","OSCARS: Best Actor Winning People",2),
				("oscar_best_supporting_actress_winners","OSCARS: Best Supporting Actress Winning People",2),
				("oscar_best_supporting_actor_winners","OSCARS: Best Supporting Actor Winning People",2),
				("oscar_winners","OSCARS: Any Category Winning Movies",0),
				("oscar_winners","OSCARS: Any Category Winning People",2),
				("emmy_winners","EMMIES: Award Winning Series",1),
				("golden_globe_winners","GOLDEN GLOBE: Award Winning Movies",0),
				("razzie_winners","RAZZIES: Award Winning Movies",0),
				("national_film_registry","National Film Board Preserved Movies",0),
				("oscar_best_director_nominees","OSCARS: Best Director Nominated People",2),
				("oscar_best_actress_nominees","OSCARS: Best Actress Nominated People",2),
				("oscar_best_actor_nominees","OSCARS: Best Actor Nominated People",2),
				("oscar_best_supporting_actress_nominees","OSCARS: Best Supporting Actress Nominated People",2),
				("oscar_best_supporting_actor_nominees","OSCARS: Best Supporting Actor Nominated People",2),
				("oscar_nominees", "OSCARS: Any Category Nominated Movies",0),
				("emmy_nominees Emmy","EMMIES: Award Nominated Series",1),
				("golden_globe_nominees","GOLDEN GLOBE: Award Nominated Movies",0),
				("razzie_nominees","RAZZIES: Award Nominated Movies",0))

		for award in awards:
			key,val,tt=award
			if tt in [0,1]:
				title_type=["feature,tv_movie,short,documentary","tv_series,mini_series"]
				li=xbmcgui.ListItem(val, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
				u=ump.link_to("results_title",{"at":"0","sort":"release_date_us,desc","groups":key,"title_type":title_type[tt]})
			elif tt==2:
				li=xbmcgui.ListItem(val, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
				u=ump.link_to("results_name",{"groups":key})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "languages":		
		langs=("ar","Arabic"),("bg","Bulgarian"),("zh","Chinese"),("hr","Croatian"),("nl","Dutch"),("fi","Finnish"),("fr","French"),("de","German"),("el","Greek"),("he","Hebrew"),("hi","Hindi"),("hu","Hungarian"),("is","Icelandic"),("it","Italian"),("ja","Japanese"),("ko","Korean"),("no","Norwegian"),("fa","Persian"),("pl","Polish"),("pt","Portuguese"),("pa","Punjabi"),("ro","Romanian"),("ru","Russian"),("es","Spanish"),("sv","Swedish"),("tr","Turkish"),("uk","Ukrainian")

		for lang in langs:
			key,val=lang
			li=xbmcgui.ListItem(val, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			u=ump.link_to("select_year",{"at":"0","sort":"moviemeter,asc","num_votes":"1000,","languages":key})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "select_year":
		ump.args["year"]=""
		if "next_page" in ump.args:
			next_page=ump.args["next_page"]
			ump.args.pop("next_page")
		else:
			next_page="search"
		li=xbmcgui.ListItem("All Time", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to(next_page,ump.args)
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		for year in reversed(range(date.today().year-100,date.today().year+1)):
			ump.args["year"]=year
			li=xbmcgui.ListItem(str(year), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			u=ump.link_to(next_page,ump.args)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "search":
		title=ump.args.get("title","")
		if title==" ":
			kb = xbmc.Keyboard('default', 'Title', True)
			kb.setDefault("")
			kb.setHiddenInput(False)
			kb.doModal()
			ump.args["title"]=kb.getText()
		
		mquery=ump.args.copy()
		mquery["title_type"]="feature,tv_movie,short"
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

	elif ump.page == "results_name":
		name=ump.args.get("name","")
		if name=="?":
			kb = xbmc.Keyboard('default', 'Name', True)
			kb.setDefault("")
			kb.setHiddenInput(False)
			kb.doModal()
			ump.args["name"]=kb.getText()
		ump.set_content(ump.args.get("content_cat",ump.defs.CC_ALBUMS))
		page=ump.get_page("http://www.imdb.com/search/name","utf-8",query=ump.args)

		people=scrape_imdb_names(page)
		ids=[]
		for p in people:ids.append(p["id"])
		if not name=="":
			js=json.loads(ump.get_page("http://www.imdb.com/xml/find?json=1&nr=1&q=%s&nm=on"%ump.args["name"],"utf-8"))
			for key in ["name_popular","name_substring","name_approx"]:
				for p in js.get(key,[]):
					if not p["id"] in ids:
						people.append({"id":p["id"],"name":p["name"],"poster":"DefaultFolder.png"})

		for person in people:
			li=xbmcgui.ListItem(person["name"],iconImage=person["poster"], thumbnailImage=person["poster"])
			u=ump.link_to("search",{"role":person["id"],"sort":"release_date_us,desc",})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "results_title":
		title=ump.args.get("title","")
		if title=="?":
			kb = xbmc.Keyboard('default', 'Title', True)
			kb.setDefault("")
			kb.setHiddenInput(False)
			kb.doModal()
			ump.args["title"]=kb.getText()
		start=end=total=0
		ump.set_content(ump.args.get("content_cat",ump.defs.CC_MOVIES))
		page=ump.get_page("http://www.imdb.com/search/title","utf-8",query=ump.args,header={"Accept-Language":"tr"})#hack imdb to give me original title with my unstandart language header
		start,end,total,movies=scrape_imdb_search(page)
		suggest=""
		if (len(movies) < 1 or ump.args.get("google",False)) and "title" in ump.args.keys():
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

		allowed=[]
		if "role" in ump.args.keys():
			page=ump.get_page("http://www.imdb.com/name/%s/"%ump.args["role"],"utf-8")
			roles=re.findall('id="(.*?)-(tt[0-9]*?)"',page)
			for role in roles:
				role_t,role_id=role
				if role_t in ["director","writer","actor"]:
					allowed.append(role_id)

		if not len(movies) < 1: 
			for movie in movies:
				if len(allowed) and not movie["info"]["code"] in allowed and "role" in ump.args.keys():
					continue
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

			if total>end:
				li=xbmcgui.ListItem("Results %d-%d"%(end+1,end+51))
				ump.args["start"]=end+1
				xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("results_title",ump.args),li,True)
			
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
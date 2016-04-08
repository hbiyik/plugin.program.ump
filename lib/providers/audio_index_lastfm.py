import json

import xbmc

from ump import countries


mirror="http://ws.audioscrobbler.com/2.0/"
encoding="utf-8"
apikey="ff9469649c8c7d2120758deca5ffa586"
recnum=50

def get_country():
	language=xbmc.getLanguage(xbmc.ISO_639_1).lower()
	found=False
	for country in countries.all:
		if language == country[2]:
			found=True
			return country[0]
	if not found:
		return "USA"

def get_img(ops,default="DefaultFolder.png"):
	im=default
	for image in reversed(ops):
		if image["#text"].startswith("http"):
			im=image["#text"]
			break
	return im

def run(ump):
	globals()['ump'] = ump
	if ump.page == "root":
		ump.index_item("Search","search",args={"search":True})
		ump.index_item("Top Artists","topartist")
		ump.index_item("Top Tracks","toptrack")
		ump.index_item("Top Artists in %s"%get_country(),"geoartist",args={"country":get_country()})
		if not get_country() == "USA":
			ump.index_item("Top Artists in USA","geoartist",args={"country":"United States"})
		if not get_country() == "United Kingdom":
			ump.index_item("Top Artists in UK","geoartist",args={"country":"United Kingdom"})
		ump.index_item("Top Artists in Countries","country",args={"page":"geoartist"})
		ump.index_item("Top Tracks in %s"%get_country(),"geotrack",args={"country":get_country()})
		if not get_country() == "USA":
			ump.index_item("Top Tracks in USA","geotrack",args={"country":"United States"})
		if not get_country() == "United Kingdom":
			ump.index_item("Top Artist in UK","geotrack",args={"country":"United Kingdom"})
		ump.index_item("Top Artist in Countries","country",args={"page":"geotrack"})
		ump.index_item("Styles by Artists","tags",args={"where":"artists"})
		ump.index_item("Styles by Albums","tags",args={"where":"albums"})
		ump.index_item("Styles by Tracks","tags",args={"where":"tracks"})
		ump.set_content(ump.defs.CC_FILES)

	elif ump.page=="tags":
		q={"method":"tag.getTopTags","api_key":apikey,"format":"json"}
		js=json.loads(ump.get_page(mirror,None,query=q))
		for result in js["toptags"]["tag"]:
			ump.index_item(result["name"].title(),"tags_%s"%ump.args["where"],args={"tag":result["name"]})
		ump.set_content(ump.defs.CC_FILES)

	elif ump.page=="tags_artists":
		q={"method":"tag.getTopArtists","api_key":apikey,"format":"json","limit":100,"tag":ump.args["tag"]}
		js=json.loads(ump.get_page(mirror,None,query=q))
		for result in js["topartists"]["artist"]:
			im=get_img(result.get("image",[]))
			if im=="":
				continue
			ump.index_item(result["name"],"artist",args={"mbid":result["mbid"],"name":result["name"],"artim":im},icon=im, thumb=im)
		ump.set_content(ump.defs.CC_ARTISTS)

	elif ump.page=="tags_albums":
		q={"method":"tag.getTopAlbums","api_key":apikey,"format":"json","limit":100,"tag":ump.args["tag"]}
		js=json.loads(ump.get_page(mirror,None,query=q))
		for result in js["albums"]["album"]:
			name="%s - %s"%(result["artist"]["name"],result["name"])
			im=get_img(result.get("image",[]))
			if im == "":
				continue
			ump.index_item(name,"album",info={"code":result["mbid"],"title":name},icon=im, thumb=im,args={"artist":result["artist"]["name"],"album":result["name"]})
		ump.set_content(ump.defs.CC_ALBUMS)

	elif ump.page=="tags_tracks":
		q={"method":"tag.getTopTracks","api_key":apikey,"format":"json","tag":ump.args["tag"]}
		js=json.loads(ump.get_page(mirror,None,query=q))
		playlist=[]
		for result in js["tracks"]["track"]:
			im=get_img(result.get("image",[]))
			if im=="":
				continue
			info={"code":result["mbid"],"title":result["name"],"artist":result["artist"]["name"],"album":""}
			art={"icon":im, "thumb":im}
			playlist.append({"info":info,"art":art})
		ump.index_item("Play Top 10","urlselect",args={"playlist":playlist[:10]},info={"title":"Top Tracks","code":""})
		ump.index_item("Play All %d"%len(playlist),"urlselect",args={"playlist":playlist},info={"title":"Top Tracks","code":""})
		for item in playlist:
			ump.index_item("%s - %s"%(item["info"]["artist"],item["info"]["title"]),"urlselect",info=item["info"],art=item["art"])
		ump.set_content(ump.defs.CC_ARTISTS)

	elif ump.page=="topartist":
		q={"method":"chart.getTopArtists","api_key":apikey,"format":"json","limit":100}
		js=json.loads(ump.get_page(mirror,None,query=q))
		for result in js["artists"]["artist"]:
			im=get_img(result.get("image",[]))
			if im=="":
				continue
			ump.index_item(result["name"],"artist",args={"mbid":result["mbid"],"name":result["name"],"artim":im},icon=im, thumb=im)
		ump.set_content(ump.defs.CC_ARTISTS)
	
	elif ump.page=="toptrack":
		q={"method":"chart.getTopTracks","api_key":apikey,"format":"json"}
		js=json.loads(ump.get_page(mirror,None,query=q))
		playlist=[]
		for result in js["tracks"]["track"]:
			im=get_img(result.get("image",[]))
			if im=="":
				continue
			info={"code":result["mbid"],"title":result["name"],"artist":result["artist"]["name"],"album":""}
			art={"icon":im, "thumb":im}
			playlist.append({"info":info,"art":art})
		ump.index_item("Play Top 10","urlselect",args={"playlist":playlist[:10]},info={"title":"Top Tracks","code":""})
		ump.index_item("Play All %d"%len(playlist),"urlselect",args={"playlist":playlist},info={"title":"Top Tracks","code":""})
		for item in playlist:
			ump.index_item("%s - %s"%(item["info"]["artist"],item["info"]["title"]),"urlselect",info=item["info"],art=item["art"])
		ump.set_content(ump.defs.CC_ARTISTS)

	elif ump.page=="country":
		page=ump.args["page"]
		ump.args.pop("page")
		processed=[]
		for country in countries.all:
			if country[0] in ["USA","United Kingdom",get_country() ] or "," in country[0]:
				continue
			if not country[0] in processed:
				ump.args["country"]=country[0]
				ump.index_item(country[0],page,args=ump.args,info=ump.info,art=ump.art)
				processed.append(country[0])
		ump.set_content(ump.defs.CC_FILES)

	elif ump.page=="geoartist":
		q={"method":"geo.getTopArtists","country":ump.args["country"],"api_key":apikey,"format":"json","limit":100}
		js=json.loads(ump.get_page(mirror,None,query=q))
		for result in js["topartists"]["artist"]:
			im=get_img(result.get("image",[]))
			if im=="":
				continue
			ump.index_item(result["name"],"artist",args={"mbid":result["mbid"],"name":result["name"],"artim":im},icon=im, thumb=im)
		ump.set_content(ump.defs.CC_ARTISTS)

	elif ump.page=="geotrack":
		q={"method":"geo.getTopTracks","country":ump.args["country"],"api_key":apikey,"format":"json","limit":100}
		js=json.loads(ump.get_page(mirror,None,query=q))
		playlist=[]
		for result in js["tracks"]["track"]:
			im=get_img(result.get("image",[]))
			if im=="":
				continue
			info={"code":result["mbid"],"title":result["name"],"artist":result["artist"]["name"],"album":""}
			art={"icon":im, "thumb":im}
			playlist.append({"info":info,"art":art})
		
		ump.index_item("Play Top 40","urlselect",args={"playlist":playlist[:40]},info={"title":"Top Tracks","code":""})
		ump.index_item("Play All %d"%len(playlist),"urlselect",args={"playlist":playlist},info={"title":"Top Tracks","code":""})
		for item in playlist:
			ump.index_item("%s - %s"%(item["info"]["artist"],item["info"]["title"]),"urlselect",info=item["info"],art=item["art"])
		ump.set_content(ump.defs.CC_ARTISTS)


	elif ump.page == "search":
		conf,what=ump.get_keyboard('default', 'Search Audio', True)
		ump.index_item("Search %s in Artists" % what,"searchresult",args={"what":what,"where":"artist"})
		ump.index_item("Search %s in Albums" % what,"searchresult",args={"what":what,"where":"album"})
		ump.index_item("Search %s in Tracks" % what,"searchresult",args={"what":what,"where":"track"})
		ump.set_content(ump.defs.CC_ALBUMS)
		
	elif ump.page == "searchresult":
		what=ump.args["what"]
		where=ump.args["where"]
		q={"method":where+".search",where:what,"api_key":apikey,"format":"json"}
		js=json.loads(ump.get_page(mirror,None,query=q))

		try:
			results=js["results"][where+"matches"][where]
		except:
			return None
		if not isinstance(results,list):
			return None

		if where=="artist":
			for result in results:
				im=get_img(result.get("image",[]))
				if im=="":
					continue
				ump.index_item(result["name"],where,args={"mbid":result["mbid"],"name":result["name"],"artim":im},icon=im, thumb=im)
			ump.set_content(ump.defs.CC_ARTISTS)
		if where=="album":
			for result in results:
				name="%s - %s"%(result["artist"],result["name"])
				im=get_img(result.get("image",[]))
				if im == "":
					continue
				ump.index_item(name,where,info={"code":result["mbid"],"title":name},icon=im, thumb=im)
			ump.set_content(ump.defs.CC_ALBUMS)
		if where=="track":
			for result in results:
				mbid=result["mbid"]
				title=result["name"]
				artist=result["artist"]
				im=get_img(result.get("image",[]))
				if im == "":
					continue
				audio={}
				audio["info"]={"year":"","tracknumber":-1,"duration":"","album":"","artist":artist,"title":title,"code":mbid}
				audio["art"]={"thumb":im,"poster":im}
				ump.index_item(artist+ " - "+title,"urlselect",icon=im, thumb=im,art=audio["art"],info=audio["info"])
			ump.set_content(ump.defs.CC_SONGS)
		
	elif ump.page == "artist":
		ambid=ump.args["mbid"]
		name=ump.args["name"]
		artim=ump.args["artim"]
		q={"method":"artist.getTopAlbums","mbid":ambid,"api_key":apikey,"format":"json"}
		js=json.loads(ump.get_page(mirror,None,query=q))
		results=js.get("topalbums",{"album":[]})["album"]
		audio={}
		audio["info"]={"year":"","tracknumber":-1,"duration":"","album":"","artist":name,"title":"","code":ambid}
		audio["art"]={"thumb":artim,"poster":artim}
		playlist=[]
		q={"method":"artist.getTopTracks","mbid":ambid,"api_key":apikey,"format":"json"}
		for track in json.loads(ump.get_page(mirror,None,query=q)).get("toptracks",{"track":[]})["track"]:
			item={}
			item["info"]={"year":"","tracknumber":-1,"duration":"",	"album":"",	"artist":track["artist"]["name"],"title":track["name"],	"code":track.get("mbid","-1")}
			im=get_img(track.get("image",[]))
			item["art"]={"thumb":im,"poster":im}
			playlist.append(item)
		ump.index_item("Play Top Tracks from: %s"%name,"urlselect",info=audio["info"],art=audio["art"],args={"playlist":playlist,"mname":"Top Tracks from: %s"%name})

		for result in results:
			audio={}
			mbid=result.get("mbid","")
			im=get_img(result.get("image",[]))
			if im == "":
				continue
			audio["info"]={"year":"","tracknumber":-1,"duration":"","album":result["name"],"artist":name,"title":"","code":mbid}
			audio["art"]={"thumb":im,"poster":im}
			ump.index_item(name + " - " +result["name"],"album",args={"artist":name,"album":result["name"]},icon=im,thumb=im,info=audio["info"],art=audio["art"])
		ump.set_content(ump.defs.CC_ARTISTS)		


	elif ump.page == "album":
		if not ump.info["code"]=="":
			q={"method":"album.getinfo","mbid":ump.info["code"],"api_key":apikey,"format":"json"}
		else:
			q={"method":"album.getinfo","artist":ump.args["artist"],"album":ump.args["album"],"api_key":apikey,"format":"json"}
		js=json.loads(ump.get_page(mirror,None,query=q))
		tracks=js.get("album",None)
		alb=js.get("album",None)
		if alb:
			relyear=2000
			albumimage=get_img(alb.get("image",[]))
			results=alb.get("tracks",{"track":[]})["track"]
			tracks=[x["name"] for x in results]
			i=0
			audio={}
			audio["info"]={"year":relyear,"tracknumber":-1,	"duration":"","album":alb["name"],"artist":alb["artist"],"title":"","code":alb.get("mbid",""),"tracks":tracks}
			audio["art"]={"thumb":albumimage,"poster":albumimage}
			playlist=[]
			for result in results:
				i+=1
				audio={}
				mbid=result.get("mbid","")
				audio["info"]={"year":relyear,"tracknumber":i,"duration":int(result["duration"]),"album":alb["name"],"artist":alb["artist"],"title":result["name"],"code":result.get("mbid","")}
				audio["art"]={"thumb":albumimage,"poster":albumimage}
				playlist.append(audio)
			ump.index_item("Play Album: %s"%alb["name"],"urlselect",info=audio["info"],art=audio["art"],args={"playlist":playlist,"mname":"%s - %s [ALBUM]"%(alb["artist"],alb["name"])})
			for item in playlist:
				ump.index_item(item["info"]["artist"]+" - "+item["info"]["title"],"urlselect",info=item["info"],art=item["art"])
		ump.set_content(ump.defs.CC_ALBUMS)
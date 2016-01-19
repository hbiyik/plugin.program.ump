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

mirror="http://ws.audioscrobbler.com/2.0/"
encoding="utf-8"
apikey="ff9469649c8c7d2120758deca5ffa586"
recnum=50

def get_img(ops,default="DefaultFolder.png"):
	im=""
	for image in reversed(ops):
		if image["#text"].startswith("http"):
			im=image["#text"]
			break
	return im

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("Search", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search",{"serach":True}),li,True)


	elif ump.page == "search":
		kb = xbmc.Keyboard('default', 'Search Audio', True)
		kb.setDefault("")
		kb.setHiddenInput(False)
		kb.doModal()
		what=kb.getText()
		li=xbmcgui.ListItem("Search %s in Artists" % what, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("searchresult",{"what":what,"where":"artist"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Search %s in Albums" % what, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("searchresult",{"what":what,"where":"album"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Search %s in Tracks" % what, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("searchresult",{"what":what,"where":"track"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
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
			ump.set_content(ump.defs.CC_ARTISTS)
			for result in results:
				mbid=result["mbid"]
				title=result["name"]
				im=get_img(result.get("image",[]))
				if im=="":
					continue
				li=xbmcgui.ListItem(title, iconImage=im, thumbnailImage=im)
				u=ump.link_to(where,{"mbid":mbid,"name":result["name"],"artim":im})
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		if where=="album":
			ump.set_content(ump.defs.CC_ALBUMS)
			for result in results:
				mbid=result["mbid"]
				title=result["name"]
				artist=result["artist"]
				im=get_img(result.get("image",[]))
				if im == "":
					continue
				li=xbmcgui.ListItem(artist+ " - "+title, iconImage=im, thumbnailImage=im)
				u=ump.link_to(where,{"mbid":mbid,"name":result["name"],"artim":im})
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		if where=="track":
			ump.set_content(ump.defs.CC_SONGS)
			for result in results:
				mbid=result["mbid"]
				title=result["name"]
				artist=result["artist"]
				im=get_img(result.get("image",[]))
				if im == "":
					continue
				audio={}
				audio["info"]={
				"year":"",
				"tracknumber":-1,
				"duration":"",
				"album":"",
				"artist":artist,
				"title":title,
				"code":mbid,
				}
				audio["art"]={
				"thumb":im,
				"poster":im,
				}
				li=xbmcgui.ListItem(artist+ " - "+title, iconImage=im, thumbnailImage=im)
				ump.art=audio["art"]
				ump.info=audio["info"]
				u=ump.link_to("urlselect")
				xbmcplugin.addDirectoryItem(ump.handle,u,li,False)
		

		

	elif ump.page == "artist":
		ump.set_content(ump.defs.CC_ALBUMS)
		ambid=ump.args["mbid"]
		name=ump.args["name"]
		artim=ump.args["artim"]
		q={"method":"artist.getTopAlbums","mbid":ambid,"api_key":apikey,"format":"json"}
		js=json.loads(ump.get_page(mirror,None,query=q))
		results=js.get("topalbums",{"album":[]})["album"]

		audio={}
		audio["info"]={
		"year":"",
		"tracknumber":-1,
		"duration":"",
		"album":"",
		"artist":name,
		"title":"",
		"code":ambid,
		}
		audio["art"]={
		"thumb":artim,
		"poster":artim,
		}
		li=xbmcgui.ListItem("Play Artist: %s"%name, iconImage=artim, thumbnailImage=artim)
		li.setInfo("audio",audio["info"])
		try:
			li.setArt(audio["art"])
		except AttributeError:
			#backwards compatability
			pass
		ump.art=audio["art"]
		ump.info=audio["info"]
		u=ump.link_to("urlselect")
		xbmcplugin.addDirectoryItem(ump.handle,u,li,False)

		for result in results:
			audio={}
			mbid=result.get("mbid","")
			im=get_img(result.get("image",[]))
			audio["info"]={
			"year":"",
			"tracknumber":-1,
			"duration":"",
			"album":result["name"],
			"artist":name,
			"title":"",
			"code":mbid,
			}
			audio["art"]={
			"thumb":im,
			"poster":im,
			}
			li=xbmcgui.ListItem(name + " - " +result["name"], iconImage=im, thumbnailImage=im)
			li.setInfo("audio",audio["info"])
			try:
				li.setArt(audio["art"])
			except AttributeError:
				#backwards compatability
				pass
			u=ump.link_to("album",{"mbid":mbid,"name":result["name"]})
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		


	elif ump.page == "album":
		ump.set_content(ump.defs.CC_SONGS)
		mbid=ump.args["mbid"]
		name=ump.args["name"]
		q={"method":"album.getinfo","mbid":mbid,"api_key":apikey,"format":"json"}
		js=json.loads(ump.get_page(mirror,None,query=q))
		alb=js.get("album",None)
		if alb:
			album=alb["name"]
			artist=alb["artist"]
			release=alb.get("releasedate","")
			alid=alb["mbid"]
			relyear=2000
			albumimage=get_img(alb.get("image",[]))
			results=alb.get("tracks",{"track":[]})["track"]
			i=0
			audio={}
			audio["info"]={
			"year":relyear,
			"tracknumber":-1,
			"duration":"",
			"album":alb["name"],
			"artist":artist,
			"title":"",
			"code":alid,
			}
			audio["art"]={
			"thumb":albumimage,
			"poster":albumimage,
			}
			li=xbmcgui.ListItem("Play Album: %s"%alb["name"], iconImage=albumimage, thumbnailImage=albumimage)
			li.setInfo("audio",audio["info"])
			try:
				li.setArt(audio["art"])
			except AttributeError:
				#backwards compatability
				pass
			ump.art=audio["art"]
			ump.info=audio["info"]
			u=ump.link_to("urlselect")
			xbmcplugin.addDirectoryItem(ump.handle,u,li,False)

			for result in results:
				i+=1
				audio={}
				mbid=result.get("mbid","")
				audio["info"]={
				"year":relyear,
				"tracknumber":i,
				"duration":int(result["duration"]),
				"album":album,
				"artist":artist,
				"title":result["name"],
				"code":mbid,
				}
				audio["art"]={
				"thumb":albumimage,
				"poster":albumimage,
				}
				li=xbmcgui.ListItem(album+" - "+result["name"], iconImage=albumimage, thumbnailImage=albumimage)
				li.setInfo("audio",audio["info"])
				try:
					li.setArt(audio["art"])
				except AttributeError:
					#backwards compatability
					pass
				ump.art=audio["art"]
				ump.info=audio["info"]
				u=ump.link_to("urlselect")
				xbmcplugin.addDirectoryItem(ump.handle,u,li,False)


	xbmcplugin.endOfDirectory(ump.handle,cacheToDisc=cacheToDisc)
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

try:
	language=xbmc.getLanguage(xbmc.ISO_639_1).lower()
except AttributeError:
	#backwards compatability
	language="en"

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":

		li=xbmcgui.ListItem("Openning This Week", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"opening","sortBy":"popularity"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Top Box Office", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"in-theaters","sortBy":"popularity"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Coming Soon", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"upcoming","sortBy":"release"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Certified Fresh Movies", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"cf-in-theaters","sortBy":"popularity","minTomato":"70"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Top DVD Rentals", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"dvd-top-rentals","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"popularity"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("New DVD Releases", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"dvd-new-releases","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"release"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Upcoming DVD", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"dvd-upcoming","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"release"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Certified Fresh DVDs", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"cf-dvd-all","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"release","certified":"true"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Countdown", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"countdown"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Binge Guide", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"binge-guide"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Five Favorite Films", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"five-favorite-films"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Now Streaming", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"now-streaming"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("Parental Guidance", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"parental-guidance"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("Total Recall", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"total-recall"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	elif ump.page == "editorial":
		ptype=ump.args.get("ptype","list")
		etype=ump.args.get("edit","countdown")
		if ptype=="list":
			pnum=ump.args.get("pnum","1")
			plink=ump.args.get("plink","")
			page=ump.get_page("http://editorial.rottentomatoes.com/%s/%s"%(etype,plink),"utf-8")
			content=re.findall('<div class="panel panel-rt(.*?)form autocomplete="off"',page,re.DOTALL)
			actp=re.findall('selected="selected">([0-9])</option>',page,re.DOTALL)
			pages=re.findall('>([0-9]*?)</option>',page,re.DOTALL)
			dwn=re.findall('data-viewnumber="(.*?)"',page)
			countdowns=re.findall('<a class="unstyled articleLink" href="(.*?)" target="">.*?<img src=(.*?) class=\'attachment-full.*?noSpacing title">(.*?)</p>',content[0],re.DOTALL)
			if not pages[0]==actp[0]:
				prep=int(actp[0])-1
				li=xbmcgui.ListItem("Page %d"%prep, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
				ump.args["plink"]="?wpv_view_count=%s&wpv_paged=%d"%(dwn[0],prep)
				u=ump.link_to("editorail",ump.args)	
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
			for ct in countdowns:
				lnk,img,title=ct
				if "video:" in title.lower(): continue
				li=xbmcgui.ListItem(re.sub("\<.*?\>","",title), iconImage=img, thumbnailImage=img)
				ump.args["ptype"]="content"
				ump.args["clink"]=lnk
				u=ump.link_to("editorial",ump.args)
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
			if not pages[-1]==actp[0]:
				prep=int(actp[0])+1
				li=xbmcgui.ListItem("Page %d"%prep, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
				ump.args["plink"]="?wpv_view_count=%s&wpv_paged=%d"%(dwn[0],prep)
				u=ump.link_to("editorial",ump.args)	
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		elif ptype=="content":
			clink=ump.args.get("clink","")
			pages=[ump.get_page(clink,"utf-8")]
			pgn=re.findall('<a href="(.*?)">([0-9])</a>',pages[0])
			for pg in pgn:
				if not pg[1]=="1":
					pages.append(ump.get_page(pg[0],"utf-8"))
			
			for page in pages:
				#countdown
				movies=re.findall("<img class='article_poster' src='(.*?)'.*?div class='article_movie_title'.*?a href='.*?'>(.*?)</a>",page,re.DOTALL)
				for movie in movies:
					img,title=movie
					title=re.sub("\: series [0-9]*","",title.lower())
					title=re.sub("\: season [0-9]*","",title.lower())
					title=title.title()
					li=xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
					ump.args["title"]=title
					u=ump.link_to("search",ump.args,module="imdb")
					xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
				#binge guide
				#5 favs
				if not len(movies):
					movies=re.findall("<h2><a href='.*?'>(.*?)</a> <span class='subtle'>\(([0-9]*?)\)</span>.*?img.*?src=.(.*?). ",page,re.DOTALL)
					for movie in movies:
						title,year,img=movie
						title=re.sub("\: series [0-9]*","",title.lower())
						title=re.sub("\: season [0-9]*","",title.lower())
						title=title.title()
						li=xbmcgui.ListItem(title, iconImage=img, thumbnailImage=img)
						ump.args["title"]=title
						u=ump.link_to("search",ump.args,module="imdb")
						xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
	
	elif ump.page=="browse":
		u="http://d3biamo577v4eu.cloudfront.net/api/private/v1.0/m/list/find"
		ump.args["limit"]="30"
		if not "page" in ump.args:
			ump.args["page"]=1
		js=json.loads(ump.get_page(u,"utf-8",query=ump.args))
		count=js["counts"]["total"]
		pcount=js["counts"]["count"]-29
		for movie in js["results"]:
			pcount-=1
			if pcount>0:continue
			img=movie["posters"]["primary"]
			li=xbmcgui.ListItem(movie["title"], iconImage=img, thumbnailImage=img)
			u=ump.link_to("search",{"title":movie["title"]},module="imdb")
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		if ump.args["page"]*30<count:
			preargs=ump.args.copy()
			preargs["page"]=ump.args["page"]+1
			img="DefaultFolder.png"
			li=xbmcgui.ListItem("Page %d"%preargs["page"], iconImage=img, thumbnailImage=img)
			u=ump.link_to("browse",preargs)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

	xbmcplugin.endOfDirectory(ump.handle,cacheToDisc=cacheToDisc,updateListing=False,succeeded=True)
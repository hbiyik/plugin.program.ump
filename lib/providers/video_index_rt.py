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

from third import unidecode

try:
	language=xbmc.getLanguage(xbmc.ISO_639_1).lower()
except AttributeError:
	#backwards compatability
	language="en"
def htmlfilter(text):
	text=re.sub("<br.*?>","\n", text)
	text=re.sub("<p.*?>","\n", text)
	text=re.sub("<.*?>","", text)
	text=re.sub( '[ \t\f\v]+', ' ', text).strip()
	text=re.sub( '\n+', '\n', text).strip()
	return text

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("LIST: Top Box Office", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"in-theaters","sortBy":"popularity"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("LIST: Top DVD Rentals", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"dvd-top-rentals","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"popularity"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("LIST: New DVD Releases", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"dvd-new-releases","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"release"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("LIST: Upcoming DVD", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"dvd-upcoming","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"release"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("LIST: Certified Fresh DVDs", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("browse",{"type":"cf-dvd-all","services":"amazon;amazon_prime;flixster;hbo_go;itunes;netflix_iw;vudu","sortBy":"release","certified":"true"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("EDITORIAL: Countdown", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"countdown"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("EDITORIAL: Binge Guide", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"binge-guide"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("EDITORIAL: Five Favorite Films", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"five-favorite-films"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("EDITORIAL: Now Streaming", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"now-streaming"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		
		li=xbmcgui.ListItem("EDITORIAL: Parental Guidance", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"parental-guidance"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)

		li=xbmcgui.ListItem("EDITORIAL: Total Recall", iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
		u=ump.link_to("editorial",{"ptype":"list","edit":"total-recall"})
		xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		ump.set_content(ump.defs.CC_FILES)
	elif ump.page == "view":
		text=htmlfilter(ump.args.get("text",""))
		title=htmlfilter(ump.args.get("title",""))
		ump.view_text(title,text)

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
				ump.args["ptype"]="list"
				u=ump.link_to("editorial",ump.args)	
				xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
			ump.set_content(ump.defs.CC_FILES)
		elif ptype=="content":
			clink=ump.args.get("clink","")
			pages=[ump.get_page(clink,"utf-8")]
			re_sfxs=["(.*?)<div class='gray-movie-block clearfix'","(.*?)<p>\xa0</p>",'(.*?)<p style="text-align\: cente',"(.*?)<h2","(.*?<div.*?)<div","(.*?)<p>Pages:"]
			for re_sfx in re_sfxs:
				articlebody=re.findall('<div class="articleContentBody">'+re_sfx,pages[0],re.DOTALL)
				if len(articlebody):
					ump.view_text("",htmlfilter(articlebody[0]))
					break
			pgn=re.findall('<a href="(.*?)">([0-9])</a>',pages[0])
			for pg in pgn:
				if not pg[1]=="1":
					pages.append(ump.get_page(pg[0],"utf-8"))
			items={}			
			for page in pages:
				#countdown
				if etype=="countdown":
					movies=re.findall("<img class='article_poster' src='(.*?)'.*?div class='article_movie_title'.*?a href='.*?'>(.*?)</a>.*?<div class='countdown-index'>#([0-9]*?)</div>.*?<div class='row countdown-item-details'>(.*?)</div>\s+?</div>\s+?</div>",page,re.DOTALL)
					for movie in movies:
						img,title,num,desc=movie
						title=re.sub("\: series [0-9]*","",title.lower())
						title=re.sub("\: season [0-9]*","",title.lower())
						li=xbmcgui.ListItem("%s) %s"%(num,title.title()), iconImage=img, thumbnailImage=img)
						items[int(num)]=(li,{"title":title,"text":desc})
				#binge guide
				#5 favs
				#nowstreaming
				#parental guidance
				#total recall
				elif etype=="binge-guide":
					rsuffix=".*?(What it is\:.*?Commitment\:.*?)</p>"
				elif etype=="five-favorite-films":
					rsuffix=".*?<div class='col-sm-17'>(.*?)</div>"
				elif etype in ["now-streaming","parental-guidance"]:
					rsuffix=".*?<div class='col-sm-20'>(.*?)</div>"
				elif etype=="total-recall":
					rsuffix=".*?<p>(.*?)</p>"
				if not etype=="countdown":
					movies=re.findall("<h2><a href='.*?'>(.*?)</a> <span class='subtle'>\(([0-9]*?)\)</span>.*?img.*?src=.(.*?). "+rsuffix,page,re.DOTALL)
					k=0
					for movie in movies:
						k+=1
						title,year,img,desc=movie
						title=re.sub("\: series [0-9]*","",title.lower())
						title=re.sub("\: season [0-9]*","",title.lower())
						li=xbmcgui.ListItem(title.title(), iconImage=img, thumbnailImage=img)
						items[k]=(li,{"title":title,"text":desc})
			for k in sorted(items.keys()):
				li,args=items[k]
				u=ump.link_to("view",args)
				commands=[('Search on IMDB', 'XBMC.Container.Update(%s)'%ump.link_to("search",args,module="imdb")),
				('Search on TVDB', 'XBMC.Container.Update(%s)'%ump.link_to("search",args,module="tvdb")),
				('Search on ANN', 'XBMC.Container.Update(%s)'%ump.link_to("search",args,module="ann"))
				]
				li.addContextMenuItems(commands,True)
				xbmcplugin.addDirectoryItem(ump.handle,u,li,False)
			ump.set_content(ump.defs.CC_ALBUMS)
	
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
			u=ump.link_to("none")
			commands=[('Search on IMDB', 'XBMC.Container.Update(%s)'%ump.link_to("search",{"title":movie["title"]},module="imdb")),
				('Search on TVDB', 'XBMC.Container.Update(%s)'%ump.link_to("search",{"title":movie["title"]},module="tvdb")),
				('Search on ANN', 'XBMC.Container.Update(%s)'%ump.link_to("search",{"title":movie["title"]},module="ann"))
				]
			li.addContextMenuItems(commands,True)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,False)
		if ump.args["page"]*30<count:
			preargs=ump.args.copy()
			preargs["page"]=ump.args["page"]+1
			img="DefaultFolder.png"
			li=xbmcgui.ListItem("Page %d"%preargs["page"], iconImage=img, thumbnailImage=img)
			u=ump.link_to("browse",preargs)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		ump.set_content(ump.defs.CC_ALBUMS)
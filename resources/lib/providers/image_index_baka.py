import xbmc
import xbmcgui
import xbmcplugin
from datetime import date
from urllib import quote_plus
from urllib import urlencode
import time
import re
import json
import urlparse
recnum=50
from xml.dom import minidom
import httplib
import datetime

from difflib import SequenceMatcher
from operator import itemgetter

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

encoding="utf-8"
stype="manga"
domain="https://www.mangaupdates.com"
perpage=30

def get_releases(id):
	#https://www.mangaupdates.com/releases.html?page=1&search=35&stype=series&perpage=100
	fpage=ump.get_page("https://www.mangaupdates.com/releases.html?page=1&search=%s&stype=series&perpage=%d"%(str(id),perpage),encoding)
	pcount=re.findall("Pages \(([0-9]*?)\)",fpage)
	res=[]
	
	if len(pcount)>0:
		pages=range(2,int(pcount[0])+1)
	else:
		pages=[]
	
	def parse_page(page):
		i=0
		for td in re.findall("class='text pad'.*?\>(.*?)\</td",page):
			td=re.sub('<[^<]+?>', '', td)
			m=i%5
			if m==0:
				#release date
				try:
					rel_dat=time.strptime(td,"%m/%d/%y")
				except:
					rel_dat=time.strptime("01/01/0001","%m/%d/%Y")
					ump.add_log("Baka release does not have a valid date '%s' for id: %s and is set to Jesus time."%(td,id))
				i+=1
				continue
			if m==1:
				#title
				tit=td
				i+=1
				continue
			if m==2:
				#volume
				vol=td
				i+=1
				continue
			if m==3:
				#chapter
				cha=td
				i+=1
				continue
			if m==4:
				#group
				gro=td
				res.append((rel_dat,tit,vol,cha,gro))
				i+=1
	parse_page(fpage)

	def parse_pages(pid):
		page=ump.get_page("https://www.mangaupdates.com/releases.html?page=%s&search=%s&stype=series&perpage=%d"%(str(pid),str(id),perpage),encoding)
		return parse_page(page)

	for p in pages:
		ump.tm.add_queue(parse_pages,(p,))

	ump.tm.join()

	return res

def get_details_mangaka(matches):
	res={}
	ids=[]
	pops=[]
	def update(k,id,name):
		if not id in ids:
			ids.append(id)
		else:
			pops.append(k)
		thumb="DefaultFolder.png"
		link="%s/authors.html?id=%s"%(domain,id)
		src=ump.get_page(link,encoding)
		info={}
		cover=re.findall("<img height.*?src='(.*?)'>",src)
		if len(cover):thumb=cover[0]
		from operator import itemgetter
		names1=sorted(re.findall('series\.html\?id\=(.*?)"\>(.*?)</a.*?>([0-9]*?)</td>\s*?</tr>',src,re.DOTALL),key=itemgetter(2),reverse=True)
		names=[]
		for name in names1:
			names.append((name[0],name[1]))
		info["orginaltitle"]=info["title"]=re.findall("<span class='tabletitle'><b>(.*?)</b>",src)[0]
		res[k]={"info":info,"art":{"thumb":thumb,"poster":thumb},"names":names}

	for k in matches.keys():
		id,name=matches[k]
		ump.tm.add_queue(update,(k,id,name))

	ump.tm.join()
	for p in pops:res.pop(p)
	return  res

def get_details(matches):
	res={}
	ids=[]
	pops=[]
	def update(k,id,name):
		if not id in ids:
			ids.append(id)
		else:
			pops.append(k)
		thumb="DefaultFolder.png"
		link="%s/series.html?id=%s"%(domain,id)
		src=ump.get_page(link,encoding)
		#<div class="sContent" ><center><img height='350' width='241' src='https://www.mangaupdates.com/image/i119027.png'></center>
		#title='Author Info'>
		#releasestitle tabletitle">Berserk</
		cover=re.findall('class="sContent".*?\<img.*?src=\'(.*?)\'',src)
		if len(cover)>0:
			thumb=cover[0]
		else:
			ump.add_log("Cant find mangaka for baka id %s"%str(id))
		mangaka=re.findall("title='Author Info'\>(.*?)\</",src)
		if len(mangaka)>0:
			mangaka=re.sub('<[^<]+?>', '', mangaka[0])
		else:
			mangaka=""
			ump.add_log("Cant find cover for baka %s"%str(id))
		title=re.findall('releasestitle tabletitle"\>(.*?)\</',src)
		if len(title)>0:
			title=re.sub('<[^<]+?>', '', title[0])
		else:
			title=name
		info={"title":title,"originaltitle":name,"writer":mangaka,"code":id}
		res[k]={"info":info,"art":{"thumb":thumb,"poster":thumb}}
	
	for k in matches.keys():
		id,name=matches[k]
		ump.tm.add_queue(update,(k,id,name))
	
	ump.tm.join()

	for p in pops:res.pop(p)
	return  res

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("Search")
		li.addContextMenuItems([],True)
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("select_type",{"stype":"title","perpage":perpage,"page":1}),li,True)
		li=xbmcgui.ListItem("Genres")
		li.addContextMenuItems([],True)
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("genres"),li,True)
		li=xbmcgui.ListItem("Themes")
		li.addContextMenuItems([],True)
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("categories"),li,True)
		li=xbmcgui.ListItem("Mangakas")
		li.addContextMenuItems([],True)
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search_mangaka",{"orderby":"series","perpage":perpage,"page":1,}),li,True)
		ump.set_content(ump.defs.CC_FILES)
	
	elif ump.page=="genres":
		page=ump.get_page("%s/genres.html"%domain,encoding)
		genres=set(re.findall("\?genre\=(.*?)'",page))
		for genre in genres:
			li=xbmcgui.ListItem(genre.replace("+"," "))
			li.addContextMenuItems([],True)
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("select_type",{"genre":genre.lower(),"orderby":"rating","filter":"somereleases","search":None,"stype":"title","perpage":perpage,"page":1}),li,True)
		ump.set_content(ump.defs.CC_FILES)

	elif ump.page=="categories":
		page=ump.get_page("%s/categories.html?perpage=100&orderby=agree"%domain,encoding)
		cats=re.findall("\?category\=(.*?)'>(.*?)</a",page)
		for cat in cats:
			v,c=cat
			li=xbmcgui.ListItem(c.replace("/s","").replace("/ies",""))
			li.addContextMenuItems([],True)
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("select_type",{"category":v,"orderby":"rating","filter":"somereleases","search":None,"stype":"title","perpage":perpage,"page":1}),li,True)
		ump.set_content(ump.defs.CC_FILES)


	elif ump.page=="select_type":
		if not "search" in ump.args:
			kb = xbmc.Keyboard('default', 'Search Baka', True)
			kb.setDefault("")
			kb.setHiddenInput(False)
			kb.doModal()
			ump.args["search"]=kb.getText()
		elif ump.args["search"] is None:
			ump.args.pop("search")
		types=(("Search Manga (Japanese Comics)","manga"),("Search Mangaka (Author)","mangaka"),("Search Manhwa (Korean Comics)","manhwa"),("Search Manhua (Chinese Comics)","manhua"),("Search Novel","novel"),("Search Artbook","artbook"),("Search Doujinshi (Self Published)","doujinshi"),("Drama CD (Scripts)","drama_cd"),("Search OEL (Original English Language)","oel"),("Search All kinds of Puplications",""))
		for type in types:
			t,v=type
			li=xbmcgui.ListItem(t)
			li.addContextMenuItems([],True)
			if v == "mangaka" :
				if not "search" in ump.args: continue
				xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search_mangaka",ump.args),li,True)
			else:
				ump.args["type"]=v
				xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search",ump.args),li,True)
		ump.set_content(ump.defs.CC_FILES)
	
	elif ump.page=="search_mangaka":
		page=ump.get_page("%s/authors.html"%domain,encoding,query=ump.args)
		names=re.findall("id=([0-9]*?)' alt='Author Info'\>(.*?)\</",page)
		pagination=re.findall('title="(.*?)">Last</a>',page)
		matches={}
		k=0
		for name in names:
			k+=1
			(id,title)=name
			if id in matches.keys():
				matches[k]+=(id," / " + re.sub('<[^<]+?>', '', title))
			else:
				matches[k] = (id,re.sub('<[^<]+?>', '', title))
		matches=get_details_mangaka(matches)

		for k in sorted(matches.keys()):
			u=ump.link_to("search",{"names":matches[k]["names"],"page":1})
			li=xbmcgui.ListItem("%s"% matches[k]["info"]["title"])
			li.setInfo(ump.defs.CT_IMAGE,matches[k]["info"])
			li.addContextMenuItems([],True)
			try:
				li.setArt(matches[k]["art"])
			except AttributeError:
				#backwards compatability
				pass
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		if len(pagination):
			page=ump.args["page"]+1
			li=xbmcgui.ListItem("Page %d"%page)
			li.addContextMenuItems([],True)
			ump.args["page"]=page+1
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search_mangaka",ump.args),li,True)
		ump.set_content(ump.defs.CC_ALBUMS)

	elif ump.page == "search":
		print ump.args
		if "names" in ump.args:
			names=ump.args["names"][(ump.args["page"]-1)*perpage:ump.args["page"]*perpage]
			if perpage*ump.args["page"]<len(ump.args["names"]):
				pagination=[True]
			else:
				pagination=[]
		else:
			page=ump.get_page("%s/series.html"%domain,encoding,query=ump.args)
			names=re.findall("id=([0-9]*?)' alt='Series Info'\>(.*?)\</a",page)
			pagination=re.findall('title="(.*?)">Last</a>',page)
		matches={}
		k=0
		for name in names:
			k+=1
			(id,title)=name
			if id in matches.keys():
				matches[k]+=(id," / " + re.sub('<[^<]+?>', '', title))
			else:
				matches[k] = (id,re.sub('<[^<]+?>', '', title))
		print matches
		matches=get_details(matches)
		for k in sorted(matches.keys()):
			u=ump.link_to("show_chapters",matches[k])
			li=xbmcgui.ListItem("%s , %s"% (matches[k]["info"]["title"],matches[k]["info"]["writer"]))
			li.setInfo(ump.defs.CT_IMAGE,matches[k]["info"])
			cmd=('Search %s' % matches[k]["info"]["writer"], 'XBMC.Container.Update(%s)'%ump.link_to("search_mangaka",{"search":matches[k]["info"]["writer"]}))
			li.addContextMenuItems([cmd],True)
			try:
				li.setArt(matches[k]["art"])
			except AttributeError:
				#backwards compatability
				pass
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
		if len(pagination):
			page=ump.args["page"]+1
			li=xbmcgui.ListItem("Page %d"%page)
			li.addContextMenuItems([],True)
			ump.args["page"]=page+1
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search",ump.args),li,True)
		ump.set_content(ump.defs.CC_ALBUMS)

	elif ump.page== "show_chapters":
		info=ump.args["info"]
		art=ump.args["art"]
		ump.art=art
		ump.info=info
		id=info["code"]
		t1=time.time()
		releases=get_releases(id)
		rel_sort=sorted(releases,key=itemgetter(0,3),reverse=True)
		
		def create_li(chapter):
			if chapter in cache:
				return
			else:
				chapter=str(chapter)
				cache.append(chapter)
				li=xbmcgui.ListItem("Chapter %s"%chapter)
				li.setInfo(ump.defs.CT_IMAGE,info)
				li.addContextMenuItems([],True)
				try:
					li.setArt(art)
				except AttributeError:
					#backwards compatability
					pass
				ump.info["season"]="-1"
				ump.info["episode"]=chapter
				u=ump.link_to("urlselect")
				xbmcplugin.addDirectoryItem(ump.handle,u,li,False)

		cache=[]
		pre=0
		suffixes=["end"]
		for rel in rel_sort:
			chapter=rel[3]
			#clear suffixes
			for suffix in suffixes:
				if " (%s)"%suffix in chapter:
					chapter=chapter.replace(" (%s)"%suffix,"")
			#clear versions
			chapter=re.sub("v[0-9].*","",chapter)

			#clear sequence releases
			if "-" in chapter:
				sequences=chapter.split("-")
				if len(sequences)==2 and sequences[0].isnumeric() and sequences[1].isnumeric():
					if int(sequences[0])>int(sequences[1]):
						chapter=sequences[0]
					else:
						chapter=sequences[1]

			#fill the missing releases
			if chapter.isnumeric():
				chapter=int(chapter)
			else:
				create_li(chapter)
				continue
			if pre==0:
				create_li(chapter)
				pre=chapter
				continue
			else:
				for i in range(pre-chapter):
					create_li(pre-i-1)
				pre=chapter

		for p in range(pre-1):
			create_li(pre-p-1)
		ump.set_content(ump.defs.CC_FILES)
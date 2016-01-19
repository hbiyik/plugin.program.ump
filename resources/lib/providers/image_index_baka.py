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

def get_releases(id):
	#https://www.mangaupdates.com/releases.html?page=1&search=35&stype=series&perpage=100
	fpage=ump.get_page("https://www.mangaupdates.com/releases.html?page=1&search=%s&stype=series&perpage=100"%str(id),encoding)
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
		page=ump.get_page("https://www.mangaupdates.com/releases.html?page=%s&search=%s&stype=series&perpage=100"%(str(pid),str(id)),encoding)
		return parse_page(page)

	for p in pages:
		ump.tm.add_queue(parse_pages,(p,))

	ump.tm.join()

	return res

def get_details(matches):
	res={}
	def update(id):
		link="https://www.mangaupdates.com/series.html?id=%s"%str(id)
		src=ump.get_page(link,encoding)
		#<div class="sContent" ><center><img height='350' width='241' src='https://www.mangaupdates.com/image/i119027.png'></center>
		#title='Author Info'>
		#releasestitle tabletitle">Berserk</
		cover=re.findall('class="sContent".*?\<img.*?src=\'(.*?)\'',src)
		if len(cover)>0:
			cover=cover[0]
		else:
			cover=""
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
			title=matches[id]
		info={"title":title,"originaltitle":matches[id],"writer":mangaka,"code":id}
		if cover=="":
			cover="DefaultFolder.png"
		art={"thumb":cover,"poster":cover}
		res[id]={"info":info,"art":art}

	for id in matches.keys():
		ump.tm.add_queue(update,(id,))
	
	ump.tm.join()
	return  res

def run(ump):
	globals()['ump'] = ump
	cacheToDisc=True
	if ump.page == "root":
		li=xbmcgui.ListItem("Search")
		xbmcplugin.addDirectoryItem(ump.handle,ump.link_to("search"),li,True)

	elif ump.page == "search":
		if "what" in ump.info.keys():
			what=ump.info["what"]
		else:
			kb = xbmc.Keyboard('default', 'Search %s'%stype, True)
			kb.setDefault("")
			kb.setHiddenInput(False)
			kb.doModal()
			what=kb.getText()
			ump.info["what"]=what
		q={"page":1,"search":what,"stype":"title","perpage":100}
		page=ump.get_page("https://www.mangaupdates.com/series.html",encoding,query=q)
		names=re.findall("id=([0-9]*?)' alt='Series Info'\>(.*?)\</",page)
		matches={}
		for name in names:
			(id,title)=name
			if similar(what,title)>0.5:
				if id in matches.keys():
					matches[id]+=" / " + re.sub('<[^<]+?>', '', title)
				else:
					matches[id] = re.sub('<[^<]+?>', '', title)
		matches=get_details(matches)

		for k in matches.keys():
			li=xbmcgui.ListItem("%s , %s"% (matches[k]["info"]["title"],matches[k]["info"]["writer"]))
			li.setInfo(ump.defs.CT_IMAGE,matches[k]["info"])
			try:
				li.setArt(matches[k]["art"])
			except AttributeError:
				#backwards compatability
				pass
			u=ump.link_to("show_chapters",matches[k])
			xbmcplugin.addDirectoryItem(ump.handle,u,li,True)
	
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

	xbmcplugin.endOfDirectory(ump.handle,	cacheToDisc=cacheToDisc)
import cookielib
import inspect
import json
import os
from random import choice
import re
import socket
from string import punctuation
import sys
import time
import traceback
from urllib import urlencode
import urllib2
from urlparse import parse_qs

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from quality import meta
from third.unescape import unescape
from third.unidecode import unidecode
from ump import buffering
from ump import cloudfare
from ump import defs
from ump import providers
from ump import proxy
from ump import task
from ump import ui
from ump import webtunnel
from ump import prefs 
from ump import http

addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

def humanint(size,precision=2):
	suffixes=['B','KB','MB','GB','TB']
	suffixIndex = 0
	while size > 1024:
		suffixIndex += 1 #increment the index of the suffix
		size = size/1024.0 #apply the division
	return "%.*f %s"%(precision,size,suffixes[suffixIndex])

def humanres(w,h):
	res=""
	heights=[240,360,480,576,720,1080,2160,4320]
	if h == 0 or w == 0 :
		return "???p"
	for height in heights:
		if h>=height*height/w:
			res=str(height)+"p"
	return res

class ump():
	def __init__(self,pt=False):
		self.index_items=[]
		self.settings={}
		self.buffermode=buffering.get()
		self.log=""
		self.handle = int(sys.argv[1])
		self.ws_limit=False #web search limit
		self.defs=defs
		self.monitor=xbmc.Monitor()
		if self.monitor.abortRequested():sys.exit()
		self.window = ui.listwindow('select.xml', addon_dir,'Default', '720p',ump=self)
		self.iwindow = ui.imagewindow('picture.xml', addon_dir,"Default","720p")
		self.urlval_en=True
		self.urlval_tout=30
		self.urlval_d_size={self.defs.CT_VIDEO:1000000,self.defs.CT_AUDIO:10000,self.defs.CT_IMAGE:200}
		self.urlval_d_tout=1.5
		self.tm_conc=int(float(addon.getSetting("conc")))
		self.player=None
		self.cfagents=prefs.get("cfagents")
		self.cflocks={}
		self.mirrors=[]
		self.terminate=False
		self.dialog=xbmcgui.Dialog()
		self.dialogpg=xbmcgui.DialogProgressBG()
		self.dialogpg.create("UMP")
		self.dialogpg.update(100)
		self.tm=task.manager(self.dialogpg,self.tm_conc)
		self.loaded_uprv={}
		self.checked_uids={"video":{},"audio":{},"image":{}}
		self.pt=pt
		socket.socket = proxy.getsocket()
		policy=cookielib.DefaultCookiePolicy(rfc2965=True, rfc2109_as_netscape=True, strict_rfc2965_unverifiable=False)
		if not os.path.exists( xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump')):
			os.makedirs(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'))
		self.cj=cookielib.LWPCookieJar(os.path.join( xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'), "cookie"))
		self.cj.set_policy(policy)
		if os.path.exists(os.path.join( xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'), "cookie")):
			try:
				self.cj.load()
			except cookielib.LoadError:
				pass
		self.opener = urllib2.build_opener(http.HTTPErrorProcessor,urllib2.HTTPCookieProcessor(self.cj))
		if addon.getSetting("overrideua")=="true":
			self.ua=addon.getSetting("useragent")
		else:
			from ump import useragents
			self.ua=choice(useragents.all)
		self.opener.addheaders = [('User-agent', self.ua)]
		self.tunnel=webtunnel.tunnel(self.opener)
		query=sys.argv[2][1:]
		result=parse_qs(query)
		[self.module]= result.get('module', ["ump"])
		[self.page]= result.get('page', ["root"])
		[args]= result.get('args', ["{}"])
		self.args=json.loads(args)
		for keep in ["info","art"]:
			[lst]=result.get(keep, ["{}"])
			setattr(self,keep,json.loads(lst))
		[self.content_type]= result.get('content_type', ["ump"])
		[self.content_cat]= result.get('content_cat', ["ump"])
		self.loadable_uprv=providers.find(self.content_type,"url")
		self.dialogpg.update(100,"UMP %s:%s:%s"%(self.content_type,self.module,self.page))
	
	def get_keyboard(self,*args):
		kb = xbmc.Keyboard(*args)
		kb.setDefault("")
		kb.setHiddenInput(False)
		if not self.monitor.abortRequested():
			kb.doModal()
		if self.monitor.abortRequested():
			self.dialogpg.close()
			sys.exit()
		return kb.isConfirmed(),kb.getText()
		
	def absuri(self,pre,post):
		if pre.startswith("//"):
			pre="http:"+pre
		if pre.endswith("/"):
			pre=pre[:-1]
		if post.startswith("http://") or post.startswith("https://"):
			return post
		elif post.startswith("/"):
			d=pre.split("/")
			return d[0]+"//"+d[2]+post
		else:
			return pre+post

		
	def index_item(self,name,page=None,args={},module=None,thumb="DefaultFolder.png",icon="DefaultFolder.png",info={},art={},cmds=[],adddefault=True,removeold=True,isFolder=True):
		if page=="urlselect":isFolder=False
		if info == {}:info=self.info
		if info is None:info={} 
		if art == {}:art=self.art
		if art is None: art={}
		#if thumb == "DefaultFolder.png" and "thumb" in art and not art["thumb"] == "":thumb=art["thumb"]
		#if icon == "DefaultFolder.png" and "thumb" in art and not art["thumb"] == "":icon=art["thumb"]
		self.info=info
		self.art=art
		u=self.link_to(page,args,module)
		li=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=thumb)
		li.setArt(art)
		li.setInfo(self.content_type,info)
		coms=[]
		if adddefault:
			coms.append(('Detailed Info',"Action(Info)"))
			coms.append(('Bookmark',"RunScript(%s,addfav,%s,%s,%s,%s,%s)"%(os.path.join(addon_dir,"lib","ump","script.py"),str(isFolder),self.content_type,json.dumps(name),thumb,u)))
		coms.extend(cmds)
		if adddefault:
			coms.append(("Addon Settings","Addon.OpenSettings(plugin.program.ump)"))
		li.addContextMenuItems(coms,removeold)
		self.index_items.append((u,li,isFolder,adddefault,coms,removeold))
		return li

	def view_text(self,label,text):
		try:
			id = 10147
			xbmc.executebuiltin('ActivateWindow(%d)' % id)
			xbmc.sleep(100)
			win = xbmcgui.Window(id)
			retry = 50
			while (retry > 0):
				try:
					xbmc.sleep(10)
					win.getControl(1).setLabel(label)
					win.getControl(5).setText(text)
					retry = 0
				except:
					retry -= 1
		except:
			pass


	def match_cast(self,casting):
		match_cast=False
		if len(casting)>0:
			infocasting=self.info["cast"]
			cast_found=0
			for cast in casting:
				for icast in infocasting:
					if self.is_same(cast,icast):
						cast_found+=1
						continue

			if len(casting)==cast_found or (len(infocasting)==cast_found and len(casting)>len(infocasting)) or (len(casting)==cast_found and len(casting)<len(infocasting)):
				match_cast=True
		return match_cast

	def check_codes(self,codes):
		have=False
		for cnum in codes:
			if "code%d"%cnum in self.info.keys() and not (self.info["code%d"%cnum ] == "" or self.info["code%d"%cnum ]== " " ):
				have=True
				break

		return have

	def get_vidnames(self,max=5,org_first=True):
		is_serie="tvshowtitle" in self.info.keys() and not self.info["tvshowtitle"].replace(" ","") == ""
		names=[]
		if is_serie:
			ww=self.info["tvshowtitle"]
		else:
			ww=self.info["title"]
		if org_first:
			names.append(self.info["originaltitle"])
			names.append(ww)
		else:
			names.append(ww)
			names.append(self.info["originaltitle"])
		names.append(self.info["localtitle"])
		names.extend(self.info["alternates"])
		names2=[]
		for name in names:
			if not name in names2:
				names2.append(name)

		if max==0:
			return is_serie,names2
		else:
			return is_serie,names2[:max]

	def set_content(self,content_cat="ump",enddir=True):
		if content_cat=="N/A":
			content_cat=self.content_cat
		else:
			self.content_cat=content_cat
		xbmcplugin.setContent(self.handle, content_cat)
		items=[]
		if len(self.index_items):
			for u,li,isfolder,adddef,coms,remold in self.index_items:
				items.append((u,li,isfolder))
				if adddef:
					coms.append(('Set current view \"default\" for %s'%content_cat,"RunScript(%s,setview,%s,%s)"%(os.path.join(addon_dir,"lib","ump","script.py"),self.content_type,content_cat)))
					li.addContextMenuItems(coms,remold)
			xbmcplugin.addDirectoryItems(self.handle,items,len(items))
		if enddir:xbmcplugin.endOfDirectory(self.handle,cacheToDisc=False,updateListing=False,succeeded=True)
		wmode=addon.getSetting("view_"+content_cat).lower()
		if wmode=="":wmode="default"
		if not wmode == "default":
			mode=self.defs.VIEW_MODES[wmode].get(xbmc.getSkinDir(),None)
		else:
			mode=prefs.get("pref_views",content_cat,xbmc.getSkinDir())
			if mode=={}: mode=None
		if self.content_type==self.defs.CT_AUDIO and content_cat in [self.defs.CC_MOVIES,self.defs.CC_SONGS,self.defs.CC_ARTISTS,self.defs.CC_ALBUMS]:
			#issue #38
			self.add_log("UMP issue #38 %s skippied view: %s"%(content_cat,wmode))
		elif not mode is None:
			for i in range(0, 10*60):
				if self.terminate or self.monitor.abortRequested():
					break
				if xbmc.getCondVisibility('Container.Content(%s)' % content_cat):
					xbmc.executebuiltin('Container.SetViewMode(%d)' % mode)
					break
				xbmc.sleep(100)
				
	def is_same(self,name1,name2,strict=False):
		predicate = lambda x:x not in punctuation+" "
		if strict:
			return filter(predicate,name1.lower())==filter(predicate,name2.lower())
		else:
			name1=name1.lower()
			name2=name2.lower()
			for word in ["the"]:
				name1=name1.replace("%s "%word,"")
				name2=name2.replace("%s "%word,"")
			return filter(predicate,unidecode(name1))==filter(predicate,unidecode(name2))
	
	def link_to(self,page=None,args={},module=None):
		query={}
		query["module"]=[module,self.module][module is None]
		query["page"]=[page,self.page][page is None]
		query["args"]=json.dumps(args)
		query["content_type"]=self.content_type
		for keep in ["info","art"]:
			query[keep]=json.dumps(getattr(self,keep))
		return sys.argv[0] + '?' + urlencode(query)

	def get_page(self,url,encoding,query=None,data=None,range=None,tout=None,head=False,referer=None,header=None,tunnel="disabled",forcetunnel=False):
		
		if self.terminate:
			raise task.killbill

		#python cant handle unicode urlencoding so needs to get dirty below.
		if not query is None:
			query=urlencode (dict ([k, v.encode('utf-8') if isinstance (v, unicode) else v] for k, v in query.items())) 
			url=url+"?"+query
		if not data is None:
			data=urlencode (dict ([k, v.encode('utf-8') if isinstance (v, unicode) else v] for k, v in data.items()))
		#change timeout
		if tout is None:
			tout=int(float(addon.getSetting("tout")))

		headers={'Accept-encoding':'gzip'}
		if not referer is None : headers["Referer"]=referer
		if not header is None :
			for k,v in header.iteritems():
				headers[k]=v
		tmode="disabled"
		if head==True:
			req=http.HeadRequest(url,headers=headers)
		else:
			if not range is None : headers["Range"]="bytes=%d-%d"%(range)
			req=urllib2.Request(url,headers=headers)
		if not head:
			tmode=self.tunnel.set_tunnel(tunnel,force=forcetunnel)
			req=self.tunnel.pre(req,tmode,self.cj)
		response = cloudfare.ddos_open(url,self.opener, req, data,tout,self.cj,self.cfagents,self.cflocks,self.tunnel,tmode)
		self.tunnel.cook(self.cj,self.cj.make_cookies(response,req),tmode)
			
		if head :return response
		
		stream=cloudfare.readzip(response)
		stream=self.tunnel.post(stream,tmode)

		if encoding is None:
			#binary data
			src=stream
		else:
			#unicode data
			src=unicode(unescape(stream.decode(encoding,"ignore")))
		return src
	
	def web_search(self,query):
		if self.ws_limit:
			return None
		urls=[]
		query={"v":"1.0","q":query}
		j=json.loads(self.get_page("http://ajax.googleapis.com/ajax/services/search/web","utf-8",query=query))
		status=j.get("responseStatus",0)
		if not status==200:
			self.add_log("web search exceeded its limit")
			self.ws_limit=True
			return None
		else:
			results=j["responseData"]["results"]
			for result in results:
				urls.append(result["unescapedUrl"])
		return urls

	def notify_error(self,e,silent=True):
		frm = inspect.trace()[-1]
		mod = inspect.getmodule(frm[0])
		modname = mod.__name__ if mod else frm[1]
		errtype= e.__class__.__name__
		if not silent:
			self.dialog.notification("ERROR","%s : %s"%(modname, errtype))
		if not errtype=="killbill" and addon.getSetting("tracetolog")=="true":
			print traceback.format_exc()

	def add_log(self,line):
		line=unidecode(line)
		if hasattr(self,"window") and hasattr(self.window,"status"):
			self.log=line+"\n"+self.log
			self.window.status.setText(self.log)
		if addon.getSetting("logtolog")=="true":
			print line

	def add_mirror(self,parts,name,wait=0,missing="drop"):
		if not (self.terminate or self.monitor.abortRequested()) and isinstance(parts,list) and len(parts)>0:
			for part in parts:
				upname=part.get("url_provider_name",None)
				uphash=part.get("url_provider_hash",None)
				#sanity check
				if upname is None or uphash is None:
					return False
				#check if there is an appropriate url provider
				if not providers.is_loadable(self.content_type,"url",upname,self.loadable_uprv):
					self.add_log("no appropriate url provider. Skipping : %s , %s" % (str(self.content_type),str(upname)))
					return False
				#check if provider first time. checked ids are dynamic on provider name
				elif upname in self.checked_uids[self.content_type].keys():
				#check if already proccesed
					if uphash in self.checked_uids[self.content_type][upname]:
						self.add_log("already processed, skipping :%s , %s, %s " % (str(self.content_type),str(upname),str(uphash)))
						return False
				else:
				#if first time, create list dynamically
					self.checked_uids[self.content_type][upname]=[]
				self.checked_uids[self.content_type][upname].append(uphash)
			self.tm.add_queue(target=self._on_new_id, args=(parts,name,wait,missing),pri=5)
		else:
			return False

	def max_meta(self,parts):
		#get the highest quality info from each part and mirror
		q=0
		max_w=0
		max_h=0
		max_s=0
		part_s=0
		max_key=""
		for part in parts:
			ss=0
			part_s=0
			for key,mirror in part["urls"].iteritems():
				if not part["urls"][key]["meta"] == {}:
					t=part["urls"][key]["meta"]["type"]
					w=part["urls"][key]["meta"]["width"]
					h=part["urls"][key]["meta"]["height"]
					s=part["urls"][key]["meta"]["size"]
					if not (w is None or h is None) and w*h>=q:
						max_w=w
						max_h=h
						q=w*h
					if not s is None and s>ss:
						max_key=key
						part_s=s
						ss=s
			max_s+=part_s
		return max_key,max_w,max_h,max_s

	def _on_new_id(self,parts,name,wait,missing):
		##validate media providers url first before adding
		self._validateparts(parts,wait)
		ignores=[]
		for k in range(len(parts)):
			if parts[k]["urls"]=={}:
				#if even 1 part is missing drop the mirror!!
				if missing=="drop":
					self.add_log("mirror dropped, has missing parts: %s"%str(parts))
					return False
				elif missing=="ignore":
					ignores.append(k)
		
		for ignore in ignores:
			self.add_log("part %s,%s ignored"%(parts[ignore]["url_provider_name"],parts[ignore]["url_provider_hash"]))
			parts.pop(ignore)

		#if payer is not yet ready init it.
		if self.player is None:
			self.player=ui.xplayer(ump=self)

		max_k,max_w,max_h,max_s=self.max_meta(parts)
		prefix_q=prefix_s=""

		if max_w*max_h>0:
			prefix_q="[R:%s]"%humanres(max_w,max_h)

		if max_s>0: 
			prefix_s="[F:%s]"%humanint(max_s)
		mname=prefix_q+prefix_s+name
		
		autoplay=False
		if self.content_type==self.defs.CT_VIDEO and addon.getSetting("auto_en_video")=="true":
			if addon.getSetting("video_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"]:
				if unicode(prefix_q[3:-2]).isnumeric() and int(prefix_q[3:-2])>=int(float(addon.getSetting("min_vid_res"))):
					autoplay=True
			if addon.getSetting("video_val_method")=="Check if Alive Only" or addon.getSetting("video_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"] and autoplay:
				tags=re.findall("\[(.*?)\]",name)
				required=addon.getSetting("require_tag").split(",")
				filtered=addon.getSetting("dont_require_tag").split(",")
				autoplay=True
				for tag in tags:
					if not tag=="" and tag.lower().replace(" ","") in [x.lower().replace(" ","") for x in filtered]:
						autoplay=False
						break
				
				for require in required:
					if not require=="" and not require.lower().replace(" ","") in [x.lower().replace(" ","") for x in tags]:
						autoplay=False
						break
				
		if self.content_type==self.defs.CT_AUDIO and addon.getSetting("auto_en_audio")=="true" and addon.getSetting("audio_val_method")=="Check if Alive Only":
			autoplay=True

		if self.content_type==self.defs.CT_IMAGE and addon.getSetting("auto_en_image")=="true" and addon.getSetting("audio_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"]:
			autoplay=True

		item=xbmcgui.ListItem()
		item.setLabel(mname)
		item.setLabel2(self.info["title"])
		item.setProperty("parts",json.dumps(parts))
		upname=parts[0].get("url_provider_name",None)
		if not upname is None:
			item.setIconImage("http://boogie.us.to/dataserver/ump/images/"+parts[0]["url_provider_name"]+".png")
		#if there is no more mirrors and media does not require a provider directly play it.
		if autoplay:
			try:
				state=self.player.create_list(item,True)
				if state:
					self.shut(True,3)
				return None
			except Exception,e:
				self.notify_error(e)

		self.window.addListItem(item)
		if False and self.content_type==self.defs.CT_VIDEO and addon.getSetting("video_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"] and len(parts)==1:
			from ump import globaldb
			tags=re.findall("\[(.*?)\]",mname)
			hs=fs=d=""
			for tag in tags:
				if tag.startswith("HS:"): hs=tag.split("HS:")[1]
				if tag.startswith("FS:"): fs=tag.split("FS:")[1]
				if tag.startswith("D:"): d=tag.split("D:")[1]
			globaldb.sync(self,parts[0]["url_provider_name"],parts[0]["url_provider_hash"],parts[0]["urls"][max_k]["url"],humanres(max_w,max_h),max_w,max_h,hs,fs,d,float(max_s)/1000000)

	def _validateparts(self,parts,wait):
		gid=self.tm.create_gid()
		def wrap(i):
			parts[i]=self._validatepart(parts[i])

		for k in range(len(parts)):
			self.tm.add_queue(wrap,(k,),gid=gid,pri=5)
			time.sleep(wait)
		self.tm.join(gid)

	def _validatepart(self,part):
		metaf=getattr(meta,self.content_type)
		timeout=self.urlval_tout
		provider=providers.load(self.content_type,"url",part["url_provider_name"])
		if hasattr(provider,"timeout") and isinstance(provider.timeout,int):
			timeout=provider.timeout
		#if urls require validation and url is not validated or timed out
		if not "uptime" in part.keys() or time.time()-part["uptime"]>timeout:

			try:
				self.add_log("validating %s:%s"%(part["url_provider_name"],part["url_provider_hash"]))
				part["urls"]=provider.run(part["url_provider_hash"],self,part.get("referer",""))
			except (socket.timeout,urllib2.URLError,urllib2.HTTPError),e:
				self.add_log("dismissed due to timeout: %s " % part["url_provider_name"])
				part["urls"]={}
			except Exception,e:
				self.notify_error(e)
				part["urls"]={}
			#validate url by downloading header (and check quality)
			if not isinstance(part["urls"],dict):
				part["urls"]={}
			for key in part["urls"].keys():
				try:
					u=part["urls"][key]
					#overide the referer from url provider when it sends dict mirrors
					if not isinstance(u,dict):
						part["urls"][key]={}
						part["urls"][key]["referer"]=part.get("referer","")
						part["urls"][key]["url"]=u
					method=addon.getSetting(self.content_type+"_val_method")
					m=metaf("",method,self.get_page,part["urls"][key]["url"],part["urls"][key]["referer"])
					part["urls"][key]["meta"]=m
#				except (socket.timeout,urllib2.URLError,urllib2.HTTPError),e:
#					part["urls"].pop(key)
#					self.add_log(" dismissed due to network error: %s" % part["url_provider_name"])
#					print part
#					print e
				except Exception,e:
					self.notify_error(e)
					part["urls"].pop(key)
					self.add_log("key removed : %s, %s"%(key,part["url_provider_name"]))
			part["uptime"]=time.time()
			k,w,h,s=self.max_meta([part])
			part["defmir"]=k
		return part

	def shut(self,play=False,noblock=0):
		self.terminate=True
		prefs.set("cfagents",self.cfagents)
		self.tm.s.set()
		if hasattr(self,"dialogpg"):
			self.dialogpg.close()
			del(self.dialogpg)
		if self.monitor.abortRequested():
			return None
		if hasattr(self,"window"):
			self.window.close()
			if hasattr(self.window,"status"):
				del(self.window.status)
			del(self.window)
		if hasattr(self,"iwindow"):
			self.iwindow.close()
			if hasattr(self.iwindow,"img"):
				del(self.iwindow.img)
			del(self.iwindow)
		if hasattr(self,"dialog"):
			del(self.dialog)
		try:
			self.cj.save()
		except:
			try:
				os.remove(os.path.join( xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'), "cookie"))
			except:
				pass
		if play:
			self.player.xplay()
			cnt=0
		else:
			cnt="all"
		if hasattr(self,"player"):
			del(self.player)
		if self.handle=="-1":
			self.tm.join(noblock=noblock,cnt=cnt)
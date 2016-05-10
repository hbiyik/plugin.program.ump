import inspect
import json
import os
from random import choice
import re
from urlparse import parse_qs

import sys
import time
import traceback
from urllib import urlencode

import xbmcgui

from quality import meta

from ump import buffering
from ump import defs
from ump import prefs 
from ump import providers

class ump():
	def __init__(self,backend="kodi"):
		if isinstance(backend,str):
			self.backend=__import__("backend",fromlist=[backend]).interface()
		else:
			self.backend=backend
		self.index_items=[]
		self.log=""
		self.ws_limit=False #web search limit
		self.buffermode=buffering.get()
		if self.backend.abortRequested():sys.exit()	
		self.urlval_tout=30#time in seconds that url needs to be revalidated
		self.checked_uids={"video":{},"audio":{},"image":{}}
		self.terminate=False
		#navigation directors
		self.__init_nav()
		self.loadable_uprv=None
		self.backend.dialogbg.update(100,"UMP %s:%s:%s"%(self.content_type,self.module,self.page))
		self.__is_ui_init=False
		self.__is_browser_init=False
		self.__is_tm_init=False
	
	def __init_ui(self):
		from ump import ui
		self.window = ui.listwindow('select.xml', defs.addon_dir,'Default', '720p',ump=self)
		self.iwindow = ui.imagewindow('picture.xml', defs.addon_dir,"Default","720p")
		self.__is_ui_init=True
		
	def __init_nav(self):	
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
			
	def __init_browser(self):
		import cookielib
		import socket
		import urllib2
		from ump import proxy
		from ump import webtunnel
		from ump import http
		from ump import cloudfare
		from third.unescape import unescape
		
		self.cfagents=prefs.get("cfagents")
		self.cflocks={}
		socket.socket = proxy.getsocket()
		policy=cookielib.DefaultCookiePolicy(rfc2965=True, rfc2109_as_netscape=True, strict_rfc2965_unverifiable=False)
		self.cj=cookielib.LWPCookieJar(os.path.join(defs.addon_ddir, "cookie"))
		self.cj.set_policy(policy)
		if os.path.exists(defs.addon_cookfile):
			try:
				self.cj.load()
			except cookielib.LoadError:
				pass
		if defs.addon.getSetting("verifyssl").lower()=="false":
			self.opener = urllib2.build_opener(http.HTTPErrorProcessor,urllib2.HTTPCookieProcessor(self.cj),http.HTTPSHandler)
		else:
			self.opener = urllib2.build_opener(http.HTTPErrorProcessor,urllib2.HTTPCookieProcessor(self.cj))	
		if defs.addon.getSetting("overrideua")=="true":
			self.ua=defs.addon.getSetting("useragent")
		else:
			from ump import useragents
			self.ua=choice(useragents.all)
		self.opener.addheaders = [('User-agent', self.ua)]
		self.tunnel=webtunnel.tunnel(self.opener)
		self.__is_browser_init=True
		
	def __init_tm(self):
		from ump import task
		self.tm=task.manager(self.backend.dialogbg,int(float(defs.addon.getSetting("conc"))))
		self.__is_tm_init=True
	
	def list_indexers(self,content_type=None):
		if content_type is None: content_type = self.content_type
		for provider in providers.find(content_type,"index"):
			provider_cat,provider_type,provider_name=provider
			img=defs.arturi+provider_name+".png"
			if self.content_type == "ump":
				content_type=provider_cat
			elif content_type is None:
				content_type=self.content_type
			self.index_item(provider_name.title(),content_type=content_type,module=provider_name, icon=img, thumb=img)
		self.set_content(defs.CC_ALBUMS)		
	
	def url_select(self,content_type=None):
		if content_type is None: content_type=self.content_type
		link_providers=providers.find(content_type,"url")
		if not defs.addon.getSetting("tn_chk_url_en").lower()=="false":
			from ump import webtunnel
			webtunnel.check_health(self,True)
		if len(link_providers)==0:
			self.backend.dialog.notification("ERROR","There is no available providers for %s"%content_type)
		else:
			for provider in link_providers:
				try:
					provider=providers.load(content_type,"link",provider[2])
				except Exception, e:
					self.notify_error(e)
					continue
				self.add_task(provider.run, (self,),pri=10)
			self.window.doModal()
			
	def load_indexer(self,content_type=None,module=None):
		if content_type is None: content_type=self.content_type
		if module is None: module = self.module
		indexers=providers.find(content_type,"index")
		if	providers.is_loadable(content_type,"index",module,indexers)==1:
			try:
				providers.load(content_type,"index",module).run(self)
			except Exception,e:
				self.notify_error(e)
				
		elif providers.is_loadable(content_type,"index",module,indexers)==2:
			try:
				providers.load("ump","index",module).run(self)
			except Exception,e:
				self.notify_error(e)
	
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
		return self.backend.add_index_item(name,u,page,args,module,thumb,icon,info,art,cmds,adddefault,removeold,isFolder)

	def view_text(self,label,text):
		return self.backend.view_text(label,text)

	def set_content(self,content_cat="ump",enddir=True):
		self.content_cat=content_cat
		self.backend.end_index_items(self,self.index_items,self.content_type,content_cat="ump",enddir=True)
				
	def __link_to(self,page=None,args={},module=None,content_type=None):
		query={}
		query["module"]=[module,self.module][module is None]
		query["page"]=[page,self.page][page is None]
		query["args"]=json.dumps(args)
		query["content_type"]=[content_type,self.content_type][content_type is None]
		for keep in ["info","art"]:
			query[keep]=json.dumps(getattr(self,keep))
		return sys.argv[0] + '?' + urlencode(query)
	
	def add_task(self,target,args,gid=0,pri=0):
		if not self.__is_tm_init: self.__init_tm()
		self.tm.add_task(target,args,gid,pri)
		
	def join_tm(self,*args,**kwargs):
		if self.__is_tm_init:
			self.tm.join(*args,**kwargs)
	
	def get_page(self,url,encoding,query=None,data=None,range=None,tout=None,head=False,referer=None,header=None,tunnel="disabled",forcetunnel=False):
		
		if not self.__is_browser_init: self.__init_browser()
		
		if self.terminate and self.__is_tm_init:
			raise task.killbill

		#python cant handle unicode urlencoding so needs to get dirty below.
		if not query is None:
			query=urlencode (dict ([k, v.encode('utf-8') if isinstance (v, unicode) else v] for k, v in query.items())) 
			url=url+"?"+query
		if not data is None:
			data=urlencode (dict ([k, v.encode('utf-8') if isinstance (v, unicode) else v] for k, v in data.items()))
		#change timeout
		if tout is None:
			tout=int(float(defs.addon.getSetting("tout")))

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
		if not errtype=="killbill" and defs.addon.getSetting("tracetolog")=="true":
			self.backend.log(traceback.format_exc(),defs.loglevel)

	def add_log(self,line):
		line=unidecode(line)
		if hasattr(self,"window") and hasattr(self.window,"status"):
			self.log=line+"\n"+self.log
			self.window.status.setText(self.log)
		if defs.addon.getSetting("logtolog")=="true":
			self.backend.log(line,defs.loglevel)

	def add_mirror(self,parts,name,wait=0,missing="drop"):
		if self.loadable_uprv is None:
			providers.find(self.content_type,"url")
		if not (self.terminate or self.backend.abortRequested()) and isinstance(parts,list) and len(parts)>0:
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
			try:
				caller = inspect.getframeinfo(inspect.stack()[1][0])
				lpname=os.path.split(caller.filename)[-1].split(".")[0].split("_")[2]
			except:
				lpname=None
			self.add_task(target=self._on_new_id, args=(lpname,parts,name,wait,missing),pri=5)
		else:
			return False
		
	def get_keyboard(self,*args,**kwargs):
		return self.backend.get_input(*args,**kwargs)

	def shut(self,play=False,noblock=0):
		self.terminate=True
		prefs.set("cfagents",self.cfagents)
		if self.__is_tm_init:
			self.tm.s.set()
		if hasattr(self,"dialogpg"):
			self.backend.dialogpg.close()
			del(self.backend.dialogpg)
		if self.backend.abortRequested():
			return None
		if hasattr(self,"window"):
			self.window.close()
			if hasattr(self.window,"status"):
				del(self.window.status)
			del(self.window)
		if hasattr(self,"dialog"):
			del(self.backend.dialog)
		try:
			self.cj.save()
		except:
			try:
				os.remove(defs.addon_cookfile)
			except:
				pass
		if play:
			self.player.xplay()
			cnt=0
		else:
			cnt="all"	
		if hasattr(self,"iwindow"):
			self.iwindow.close()
			if hasattr(self.iwindow,"img"):
				del(self.iwindow.img)
			del(self.iwindow)
		if hasattr(self,"player"):
			del(self.player)
		self.join_tm(noblock=noblock,cnt=cnt)

	def __on_new_id(self,lpname,parts,name,wait,missing):
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
					self.add_log("part %s,%s ignored"%(parts[k]["url_provider_name"],parts[k]["url_provider_hash"]))
					ignores.append(k)
		
		for ignore in sorted(ignores,reverse=True):
			parts.pop(ignore)
		
		if not len(parts):
			return None

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
		if self.content_type==defs.CT_VIDEO and defs.addon.getSetting("auto_en_video")=="true":
			if defs.addon.getSetting("video_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"]:
				if unicode(prefix_q[3:-2]).isnumeric() and int(prefix_q[3:-2])>=int(float(defs.addon.getSetting("min_vid_res"))):
					autoplay=True
			if defs.addon.getSetting("video_val_method")=="Check if Alive Only" or defs.addon.getSetting("video_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"] and autoplay:
				tags=re.findall("\[(.*?)\]",name)
				required=defs.addon.getSetting("require_tag").split(",")
				filtered=defs.addon.getSetting("dont_require_tag").split(",")
				autoplay=True
				for tag in tags:
					if not tag=="" and tag.lower().replace(" ","") in [x.lower().replace(" ","") for x in filtered]:
						autoplay=False
						break
				
				for require in required:
					if not require=="" and not require.lower().replace(" ","") in [x.lower().replace(" ","") for x in tags]:
						autoplay=False
						break
				
		if self.content_type==defs.CT_AUDIO and defs.addon.getSetting("auto_en_audio")=="true" and defs.addon.getSetting("audio_val_method")=="Check if Alive Only":
			autoplay=True

		if self.content_type==defs.CT_IMAGE and defs.addon.getSetting("auto_en_image")=="true" and defs.addon.getSetting("audio_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"]:
			autoplay=True

		item=xbmcgui.ListItem()
		item.setLabel(mname)
		item.setLabel2(self.info["title"])
		item.setProperty("parts",json.dumps(parts))
		item.setProperty("lpname",lpname)
		upname=parts[0].get("url_provider_name",None)
		art={}
		if not upname is None:
			art["icon"]=defs.arturi+parts[0]["url_provider_name"]+".png"
			item.setIconImage(defs.arturi+parts[0]["url_provider_name"]+".png")
		if not lpname is None:
			#art["thumb"]=defs.arturi+lpname+".png"
			item.setProperty("lpimg",defs.arturi+lpname+".png")
		item.setArt(art)
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
		if False and self.content_type==defs.CT_VIDEO and defs.addon.getSetting("video_val_method") in ["Check if Alive & Quality","Check if Alive + Quality"] and len(parts)==1:
			from ump import globaldb
			tags=re.findall("\[(.*?)\]",mname)
			hs=fs=d=""
			for tag in tags:
				if tag.startswith("HS:"): hs=tag.split("HS:")[1]
				if tag.startswith("FS:"): fs=tag.split("FS:")[1]
				if tag.startswith("D:"): d=tag.split("D:")[1]
			globaldb.sync(self,parts[0]["url_provider_name"],parts[0]["url_provider_hash"],parts[0]["urls"][max_k]["url"],humanres(max_w,max_h),max_w,max_h,hs,fs,d,float(max_s)/1000000)

	def __validateparts(self,parts,wait):
		def wrap(i):
			parts[i]=self._validatepart(parts[i])
		gid=time.time()
		for k in range(len(parts)):
			self.add_task(wrap,(k,),gid=gid,pri=5)
			time.sleep(wait)
		self.join_tm(gid)

	def __validatepart(self,part):
		metaf=getattr(meta,self.content_type)
		timeout=self.urlval_tout
		provider=providers.load(self.content_type,"url",part["url_provider_name"])
		if hasattr(provider,"timeout") and isinstance(provider.timeout,int):
			timeout=provider.timeout
		#if urls require validation and url is not validated or timed out
		if not "uptime" in part.keys() or time.time()-part["uptime"]>timeout:

			try:
				self.add_log("retrieving url from %s:%s"%(part["url_provider_name"],part["url_provider_hash"]))
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
				if not isinstance(key,str):
					try:
						part["urls"][str(key)]=part["urls"].pop(key)
						key=str(key)
					except:
						self.add_log("unsupport url key type '%s' in url provider %s"%(type(key),part["url_provider_name"]))
						part["urls"].pop(key)
						continue
				try:
					u=part["urls"][key]
					#overide the referer from url provider when it sends dict mirrors
					if not isinstance(u,dict):
						part["urls"][key]={}
						part["urls"][key]["referer"]=part.get("referer","")
						part["urls"][key]["url"]=u
					method=defs.addon.getSetting(self.content_type+"_val_method")
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
					self.add_log("validation failed: key removed : %s, %s"%(key,part["url_provider_name"]))
			part["uptime"]=time.time()
			k,w,h,s=self.max_meta([part])
			part["defmir"]=k
		return part
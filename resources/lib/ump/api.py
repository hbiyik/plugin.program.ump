import os
import json
import urllib
import urllib2
import inspect
import traceback
import sys
import urlparse
import re
import time
import datetime
from cookielib import LWPCookieJar
from socket import timeout
from socket import getdefaulttimeout
from threading import current_thread
from StringIO import StringIO
import gzip
import string

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from unidecode import unidecode

from ump import defs
from ump import task
from ump import providers
from ump import ui
from third.unescape import unescape
from quality import meta
addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

class HeadRequest(urllib2.Request):
	def get_method(self):
		return "HEAD"

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
		self.defs=defs
		self.window = ui.listwindow('DialogSelect.xml', os.getcwd(), 'LCARS', 'PAL',ump=self)
		self.iwindow = ui.imagewindow('picture.xml', addon_dir,"Default","720p")
		self.urlval_en=True
		self.urlval_tout=60
		self.urlval_d_size={self.defs.CT_VIDEO:1000000,self.defs.CT_AUDIO:10000,self.defs.CT_IMAGE:200}
		self.urlval_d_tout=1.5
		self.tm_conc=4
		self.player=None
		self.mirrors=[]
		self.terminate=False
		self.tm=task.manager(self.tm_conc)
		self.loaded_uprv={}
		self.checked_uids={"video":{},"audio":{},"image":{}}
		self.pt=pt
		self.cj=LWPCookieJar(os.path.join( addon_dir, 'resources', 'data', "cookie"))
		if os.path.exists(os.path.join( addon_dir, 'resources', 'data', "cookie")):
			self.cj.load()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.ua="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"
		self.opener.addheaders = [('User-agent', self.ua)]
		self.dialog=xbmcgui.Dialog()
		self.handle = int(sys.argv[1])
		query=sys.argv[2][1:]
		result=urlparse.parse_qs(query)
		[self.module]= result.get('module', ["ump"])
		[self.page]= result.get('page', ["root"])
		[args]= result.get('args', ["{}"])
		self.args=json.loads(args)
		for keep in ["info","art"]:
			[lst]=result.get(keep, ["{}"])
			setattr(self,keep,json.loads(lst))
		[self.content_type]= result.get('content_type', ["index"])
		[self.content_cat]= result.get('content_cat', ["N/A"])
		self.loadable_uprv=providers.find(self.content_type,"url")


	def set_content(self,content_cat="N/A"):
		if content_cat=="N/A":
			content_cat=self.content_cat
		else:
			self.content_cat=content_cat
		xbmcplugin.setContent(self.handle, content_cat)

	def is_same(self,name1,name2,strict=False):
		predicate = lambda x:x not in string.punctuation+" "
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
		return sys.argv[0] + '?' + urllib.urlencode(query)

	def get_page(self,url,encoding,query=None,data=None,range=None,tout=None,head=False,referer=None):
		if self.terminate:
			raise task.killbill
		oldheaders=[]
		#python cant handle unicode urlencoding so needs to get dirty below.
		if not query is None:
			query=urllib.urlencode (dict ([k, v.encode('utf-8') if isinstance (v, unicode) else v] for k, v in query.items())) 
			url=url+"?"+query
		if not data is None:
			data=urllib.urlencode (dict ([k, v.encode('utf-8') if isinstance (v, unicode) else v] for k, v in data.items()))
		#change timeout
		if tout is None:
			tout=getdefaulttimeout()

		if head==True:
			req=HeadRequest(url)
		else:
			headers={'Accept-encoding':'gzip'}
			if not range is None : headers["Range"]="bytes=%d-%d"%(range)
			if not referer is None : headers["Referer"]=referer
			req=urllib2.Request(url,headers=headers)

		response = self.opener.open(req, data,timeout=tout)

		if head :
			return response
		
		if response.info().get('Content-Encoding') == 'gzip':
			buf = StringIO(response.read())
			f = gzip.GzipFile(fileobj=buf)
			stream = f.read()
		else:
			stream=response.read()

		if encoding is None:
			#binary data
			src=stream
		else:
			#unicode data
			src=unicode(unescape(stream.decode(encoding,"ignore")))
		return src
	
	def notify_error(self,e):
		frm = inspect.trace()[-1]
		mod = inspect.getmodule(frm[0])
		modname = mod.__name__ if mod else frm[1]
		errtype= e.__class__.__name__
		self.dialog.notification("ERROR","%s : %s"%(modname, errtype))
		print traceback.format_exc()

	def add_log(self,line):
		line=unidecode(line)
		if hasattr(self,"window") and hasattr(self.window,"status"):
			self.window.status.setText(line+"\n"+self.window.status.getText())
		print line

	def add_mirror(self,parts,name):
		if not self.terminate:
			for part in parts:
				upname=part.get("url_provider_name",None)
				uphash=part.get("url_provider_hash",None)
				#sanity check
				if upname is None or uphash is None:
					return False
				#check if there is an appropriate url provider
				if not providers.is_loadable(self.content_type,"url",upname,self.loadable_uprv):
					self.add_log("%s , %s does not have an appropriate url provider. Skipping..." % (str(self.content_type),str(upname)))
					return False
				#check if provider first time. checked ids are dynamic on provider name
				elif upname in self.checked_uids[self.content_type].keys():
				#check if already proccesed
					if uphash in self.checked_uids[self.content_type][upname]:
						self.add_log("%s , %s, %s has already been processed. Skipping..." % (str(self.content_type),str(upname),str(uphash)))
						return False
				else:
				#if first time, create list dynamically
					self.checked_uids[self.content_type][upname]=[]
				self.checked_uids[self.content_type][upname].append(uphash)
			self.tm.add_queue(target=self._on_new_id, args=(parts,name),pri=5)
		else:
			return False
		
	def _on_new_id(self,parts,name):
		##validate media providers url first before adding
		self._validateparts(parts)
		for part in parts:
			if part["urls"]=={}:
				#if even 1 part is missing drop the mirror!!
				self.add_log("%s has missing parts ignoring."%str(parts))
				return False
		#if payer is not yet ready init it.
		if self.player is None:
			self.player=ui.xplayer(ump=self)

		#get the highest quality info from each part and mirror
		q=0
		prefix=""
		for part in parts:
			for mirror in part["urls"].itervalues():
				if self.content_type == self.defs.CT_VIDEO:
					if not mirror["meta"] == {}:
						t=mirror["meta"]["type"]
						w=int(mirror["meta"]["width"])
						h=int(mirror["meta"]["height"])
						s=int(mirror["meta"]["size"])
						if w*h>=q:
							prefix="[%s]"%humanres(w,h)
							q=w*h
							if s>0:
								prefix="%s[F:%s]"%(prefix,humanint(s))
		item=xbmcgui.ListItem()
		item.setLabel(prefix+name)
		item.setLabel2(self.info["title"])
		item.setProperty("parts",json.dumps(parts))
		upname=parts[0].get("url_provider_name",None)
		if not upname is None:
			item.setIconImage(os.path.join( addon_dir, 'resources', 'images', parts[0]["url_provider_name"]+".png" ))
		#if there is no more mirrors and media does not require a provider directly play it.
		q,a,p=self.tm.stats(1)
		if q==0 and a==1 and upname is None:
			state=self.player.create_list(item)
			if state:
				self.player.play()
		else:
		#else init selector ui and add item
			self.window.addListItem(item)

	def _validateparts(self,parts):
		gid=self.tm.create_gid()
		def wrap(i):
			parts[i]=self._validatepart(parts[i])

		for k in range(len(parts)):
			self.tm.add_queue(wrap,(k,),gid=gid,pri=5)
		self.tm.join(gid)

	def _validatepart(self,part):
		metaf=getattr(meta,self.content_type)
		#if urls require validation and url is not validated or timed out
		if not "uptime" in part.keys() or time.time()-part["uptime"]>self.urlval_tout:
			provider=providers.load(self.content_type,"url",part["url_provider_name"])
			try:
				self.add_log("validating %s:%s"%(part["url_provider_name"],part["url_provider_hash"]))
				part["urls"]=provider.run(part["url_provider_hash"],self)
			except (timeout,urllib2.URLError,urllib2.HTTPError),e:
				self.add_log("%s dismissed : Timeout" % part["url_provider_name"])
				part["urls"]={}
			except Exception,e:
				self.notify_error(e)
				part["urls"]={}
			#validate url by downloading header (and check quality)
			for key in part["urls"].keys():
				try:
					u=part["urls"][key]
					part["urls"][key]={}
					part["urls"][key]["url"]=u
					m=metaf("",self.get_page,u)
					part["urls"][key]["meta"]=m
				except (timeout,urllib2.URLError,urllib2.HTTPError),e:
					part["urls"].pop(key)
					self.add_log("%s dismissed : Network Error" % part["url_provider_name"])
				except Exception,e:
					self.notify_error(e)
					part["urls"].pop(key)
					self.add_log("%s key in %s removed"%(key,part["url_provider_name"]))
			part["uptime"]=time.time()
		return part

	def shut(self,play=False):
		self.cj.save()
		self.terminate=True
		if hasattr(self,"window"):
			self.window.close()
		self.tm.s.set()
		self.tm.join()
		if play:
			self.player.play()
		if hasattr(self,"window"):
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

		if hasattr(self,"player"):
			del(self.player)
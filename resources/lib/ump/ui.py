import xbmcgui
import xbmc
import json
from ump import providers
import time
import threading
import urlparse
import urllib
import time
import xbmcaddon

addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

class xplayer(xbmc.Player):
	def __init__(self,ump=None,*args,**kwargs):
		self.ump=ump
		if not self.ump.content_type==self.ump.defs.CT_IMAGE:
			self.playlist=xbmc.PlayList(self.ump.content_type==self.ump.defs.CT_VIDEO)
		else:
			self.playlist=[]
	
	def selectmirror(self,part):
		#in case its multiparted and it has timed out
		part=self.ump._validatepart(part)
		if len(part["urls"].keys())>1:
			slc=self.ump.dialog.select("Select Quality", part["urls"].keys())
		elif len(part["urls"].keys())==1:
			slc=0
		else:
			return "#"
		k=part["urls"].keys()[slc]
		url=part["urls"][k]["url"]
		urlp=urlparse.urlparse(url)
		urlenc={"Cookie":"","User-Agent":self.ump.ua,"Referer":part["urls"][k]["referer"]}
		cook=""
		for cookie in self.ump.cj:
			if urlp.netloc in cookie.domain or cookie.domain in urlp.netloc:
				cook+=cookie.name+"="+cookie.value+";"
		urlenc["Cookie"]=cook
		return url+"|"+urllib.urlencode(urlenc),k
	
	def create_list(self,it):
		if not self.ump.content_type==self.ump.defs.CT_IMAGE:
			self.playlist.clear()
		else:
			self.playlist=[]
		parts=json.loads(it.getProperty("parts"))
		for i in range(len(parts)):
			listitem = xbmcgui.ListItem()
			for key in ["uptime","urls","url_provider_hash","url_provider_name"]:
				if key in parts[i].keys():
					listitem.setProperty(key,json.dumps(parts[i][key]))
			listitem.setInfo(self.ump.content_type,self.ump.info)
			listitem.setArt(self.ump.art)
			if "partname" in parts[i].keys():
				listitem.setLabel(parts[i]["partname"])
			else:
				listitem.setLabel(self.ump.info["title"])
			url,k=self.selectmirror(parts[i])
			if url:
				if not self.ump.content_type==self.ump.defs.CT_IMAGE:
					self.playlist.add(url,listitem)
				else:
					self.playlist.append((url,parts[i]["urls"][k]["meta"]["width"],parts[i]["urls"][k]["meta"]["height"]))
			else:
				#not sure even this is possible :) gotta clean this sometime
				self.ump.add_log("Part Vanished!!!")
		return True
		
	def play(self):
		if not self.ump.content_type==self.ump.defs.CT_IMAGE:
			xbmc.Player(xbmc.PLAYER_CORE_MPLAYER).play(self.playlist)
		else:
			self.ump.iwindow.playlist=self.playlist
			self.ump.iwindow.doModal()
	
	def decode_hash(self,part):
		if not part["url"]=="#":
			return part["url"]
		else:
			name=part["url_provider_name"]
			hash=part["url_provider_hash"]
			provider=providers.load(self.ump.content_type,"url",name)
			link=provider.run(hash,self.ump)
			return link

class imagewindow(xbmcgui.WindowXMLDialog):
	def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback="720p"):
		self.zt=0 #zoome type 0 fited 1 zoomed
		self.cur=0
		self.playlist=None

	def onInit(self):
		self.img=self.getControl(666)
		res=[(1920,1080),(1280,720),(720,480),(720,480),(720,480),(720,480),(720,576),(720,576),(720,480),(720,480)]
		self.ww,self.wh=(1280,720)
		self.setimage(0)

	def setimage(self,cur):
		self.cur=cur%len(self.playlist)
		u,w,h=self.playlist[self.cur][0],self.playlist[self.cur][1],self.playlist[self.cur][2]
		self.w=w
		self.h=h
		self.img.setImage(u)
		self.fitmode()

	def fitmode(self,type=0):
		self.zt=type
		if self.h>self.w:
			mode=(type+1)%2
		else:
			mode=type%2
		if mode==0:
			self.img.setWidth(self.ww)
			self.img.setHeight(self.h*self.ww/self.w)
		if mode==1:
			self.img.setWidth(self.w*self.wh/self.h)
			self.img.setHeight(self.wh)

		x,y=self.img.getPosition()
		
		x1=self.ww-self.img.getWidth()
		if x1>0:
			x1=x1/2
		else:
			x1=0

		y1=self.wh-self.img.getHeight()
		if y1>0:
			y1=y1/2
		else:
			y1=0

		self.img.setPosition(x1,y1)
	
	def onAction(self, action):
		x,y=self.img.getPosition()
		#2 right 
		if action.getId() == 2:
			self.setimage(self.cur+1)
		#1 left
		if action.getId() == 1 :
			self.setimage(self.cur-1)
		#4 down 
		if action.getId() == 4:
			refy=-self.img.getHeight()+self.wh
			refx=-self.img.getWidth()+self.ww
			self.img.setPosition(x-(x-refx)/10,y-(y-refy)/10)
		#3 up
		if action.getId() == 3 :
			ref=0
			self.img.setPosition(x-(x-ref)/10,y-(y-ref)/10)

		#5 item select
		if action.getId() == 7 :
			self.fitmode(self.zt+1)

		if action.getId() in [10,92] :
			self.close()
	
	def onClick(self, controlID):
		pass

	def onFocus(self, controlID):
		pass
	
class listwindow(xbmcgui.WindowXMLDialog):
	def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback,ump=None):
		self.ump=ump
		self.isinit=False

	def onInit(self):
		q,a,p=self.ump.tm.stats()
		self.p=p
		self.progress=self.getControl(2)
		self.lst=self.getControl(6)
		self.button= self.getControl(5)
		self.button.setLabel("Cancel")
		self.button.setEnabled(True)
		self.button.setVisible(True)
		self.button.controlUp(self.lst)
		self.button.controlDown(self.lst)
		self.setFocus(self.button)
		statush=100
		margin=3
		#self.lst.setHeight(self.lst.getHeight()-statush)
		#lstw=self.lst.getWidth()
		#lsth=self.lst.getHeight()
		#lstx,lsty=self.lst.getPosition()
		#self.status=xbmcgui.ControlTextBox(lstx+margin, lsty+lsth, lstw, statush-margin, textColor='0xCCCCCCCC')
		self.status=self.getControl(8)
		if not self.ump.art["fanart"]=="":
			self.getControl(3).setImage(self.ump.art["fanart"])
			self.getControl(3).setColorDiffuse('0xFF333333')
		#self.status.setEnabled(True)
		#self.status.setVisible(True)
	def _update(self):
		q,a,p=self.ump.tm.stats()
		if not q+a+p-self.p == 0:
			self.progress.setPercent(float(p-self.p)*100/float(q+a+p-self.p))

	def onAction(self, action):
		self._update()
		if action.getId() in [1,2,3,4,107] :
			#user input
			if threading.active_count()==2:
				self.button.setLabel("Close")
		if action.getId() in [10,92] :
			self.ump.shut()

	def onClick(self, controlID):
		self._update()
		if controlID==5:
			self.ump.shut()
		else:
			try:
				it=self.lst.getSelectedItem()
				state=self.ump.player.create_list(it)
				if state:
					self.ump.shut(True)
			except Exception,e:
				self.ump.notify_error(e)

	def onFocus(self, controlID):
		self._update()
	
	def addListItem(self,listItem):
		self._update()
		self.lst.addItem(listItem)
		if self.lst.size()==1: 
			self.setFocus(self.lst)
		else:
			focusid=self.getFocusId()
			sid=self.lst.getSelectedPosition()
			if focusid==6:
				self.lst.selectItem(sid)
			else:
				self.setFocusId(focusid)
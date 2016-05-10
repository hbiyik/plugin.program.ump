import xbmc
import xbmcgui
import xbmcplugin
import sys
import os
import json
from ump import defs
from ump import prefs

class Mon(xbmc.Monitor):
	def __init__(self):
		self.ar=False

	def onAbortRequested(self):
		self.ar = True

	def abortRequested(self):
		return self.ar

def execute(*args,**kwargs):
	pass

def sleep(*args,**kwargs):
	pass

def log(*args,**args):
	pass

class interface():
	def __init__(self):
		self.m=xbmc.Monitor()
		self.handle = int(sys.argv[1])	
		if not hasattr(self.m,"abortRequested"):
			self.m=Mon()
		self.dialog=xbmcgui.Dialog()
		self.dialogbg=xbmcgui.DialogProgressBG()
		self.dialogbg.create("UMP")
		
	def abortRequested(self):
		return self.m.abortRequested()	 
	
	def get_input(self,*args):
		kb = xbmc.Keyboard(*args)
		kb.setDefault("")
		kb.setHiddenInput(False)
		if not self.abortRequested():
			kb.doModal()
		if self.abortRequested():
			self.dialogpg.close()
			sys.exit()
		return kb.isConfirmed(),kb.getText()

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


	def add_index_item(self,name,u,page=None,args={},module=None,thumb="DefaultFolder.png",icon="DefaultFolder.png",info={},art={},cmds=[],adddefault=True,removeold=True,isFolder=True):
		##huge assumption here
		if page=="urlselect":isFolder=False
		li=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=thumb)
		li.setArt(art)
		li.setInfo(defs.LI_CTS[self.content_type],info)
		coms=[]
		if adddefault:
			coms.append(('Detailed Info',"Action(Info)"))
			coms.append(('Bookmark',"RunScript(%s,addfav,%s,%s,%s,%s,%s)"%(os.path.join(defs.addon_dir,"lib","ump","script.py"),str(isFolder),self.content_type,json.dumps(name),thumb,u)))
		coms.extend(cmds)
		if adddefault:
			coms.append(("Addon Settings","Addon.OpenSettings(plugin.program.ump)"))
		li.addContextMenuItems(coms,removeold)
		self.index_items.append((u,li,isFolder,adddefault,coms,removeold))
		return li

	def end_index_items(self,index_items,content_type,content_cat="ump",enddir=True):
		xbmcplugin.setContent(self.handle, content_cat)
		items=[]
		if len(index_items):
			for u,li,isfolder,adddef,coms,remold in index_items:
				items.append((u,li,isfolder))
				if adddef:
					coms.append(('Set current view \"default\" for %s'%content_cat,"RunScript(%s,setview,%s,%s)"%(os.path.join(defs.addon_dir,"lib","ump","script.py"),content_type,content_cat)))
					li.addContextMenuItems(coms,remold)
			xbmcplugin.addDirectoryItems(self.handle,items,len(items))
		if enddir:xbmcplugin.endOfDirectory(self.handle,cacheToDisc=False,updateListing=False,succeeded=True)
		wmode=defs.addon.getSetting("view_"+content_cat).lower()
		if wmode=="":wmode="default"
		if not wmode == "default":
			mode=defs.VIEW_MODES[wmode].get(xbmc.getSkinDir(),None)
		else:
			mode=prefs.get("pref_views",content_cat,xbmc.getSkinDir())
			if mode=={}: mode=None
		if content_type==defs.CT_AUDIO and content_cat in [defs.CC_MOVIES,defs.CC_SONGS,defs.CC_ARTISTS,defs.CC_ALBUMS]:
			#issue #38
			self.add_log("UMP issue #38 %s skippied view: %s"%(content_cat,wmode))
		elif not mode is None:
			for i in range(0, 10*60):
				if self.terminate or self.backend.abortRequested():
					break
				if xbmc.getCondVisibility('Container.Content(%s)' % content_cat):
					xbmc.executebuiltin('Container.SetViewMode(%d)' % mode)
					break
				xbmc.sleep(100)

	def log (self,*args,**kwargs):
		xbmc.log(*args,**kwargs)

	def get_setting(self,*args,**kwargs):
		pass

	def set_setting(self,*args,**kwargs):
		pass

	def add_media_item(self,*args,**kwargs):
		pass

	def abort_requested(self,*args,**kwargs):
		pass

	def shut(self,*args,**kwargs):
		pass
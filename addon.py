import sys
import os
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import threading
import time
import gc

addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )
sys.path.append(os.path.join( addon_dir, 'resources', 'lib' ) )

from ump import providers
from ump import api
from ump import ui

ump=api.ump()

print "HANDLE       : " + str(ump.handle)
print "MODULE       : " + str(ump.module)
print "PAGE         : " + str(ump.page)
#print "ARGS         : " + str(ump.args)
print "CONTENT_TYPE : " + str(ump.content_type)
#print "INFO         : " + str(ump.info)
#print "ART          : " + str(ump.art)


indexers=providers.find(ump.content_type,"index")
url_providers=providers.find(ump.content_type,"url")
link_providers=providers.find(ump.content_type,"link")

if False:
	iwin=ui.imagewindow('picture.xml', addon_dir,"Default","720p",playlist=[])

if ump.module == "ump":
	if ump.page is "root":
		for provider in indexers:
			provider_cat,provider_type,provider_name=provider
			li=xbmcgui.ListItem(provider_name, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to(module=provider_name),li,True)
		xbmcplugin.endOfDirectory(ump.handle)
elif ump.page== "urlselect":
#	threads=[]
	if len(link_providers)==0:
		ump.dialog.notification("ERROR","There is no available providers for %s"%ump.content_type)
	else:
		gid=ump.tm.create_gid()
		for provider in link_providers:
			provider=providers.load(ump.content_type,"link",provider[2])
			ump.tm.add_queue(provider.run, (ump,),gid=gid)
		ump.window.doModal()
		ump.tm.join(gid)
elif providers.is_loadable(ump.content_type,"index",ump.module,indexers):
	providers.load(ump.content_type,"index",ump.module).run(ump)
ump.tm.join()
ump.tm.stop()
ump.shut()
print "CONTENT_CAT  : " + str(ump.content_cat)
del gc.garbage[:]
gc.collect()
while not len(threading.enumerate())==1:
	print threading.enumerate()
print "EOF"

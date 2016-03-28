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
sys.path.append(os.path.join(addon_dir,"lib"))

from ump import providers
from ump import api
from ump import ui


#bookmark.resolve()
ump=api.ump()

print "HANDLE       : " + str(ump.handle)
print "MODULE       : " + str(ump.module)
print "PAGE         : " + str(ump.page)
#print "ARGS         : " + str(ump.args)
print "CONTENT_TYPE : " + str(ump.content_type)
#print "INFO         : " + str(ump.info)
#print "ART          : " + str(ump.art)

indexers=providers.find(ump.content_type,"index")
url_providers=providers.find(ump.content_type,"url",False)
link_providers=providers.find(ump.content_type,"link",False)

if ump.module == "ump":
	if ump.page == "root":
		for provider in indexers:
			provider_cat,provider_type,provider_name=provider
			img="http://boogie.us.to/dataserver/ump/images/"+provider_name+".png"
			li=xbmcgui.ListItem(provider_name.title(), iconImage=img, thumbnailImage=img)
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to(module=provider_name),li,True)
		ump.set_content(ump.defs.CC_ALBUMS)
elif ump.page== "urlselect":
#	threads=[]
	if len(link_providers)==0:
		ump.dialog.notification("ERROR","There is no available providers for %s"%ump.content_type)
	else:
		for provider in link_providers:
			try:
				provider=providers.load(ump.content_type,"link",provider[2])
			except Exception, e:
				ump.notify_error(e)
				continue
			ump.tm.add_queue(provider.run, (ump,),pri=10)
		ump.window.doModal()
elif providers.is_loadable(ump.content_type,"index",ump.module,indexers)==1:
	providers.load(ump.content_type,"index",ump.module).run(ump)
elif providers.is_loadable(ump.content_type,"index",ump.module,indexers)==2:
	providers.load("ump","index",ump.module).run(ump)
ump.shut()
print "CONTENT_CAT  : " + str(ump.content_cat)
del gc.garbage[:]
gc.collect()
print "EOF"

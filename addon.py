import sys
import gc
import os

import xbmcgui
import xbmcplugin

from defs import addon
from defs import addon_ldir
from defs import arturi
from defs import CC_ALBUM
sys.path.append(addon_ldir)
from ump import api
from ump import prerun
from ump import postrun
from ump import providers
from ump import ui

#bookmark.resolve()
ump=api.ump()
prerun.run(ump)

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

if ump.module == "ump":
	if ump.page == "root":
		for provider in indexers:
			provider_cat,provider_type,provider_name=provider
			img=arturi+provider_name+".png"
			li=xbmcgui.ListItem(provider_name.title(), iconImage=img, thumbnailImage=img)
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to(module=provider_name),li,True)
		ump.set_content(CC_ALBUMS)
elif ump.page== "urlselect":
	if not addon.getSetting("tn_chk_url_en").lower()=="false":
		from ump import webtunnel
		webtunnel.check_health(ump,True)
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
	try:
		providers.load(ump.content_type,"index",ump.module).run(ump)
	except Exception,e:
		ump.notify_error(e)
		
elif providers.is_loadable(ump.content_type,"index",ump.module,indexers)==2:
	try:
		providers.load("ump","index",ump.module).run(ump)
	except Exception,e:
		ump.notify_error(e)

postrun.run(ump)		
ump.shut()
print "CONTENT_CAT  : " + str(ump.content_cat)
del gc.garbage[:]
gc.collect()
print "EOF"

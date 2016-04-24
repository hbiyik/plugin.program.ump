import sys
import gc
import os

import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

addon = xbmcaddon.Addon('plugin.program.ump')
addon_ldir = xbmc.translatePath( os.path.join(addon.getAddonInfo('path'),"lib") )
sys.path.append(addon_ldir)
from ump import prerun
prerun.direct()
from ump.defs import addon_ldir
from ump.defs import arturi
from ump.defs import CC_ALBUMS

from ump import api
from ump import postrun
from ump import providers
from ump import ui
#bookmark.resolve()
ump=api.ump()
prerun.run(ump)

ump.add_log("HANDLE       : %s"%str(ump.handle))
ump.add_log("MODULE       : %s"%str(ump.module))
ump.add_log("PAGE         : %s"%str(ump.page))
#print "ARGS         : " + str(ump.args)
ump.add_log("CONTENT_TYPE : %s"%str(ump.content_type))
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
			if ump.content_type == "ump":
				content_type=provider_cat
			else:
				content_type=ump.content_type
			xbmcplugin.addDirectoryItem(ump.handle,ump.link_to(content_type=content_type,module=provider_name),li,True)
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
ump.add_log("CONTENT_CAT  : %s"%str(ump.content_cat))
del gc.garbage[:]
gc.collect()
ump.add_log("UMP:EOF")

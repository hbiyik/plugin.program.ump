from ump import bookmark
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc
import os
import json

addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

def run(ump):
	res,favs=bookmark.load()
	ccat=ump.content_type
	for fav in favs:
		wid,name,thumb,data,cat,module,page,args,info,art=fav
		if cat==ccat or ccat=="ump":
			ump.content_type=cat
			ump.info=info
			ump.art=art
			u=ump.link_to(page,args,module)
			li=xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
			li.setArt(art)
			li.setInfo(cat,info)
			commands=[
			('Detailed Info', 'Action(Info)'),
			('Rename Bookmark',"RunScript(%s,renfav,%s,%s,%s)"%(os.path.join(addon_dir,"lib","ump","script.py"),json.dumps(name),json.dumps(thumb),json.dumps(data))),
			('Remove From Bookmarks',"RunScript(%s,delfav,%s,%s,%s)"%(os.path.join(addon_dir,"lib","ump","script.py"),json.dumps(name),json.dumps(thumb),json.dumps(data))),
			("Addon Settings","Addon.OpenSettings(plugin.program.ump)")
			]
			li.addContextMenuItems(commands,True)
			xbmcplugin.addDirectoryItem(ump.handle,u,li,not wid is None)
	ump.set_content(ump.defs.CC_ALBUMS)
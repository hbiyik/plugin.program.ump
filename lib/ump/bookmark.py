import sys
import zlib
import xbmc
import xbmcgui
import os
import re
from xml.dom import minidom
import urlparse
import json
import urllib
try:
	from ump.defs import WID
except:
	from defs import WID

def resolve():
	if sys.argv[2].startswith("?hash="):
		sys.argv[2]=zlib.decompress(sys.argv[2][6:].decode("hex"))

def create(url=None):
	if not url is None:
		return sys.argv[0]+"?hash="+zlib.compress(url).encode("hex")
	elif not sys.argv[2].startswith("?hash="):
		return sys.argv[0]+"?hash="+zlib.compress(sys.argv[2]).encode("hex")
	else:
		return sys.argv[0]+sys.argv[2]


def decode(uri):
	uri=urlparse.urlparse(uri)
	result=urlparse.parse_qs(uri.query)
	[content_cat]=result.get('content_type', ["ump"])
	[module]= result.get('module', ["ump"])
	[page]= result.get('page', ["root"])
	[args]= result.get('args', ["{}"])
	args=json.loads(args.encode("utf-8"))
	[info]=result.get("info", ["{}"])
	info=json.loads(info.encode("utf-8"))
	[art]=result.get("art", ["{}"])
	art=json.loads(art.encode("utf-8"))
	return uri.path,content_cat.encode("utf-8"),module.encode("utf-8"),page.encode("utf-8"),args,info,art

def load():
	favs=[]
	favsxml=xbmc.translatePath('special://home/userdata/favourites.xml')
	if os.path.exists(favsxml):
		res=minidom.parse(favsxml)
	else:
		return None,favs
	for fav in res.getElementsByTagName("favourite"):
		cmd=None
		data=fav.lastChild.data.replace("&quot;",'"')
		cmd1=re.findall('RunPlugin\((.*?)"\)',data)
		cmd2=re.findall('PlayMedia\((.*?)"\)',data)
		cmd3=re.findall('ActivateWindow\(([0-9]*?)\,(.*?)"\,',data)
		if len(cmd1):
			cmd=cmd1[0]
			wid=None
		if len(cmd2):
			cmd=cmd2[0]
			wid=None
		elif len(cmd3):
			wid,cmd=cmd3[0]
		if not cmd is None:
			path,cat,module,page,args,info,art=decode(cmd)
			if not "plugin.program.ump" in path:
				continue
			name=fav.getAttribute("name").encode("utf-8")
			thumb=fav.getAttribute("thumb").encode("utf-8")
			favs.append((wid,name,thumb,data,cat,module,page,args,info,art))
	return res,favs

def ren(name,thumb,data):
	res,favs=load()
	mfavs=res.getElementsByTagName("favourites")[0]
	dialog = xbmcgui.Dialog()
	for fav in res.getElementsByTagName("favourite"):
		fname=fav.getAttribute("name").encode("utf-8")
		fthumb=fav.getAttribute("thumb").encode("utf-8")
		fdata=fav.lastChild.data.replace("&quot;",'"')
		if name==fname and fthumb==thumb and fdata==data:
			kb = xbmc.Keyboard('default', 'Rename Bookmark', True)
			kb.setDefault(name)
			kb.setHiddenInput(False)
			kb.doModal()
			newname=kb.getText()
			if not newname==name or newname=="":
				fav.setAttribute("name", newname)
				res.writexml( open(xbmc.translatePath('special://home/userdata/favourites.xml'), 'w'),encoding="UTF-8")
				res.unlink()
				xbmc.executebuiltin("Container.Refresh")
				dialog.ok('UMP', '%s has been to %s'%(name,newname))
			break


def rem(name,thumb,data):
	res,favs=load()
	found=False
	mfavs=res.getElementsByTagName("favourites")[0]
	dialog = xbmcgui.Dialog()
	for fav in res.getElementsByTagName("favourite"):
		fname=fav.getAttribute("name").encode("utf-8")
		fthumb=fav.getAttribute("thumb").encode("utf-8")
		fdata=fav.lastChild.data.replace("&quot;",'"')
		if name==fname and fthumb==thumb and fdata==data:
			found=True
			if 	dialog.yesno("UMP", "Are you sure you want to remove?",name):
				mfavs.removeChild(fav)
				dialog.ok('UMP', '%s has been removed from bookmarks'%name)
			break
	if found:
		res.writexml( open(xbmc.translatePath('special://home/userdata/favourites.xml'), 'w'),encoding="UTF-8")
		res.unlink()
		xbmc.executebuiltin("Container.Refresh")
	else:
		dialog.ok('UMP', '%s can not be found in bookmarks!'%name)


def add(isFolder,content_type,name,thumb,uri):
	print uri
	path,cat,module,page,args,info,art=decode(uri)
	favsxml=xbmc.translatePath('special://home/userdata/favourites.xml')
	if os.path.exists(favsxml):
		res=minidom.parse(favsxml)
	else:
		res=minidom.parseString("<favourites></favourites>")
	favs=res.getElementsByTagName("favourites")[0]
	newnode = res.createElement("favourite")
	newnode.setAttribute("name", name)
	newnode.setAttribute("thumb", thumb)
	link="plugin://plugin.program.ump/?%s"%urllib.urlencode({"module":module,"page":page,"args":json.dumps(args),"info":json.dumps(info),"art":json.dumps(art),"content_type":content_type})
	if isFolder:
		str='ActivateWindow(%d,"%s",return)'%(WID[content_type],link)
	else:
		str='RunPlugin("%s")'%link
	print str
	favs.appendChild(newnode)
	newnode.appendChild(res.createTextNode(str))
	res.writexml( open(favsxml, 'w'),encoding="UTF-8")
	res.unlink()
	dialog = xbmcgui.Dialog()
	dialog.ok('UMP', '%s added to bookmarks'%name)

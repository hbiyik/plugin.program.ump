try:
	import xbmc
	import xbmcaddon
	addon = xbmcaddon.Addon('plugin.program.ump')
except:
	pass
import os
from xml.dom import minidom
import json

def get_skin_view(ctype):
	xmls={"video":"MyVideoNav.xml","audio":"MyMusicNav.xml","image":"MyPics.xml"}
	res=minidom.parse(os.path.join(xbmc.translatePath('special://skin/'),"addon.xml"))
	dir=res.getElementsByTagName("res")[0].getAttribute("folder")
	res.unlink()
	navxml=os.path.join(xbmc.translatePath('special://skin/'),dir,xmls[ctype])
	res=minidom.parse(navxml)
	views=res.getElementsByTagName("views")[0].lastChild.data.split(",")
	res.unlink()
	for view in views:
		label=xbmc.getInfoLabel("Control.GetLabel(%s)"%view)
		if not (label == '' or label == None): break
	return xbmc.getSkinDir(),view

def setkeys(d,k,v):
	s="d"
	for key in k:
		s=s+"['%s']"%key
	exec("%s=%s"%(s,v))
	return d

def getkeys(d,k):
	s="d"
	for key in k:
		if key == k[-1]:
			s=s+".get('%s',{})"%key
		else:
			s=s+"['%s']"%key
	return eval(s)

#this function loads a json encoded string and and convert the dict of dics in it to python onjects, ie:data["master"]["sub"]["subofsub"]....
#the purpose is to use dict as a nested xml-like object, if the pointed path does not exists in the dict of dicts
#function creates an empty dict with the correct dict structure. This is used to stored data in settings.xml
#in a hidden string with json encoding. path dicts are only accepted as string!!! dont use numerics and weird types
#that is a restriction in json and the returned value can be anything that json can encode, basically all generic built in types
#ie: int,float,str, None, list, tuple, dicts etc..

def dictate(*args):
	#arg0: json string to decode
	#arg1 to n, path strings.
	try:
		boot=json.loads(args[0])
	except:
		boot={}
	prekeys=[]

	for key in args[1:]:
		print key
		print boot
		currentkey=getkeys(boot,prekeys)
		if not key in currentkey:
			prekeys.append(key)
			setkeys(boot,prekeys,{})
		else:
			prekeys.append(key)
	
	return boot	

def get(*args):
	#arg0: setting name to get
	#arg1 to n, path strings.
	result=dictate(json.loads(addon.getSetting(args[0])),args[1:])
	addon.setSetting(args[0],json.dumps(result))
	return result

def set(*args):
	#arg0: setting name to set
	#arg1 to n-1, path strings.
	#argn, value to set
	result=dictate(json.loads(addon.getSetting(args[0])),args[1:-1])
	setketys(result,args[1:-1],args[-1])
	addon.setSetting(args[0],json.dumps(result))

def set_view(ctype,ccat):
	sid,vid=get_skin_view(ctype)
	set("pref_views",ccat,sid,vid)
	if not addon.getSetting("view_%s"%ccat).lower()=="default":
		addon.setSetting("view_%s"%ccat,"Default")
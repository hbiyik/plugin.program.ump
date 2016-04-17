try:
	import xbmc
	import xbmcaddon
	addon = xbmcaddon.Addon('plugin.program.ump')
except:
	pass
import os
from xml.dom import minidom
import json
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

preffile=os.path.join(xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump'),"prefs.json")

def prefs(mode,data=None):
	with open(preffile, mode) as pref:
		if data is None:
			ret=pref.read()
		else:
			ret=pref.write(data)
	return ret

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

def settingActive(set):
	ret=False
	res=minidom.parse(os.path.join(addon_dir,"resources","settings.xml"))
	for setting in res.getElementsByTagName("setting"):
		if setting.getAttribute("id") == set and not setting.getAttribute("visible").lower()=="false":
			ret=True
			break
	res.unlink()
	return ret

def setSetting(key,val):
	addondir=xbmc.translatePath('special://home/userdata/addon_data/plugin.program.ump')
	setfile=os.path.join(addondir,"settings.xml")
	if not os.path.exists(addondir):
		os.makedirs(addondir)
	if os.path.exists(setfile):
		res=minidom.parse(setfile)
	else:
		res=minidom.parseString("<settings></settings>")
	found=False
	for setting in res.getElementsByTagName("setting"):
		if setting.getAttribute("id")==key:
			setting.setAttribute("value",val)
			found=True
	if not found:
		newnode = res.createElement("setting")
		newnode.setAttribute("id", key)		
		newnode.setAttribute("value", val)
		res.getElementsByTagName("settings")[0].appendChild(newnode)
	res.writexml( open(setfile, 'w'),encoding="UTF-8")
	res.unlink()
	
def set_setting_attr(name,set,val):
	ret=False
	res=minidom.parse(os.path.join(addon_dir,"resources","settings.xml"))
	for setting in res.getElementsByTagName("setting"):
		if setting.getAttribute("id") == name:
			setting.setAttribute(set,val)
			ret=True
			break
	if ret:
		res.writexml( open(os.path.join(addon_dir,"resources","settings.xml"), 'w'),encoding="UTF-8")
	res.unlink()
	return ret

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

def dictate(boot,path):
	#boot: json string to decode
	#path to n, path strings.
	try:
		boot=json.loads(boot)
	except:
		boot={}
	prekeys=[]
	for key in path:
		currentkey=getkeys(boot,prekeys)
		if not key in currentkey:
			prekeys.append(key)
			setkeys(boot,prekeys,{})
		else:
			prekeys.append(key)
	
	return boot	

def get(*args):
	#args: path to prefernce dict key
	result=dictate(prefs("r"),args)
	prefs("wb",json.dumps(result))
	return getkeys(result,args)

def set(*args):
	#args: path to prefernce dict key
	#args(n): set object
	result=dictate(prefs("r"),args[:-1])
	setkeys(result,args[:-1],args[-1])
	prefs("wb",json.dumps(result))

def set_view(ctype,ccat):
	sid,vid=get_skin_view(ctype)
	set("pref_views",ccat,sid,vid)
	if not addon.getSetting("view_%s"%ccat).lower()=="default":
		addon.setSetting("view_%s"%ccat,"Default")
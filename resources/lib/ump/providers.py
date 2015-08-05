import os
import xbmc
import xbmcaddon

addon = xbmcaddon.Addon('plugin.program.ump')
addon_dir = xbmc.translatePath( addon.getAddonInfo('path') )

def find(cat,type):
	if cat is None:
		return [None,None,None]
	lst=[]
	for root, dirs, files in os.walk(os.path.join(addon_dir, 'resources', 'lib' ,'providers')):
		for file in files:
			if file.endswith('.py') and file.startswith(cat+"_"+type+"_"):
				lst.append(file[:-3].split("_"))
#	return  cat,type,name
	return lst

def is_loadable(cat,type,name,providers=None):
	providers=[providers,find(cat,type)][providers is None]
	return [cat,type,name] in providers

def load(cat,type,name):
	fname=cat+"_"+type+"_"+str(name)
	module=__import__("providers",fromlist=[fname])
	return getattr(module,fname)
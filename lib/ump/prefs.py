import xbmc
import xbmcaddon
import os
from xml.dom import minidom
import json

xmls={"video":"MyVideoNav.xml","audio":"MyMusicNav.xml","image":"MyPics.xml"}
addon = xbmcaddon.Addon('plugin.program.ump')
#method ported from exodus
def get_skin_view(ctype):
    res=minidom.parse(os.path.join(xbmc.translatePath('special://skin/'),"addon.xml"))
    dir=res.getElementsByTagName("res")[0].getAttribute("folder")
    res.unlink()
    navxml=os.path.join(xbmc.translatePath('special://skin/'),dir,xmls[ctype])
    res=minidom.parse(navxml)
    views=res.getElementsByTagName("views")[0].lastChild.data.split(",")
    for view in views:
        label=xbmc.getInfoLabel("Control.GetLabel(%s)"%view)
        if not (label == '' or label == None): break
    return xbmc.getSkinDir(),view

def setkeys(d,k,v):
    s="d"
    for key in k:
        s=s+"[%s]"%key
    exec("%s=%s"%(s,v))
    return d

def getkeys(d,k):
    s="d"
    for key in k:
        if key == k[-1]:
            s=s+".get('%s',None)"%key
        else:
            s=s+"[%s]"%key
    print s
    return eval(s)

def dictate(*args):
    try:
        boot=addon.getSetting(args[0])
        boot=json.loads(boot)
    except:
        boot={}
    prekeys=[]

    for key in args[1:]:
        print key
        prekeys.append(key)
        currentkey=getkeys(boot,prekeys)
        if (not currentkey is dict or currentkey is None or (currentkey is dict and not key in currentkey)) and not key==args[-1] :
            setkeys(boot,prekeys,{})

    print boot    
    
    
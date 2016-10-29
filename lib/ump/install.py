import sys
import os
import shutil
import zipfile
import StringIO
import re
import urllib2
from xml.dom import minidom
from distutils.version import LooseVersion

from . import defs
from . import dom
from . import throttle

import xbmcgui
import xbmcvfs
import xbmc

ua="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
skips=["xbmc.python"]
trtl=throttle.throttle(defs.addon_tdir)
def get_page(url,throttle=0):
    tid=trtl.id(url)
    entrtl=not throttle==False and isinstance(throttle,(int,float))
    if entrtl and trtl.check(tid,throttle):
        data=trtl.get(tid)
    else:
        request = urllib2.Request(url,headers={"User-Agent":ua})
        data=urllib2.urlopen(request).read()
        if entrtl:
            trtl.do(tid,data)
    return data

def is_installed(id,version=None,strict=False):
    xml=xbmc.translatePath("special://home/addons/%s/addon.xml"%id)
    if xbmcvfs.exists(xml):
        if not version:
            return bool(xbmcvfs.exists(xml))
        else:
            axml=dom.read(xml)
            aversion=LooseVersion(axml.getElementsByTagName("addon")[0].getAttribute("version"))
            version=LooseVersion(version)
            if strict:return version==aversion
            else:return version<=aversion
    return False

def push_zip(zipball,path=None):
    zip=zipfile.ZipFile(StringIO.StringIO(get_page(zipball,throttle=False)))
    if not path:
        path=xbmc.translatePath("special://home/addons/")
    zip.extractall(path)

def getxml(repo=None,datadir=None):
    if datadir:
        if not datadir.endswith("/"):datadir=datadir+"/"
        return datadir,minidom.parseString(get_page(datadir+"addons.xml"))
    elif repo:
        if is_installed(repo):
            xml=dom.read(xbmc.translatePath("special://home/addons/%s/addon.xml")%repo)
            datadir=xml.getElementsByTagName("datadir")[0].lastChild.data
            return getxml(datadir=datadir)
    
def find_deps(id,xml):
    addons=xml.getElementsByTagName("addon")
    rets={id:[None,False]}
    while True:
        cnt=0
        for id,v in rets.copy().iteritems():
            if v[1]:
                cnt+=1
                continue
            version,imports=find_addon(id,addons)
            rets[id]=[version,True]
            if not version:return
            for imp in imports:
                version,id=imp
                if id in skips:continue
                rets[id]=[version,False]
        if cnt==len(rets):break
    return rets

def install_addon(id,repo="repository.xbmc.org",datadir=None):
    if datadir:datadir,xml=getxml(datadir=datadir)
    else:datadir,xml=getxml(repo)
    installs=find_deps(id,xml)    
    for id,[version,found] in installs.iteritems():
        if found and not is_installed(id, version):
            push_zip("%s%s/%s-%s.zip"%(datadir,id,id,version))
            dialog=xbmcgui.Dialog()
            dialog.notification("Addon Installed",id)
            print "Addon Installed %s"%id
            xbmc.executebuiltin("XBMC.UpdateLocalAddons()")

def find_addon(id,addons):
    imports=[]
    for addon in addons:
        if addon.getAttribute("id")==id:
            for imp in addon.getElementsByTagName("import"):
                imports.append((imp.getAttribute("version"),imp.getAttribute("addon")))
            return addon.getAttribute("version"),imports
    return None,None

def init_paths(id,repo="repository.xbmc.org"):
    datadir,xml=getxml(repo)
    for id,[version,found] in find_deps(id,xml).iteritems():
        if found:
            dirs=[]
            axml=dom.read(xbmc.translatePath("special://home/addons/%s/addon.xml")%id)
            for extension in axml.getElementsByTagName("extension"):
                lib=extension.getAttribute("library")
                if lib and not lib=="":
                    libdir=xbmc.translatePath("special://home/addons/%s/%s"%(id,lib))
                    if not os.path.isdir(libdir):
                        libdir=os.path.dirname(libdir)
                    dirs.append(libdir)
            for dir in dirs:
                if not dir in sys.path:
                    sys.path.append(dir)
                    print "Dir added to path: %s"%dir
                    
def sideload(id,version=None,repo="repository.xbmc.org",datadir=None,strict=False,silent=True):
    dialog=xbmcgui.Dialog()
    if not is_installed(id,version,strict):
        if silent or dialog.yesno("%s is missing"%id, "In order to use this function you need %s to be installed in your KODI/XBMC.Do you want to install it now?"%id):
            install_addon("script.trakt",repo,datadir)
    init_paths(id)

def get_gitcommits(repo,user,branch="master"):
    giturl="https://github.com/%s/%s/commits/%s"%(user,repo,branch)
    page=get_page(giturl,throttle=12)
    return re.findall('data-clipboard-text="(.*?)"',page)
    
def is_libinstalled(repo,user=None,branch="master",latest=False):
    vfile=os.path.join(defs.addon_xldir,repo,"version.asc")
    if not latest:
        exist=os.path.exists(vfile)
        rver=None
        if not exist:
            rver=get_gitcommits(repo,user,branch)[0]
        return exist,rver
    else:
        with open(vfile) as fo:
            lver=fo.read()
        rver=get_gitcommits(repo,user,branch)[0]
        return lver==rver,rver

def install_lib(repo,user,branch="master",latest=False):
    isins,rver=is_libinstalled(repo, user, branch, latest)
    if not isins:
        zipball="https://codeload.github.com/%s/%s/zip/%s"%(user,repo,branch)
        rpath=os.path.join(defs.addon_xldir,repo)
        shutil.rmtree(rpath,True)
        push_zip(zipball,rpath)
        dialog=xbmcgui.Dialog()
        dialog.notification("Library Installed","%s:%s"%(repo,rver[:5]))
        print "Library Installed %s:%s"%(repo,rver[:5])
        with open(os.path.join(rpath,"version.asc"),"w") as fo:
            fo.write(rver)

def find_libpath(repo,branch="master",path=""):
    return os.path.join(defs.addon_xldir,repo,"%s-%s"%(repo,branch),path)

def init_libpaths(repo,branch="master",path=""):
    incpath=find_libpath(repo,branch,path)
    if not incpath in sys.path:
        sys.path.append(incpath)
        print "LibDir added to path: %s"%incpath
            
def sideloadlib(repo,user,branch="master",path="",latest=False,init=True):
    install_lib(repo, user, branch, latest)
    print init
    if init:
        init_libpaths(repo, branch, path)
    else:
        print 55
        return find_libpath(repo, branch, path)
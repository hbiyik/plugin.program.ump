import xbmcvfs
import os
import time
import defs
import identifier
import shutil

def mkdir(*paths):
    paths=list(paths)
    paths.append("")
    path=os.path.join(*paths)
    if not xbmcvfs.exists(path):xbmcvfs.mkdirs(path)
    
def rmdir(path):
    return shutil.rmtree(path)

class stats():
    def __init__(self):
        self.seenids=[] #cache wacthed ids in ram on each run to make it faster
        mkdir(defs.addon_stdir)
        self.identifier=identifier.identifier()
        
    def _checkid(self,id):
        path=os.path.join(defs.addon_stdir,id,"")
        return id in self.seenids or xbmcvfs.exists(path)
        
    def markseen(self,info,mediapointer=None):
        id=self.identifier.createhash(info,mediapointer)
        mkdir(defs.addon_stdir,id)
        f = xbmcvfs.File(os.path.join(defs.addon_stdir,id,"timestamp"),'w')
        f.write(str(time.time()))
        f.close()
        self.seenids.append(id)
        
    def markunseen(self,info,mediapointer=None):
        id=self.identifier.createhash(info,mediapointer)
        path=os.path.join(defs.addon_stdir,id,"")
        if xbmcvfs.exists(path):
            rmdir(path)
        
    def isseen(self,info,mediapointer=None):
        if mediapointer:
            id=self.identifier.createhash(info,mediapointer)
            if self._checkid(id):
                    print "directid: %s, %s"%(mediapointer,id)
                    self.seenids.append(id)
                    return 1
        else:
            mediapointer=self.identifier.getpointer(info)
            for i in range(len(mediapointer)):
                nestedid=self.identifier.createhash(info,mediapointer=mediapointer[:i+1])
                if self._checkid(nestedid):
                    print "nestedid: %s, %s"%(str(mediapointer[:i+1]),nestedid)
                    self.seenids.append(nestedid)
                    return 1
        return 0
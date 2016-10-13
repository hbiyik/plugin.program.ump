import os
import md5
import time
import defs
import identifier

def mkdir(*paths):
    path=os.path.join(*paths)
    if not os.path.exists(path):os.makedirs(path)

class stats():
    def __init__(self):
        self.watchedids=[] #cache wacthed ids in ram on each run to make it faster
        mkdir(defs.addon_stdir)
        self.identifier=identifier.identifier()
        
    def _checkid(self,id):
        return id in self.watchedids or os.path.exists(os.path.join(defs.addon_stdir,id))
        
    def markwatched(self,info):
        id=self.identifier.createmd5(info)
        mkdir(defs.addon_stdir,id)
        f = open(os.path.join(defs.addon_stdir,id,"timestamp"),'w')
        f.write(str(time.time()))
        f.close()
        self.watchedids.append(id)
        
    def iswatched(self,info):
        print 1
        mediatype=info.get("mediatype",defs.MT_OTHER)
        print 2
        if mediatype==defs.MT_OTHER:return 0
        print 3
        mediapointer=defs.mediapointer.get(mediatype,["code"])
        for i in range(len(mediapointer)):
            nestedid=self.identifier.createmd5(info,mediapointer=mediapointer[:i+1])
            if self._checkid(nestedid):
                print "nestedid: %s, %s"%(str(mediapointer[:i+1]),nestedid)
                self.watchedids.append(nestedid)
                return 1
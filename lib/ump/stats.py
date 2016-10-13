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
        
    def iswatched(self,info,mediapointer=None):
        if mediapointer:
            id=self.identifier.createmd5(info,mediapointer)
            if self._checkid(id):
                    print "directid: %s, %s"%(str(mediapointer[:i+1]),id)
                    self.watchedids.append(id)
                    return 1
        else:
            mediapointer=self.identifier.getpointer(info)
            for i in range(len(mediapointer)):
                nestedid=self.identifier.createmd5(info,mediapointer=mediapointer[:i+1])
                if self._checkid(nestedid):
                    print "nestedid: %s, %s"%(str(mediapointer[:i+1]),nestedid)
                    self.watchedids.append(nestedid)
                    return 1